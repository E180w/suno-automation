import os
import time
import uuid
import httpx
from dotenv import load_dotenv
from loguru import logger

class SunoCaptchaRequired(Exception):
    pass

class SunoAuto:
    def __init__(self):
        load_dotenv()
        self.auth_token = os.getenv("SUNO_AUTH_TOKEN")
        self.browser_token = os.getenv("SUNO_BROWSER_TOKEN")
        self.device_id = os.getenv("SUNO_DEVICE_ID")
        self.capsolver_key = os.getenv("CAPSOLVER_API_KEY")
        self.base_url = "https://studio-api.prod.suno.com"
        
        if not self.auth_token:
            logger.warning("SUNO_AUTH_TOKEN not found in environment variables")

    def _get_headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
            "Authorization": f"Bearer {self.auth_token}",
            "browser-token": self.browser_token,
            "device-id": self.device_id,
            "Content-Type": "application/json"
        }

    def _solve_hcaptcha(self):
        """
        Solves hCaptcha using Capsolver API.
        Target Site: https://suno.com
        SiteKey: 512ed79c-939e-473d-9d48-690226c63b46
        """
        if not self.capsolver_key:
             raise SunoCaptchaRequired("CAPSOLVER_API_KEY is missing in environment variables.")
        
        sitekey = "512ed79c-939e-473d-9d48-690226c63b46"
        target_url = "https://suno.com"
        
        logger.info("Обнаружена капча, запуск решения через Capsolver...")
        
        create_task_url = "https://api.capsolver.com/createTask"
        payload = {
            "clientKey": self.capsolver_key,
            "task": {
                "type": "HCaptchaTaskProxyLess",
                "websiteURL": target_url,
                "websiteKey": sitekey
            }
        }
        
        try:
            with httpx.Client(timeout=30) as client:
                # 1. Create Task
                resp = client.post(create_task_url, json=payload)
                resp.raise_for_status()
                task_data = resp.json()
                
                if task_data.get("errorId", 0) != 0:
                     raise Exception(f"Capsolver Error: {task_data.get('errorDescription')}")
                
                task_id = task_data.get("taskId")
                
                # 2. Get Result
                get_result_url = "https://api.capsolver.com/getTaskResult"
                
                for _ in range(60): # Poll for up to 120s
                    time.sleep(2)
                    status_resp = client.post(get_result_url, json={"clientKey": self.capsolver_key, "taskId": task_id})
                    status_data = status_resp.json()
                    
                    status = status_data.get("status")
                    if status == "ready":
                        return status_data.get("solution", {}).get("gRecaptchaResponse")
                    
                    if status == "failed":
                        raise Exception(f"Capsolver Failed: {status_data.get('errorDescription')}")
                
                raise TimeoutError("Capsolver timeout.")
                
        except Exception as e:
            logger.error(f"Error solving captcha: {e}")
            raise

    def generate(self, prompt: str, tags: str = "", make_instrumental: bool = False):
        url = f"{self.base_url}/api/generate/v2-web/"
        headers = self._get_headers()
        
        payload = {
            "token": None,
            "generation_type": "TEXT",
            "title": "",
            "mv": "chirp-auk-turbo",
            "prompt": prompt,
            "tags": tags,
            "make_instrumental": make_instrumental,
            "transaction_uuid": str(uuid.uuid4()),
            "metadata": {
                "web_client_pathname": "/create",
                "is_max_mode": False,
                "create_mode": "custom"
            }
        }
        
        logger.info(f"Sending generation request to {url}")
        
        try:
            with httpx.Client(timeout=30) as client:
                response = client.post(url, headers=headers, json=payload)
                
                # Check JSON for captcha_type regardless of status code 
                # (Suno might return 200 or 403 with captcha requirement)
                data = None
                try:
                    data = response.json()
                except:
                    pass

                if data and isinstance(data, dict) and "captcha_type" in data:
                    token = self._solve_hcaptcha()
                    logger.success("Капча успешно решена, повторяю запрос")
                    
                    # Update headers with token and strictly required generic payload updates
                    headers["x-captcha-token"] = token
                    payload["transaction_uuid"] = str(uuid.uuid4())
                    
                    # Retry logic
                    response = client.post(url, headers=headers, json=payload)
                    response.raise_for_status()
                    return response.json()
                
                # If no captcha or captcha resolved, check regular status
                response.raise_for_status()
                logger.success("Request successful")
                return data if data else response.json()

        except httpx.HTTPError as e:
            logger.error(f"HTTP Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                 logger.error(f"Response content: {e.response.text}")
            raise

    def wait_for_clips(self, clip_ids, timeout_seconds=600):
        ids_str = ",".join(clip_ids)
        url = f"{self.base_url}/api/feed/?ids={ids_str}"
        headers = self._get_headers()
        
        start_time = time.time()
        
        while True:
            if time.time() - start_time > timeout_seconds:
                raise TimeoutError("Timed out waiting for clips to complete")

            try:
                with httpx.Client(timeout=30) as client:
                    response = client.get(url, headers=headers)
                    response.raise_for_status()
                    clips = response.json()

                if not isinstance(clips, list):
                     if not clips:
                         # logger.warning("No clips returned from feed, retrying...")
                         time.sleep(5)
                         continue
                     if isinstance(clips, dict) and 'detail' in clips:
                         logger.error(f"Error fetching feed: {clips['detail']}")
                         raise Exception(f"Feed error: {clips['detail']}")
                
                all_complete = True
                for clip in clips:
                    status = clip.get('status')
                    # clip_id = clip.get('id')
                    # logger.info(f"Clip {clip_id}: {status}") 
                    # Commented out verbose per-clip logging to keep console cleaner, 
                    # or can uncomment if strict monitoring needed.
                    
                    if status == 'error':
                        logger.error(f"Clip {clip.get('id')} failed generation.")
                        raise Exception(f"Clip {clip.get('id')} failed.")

                    if status != 'complete':
                        all_complete = False
                
                if all_complete and len(clips) >= len(clip_ids):
                    return clips
                
                time.sleep(10)
                
            except httpx.HTTPError as e:
                logger.error(f"HTTP Error checking status: {e}")
                time.sleep(5)
            except Exception as e:
                logger.error(f"Error in polling: {e}")
                raise
