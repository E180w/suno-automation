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

    def _solve_captcha(self, sitekey, url):
        """
        Implements Capsolver integration logic (Mock/Ready-to-use structure).
        Requires CAPSOLVER_API_KEY in .env.
        """
        if not self.capsolver_key:
             raise SunoCaptchaRequired("Captcha required but CAPSOLVER_API_KEY is missing in environment.")
        
        logger.info(f"Solving CAPTCHA with Capsolver. Sitekey: {sitekey}")
        
        create_task_url = "https://api.capsolver.com/createTask"
        payload = {
            "clientKey": self.capsolver_key,
            "task": {
                "type": "HCaptchaTaskProxyLess",
                "websiteURL": url,
                "websiteKey": sitekey
            }
        }
        
        try:
            with httpx.Client(timeout=30) as client:
                # Create Task
                resp = client.post(create_task_url, json=payload)
                resp.raise_for_status()
                task_data = resp.json()
                
                if task_data.get("errorId", 0) != 0:
                     raise Exception(f"Capsolver Create Task Error: {task_data.get('errorDescription')}")
                
                task_id = task_data.get("taskId")
                if not task_id:
                    raise Exception("Failed to ensure Capsolver taskId")
                
                logger.info(f"Capsolver Task ID: {task_id}. Waiting for solution...")
                
                # Poll for Result
                get_result_url = "https://api.capsolver.com/getTaskResult"
                for _ in range(60): # Max wait 120s
                    time.sleep(2)
                    status_resp = client.post(get_result_url, json={"clientKey": self.capsolver_key, "taskId": task_id})
                    status_data = status_resp.json()
                    
                    if status_data.get("status") == "ready":
                        logger.success("Captcha solved successfully.")
                        return status_data.get("solution", {}).get("gRecaptchaResponse")
                    
                    if status_data.get("status") == "failed":
                        raise Exception(f"Capsolver failed: {status_data.get('errorDescription')}")
                
                raise TimeoutError("Capsolver timeout waiting for solution")
                
        except Exception as e:
            logger.error(f"Error solving captcha: {e}")
            raise

    def generate(self, prompt: str, tags: str = "", make_instrumental: bool = False):
        """
        Sends a generation request. Handles potential hCaptcha by using Capsolver.
        """
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
                response.raise_for_status()
                data = response.json()
                
                # Check for Captcha requirement
                # Suno API usually returns 'captcha_type' in the body if verification is needed (sometimes with 200, sometimes 403)
                if isinstance(data, dict) and "captcha_type" in data:
                    logger.warning(f"Captcha detected: {data.get('captcha_type')}")
                    # Hypothetically extracting sitekey from response or using a known constant
                    sitekey = data.get("sitekey", "7e834898-d15f-4ce9-95e2-224422e519e2") # Example default or extracted
                    
                    # Solve
                    token = self._solve_captcha(sitekey, "https://suno.com")
                    
                    # Update Payload with Token & New UUID
                    payload["token"] = token
                    payload["transaction_uuid"] = str(uuid.uuid4())
                    
                    logger.info("Retrying request with Captcha token...")
                    response = client.post(url, headers=headers, json=payload)
                    response.raise_for_status()
                    data = response.json()
                
                logger.success("Generation request successful")
                return data

        except httpx.HTTPError as e:
            logger.error(f"HTTP Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                 logger.error(f"Response content: {e.response.text}")
            raise
        except ValueError as e:
            logger.error(f"JSON Parsing Error: {e}")
            raise

    def wait_for_clips(self, clip_ids, timeout_seconds=600):
        """
        Polls the feed API until all clips are complete or timeout is reached.
        """
        ids_str = ",".join(clip_ids)
        url = f"{self.base_url}/api/feed/?ids={ids_str}"
        headers = self._get_headers()
        
        start_time = time.time()
        logger.info(f"Starting to poll for clips: {clip_ids}")
        
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
                         logger.warning("No clips returned from feed, retrying...")
                         time.sleep(5)
                         continue
                     # If it's a dict (error or wrapped), handle it
                     if isinstance(clips, dict) and 'detail' in clips:
                         logger.error(f"Error fetching feed: {clips['detail']}")
                         raise Exception(f"Feed error: {clips['detail']}")
                
                all_complete = True
                for clip in clips:
                    status = clip.get('status')
                    clip_id = clip.get('id')
                    logger.info(f"Clip {clip_id}: {status}")
                    
                    # Fail fast on error
                    if status == 'error':
                        logger.error(f"Clip {clip_id} failed generation.")
                        raise Exception(f"Clip {clip_id} failed.")

                    if status != 'complete':
                        all_complete = False
                
                if all_complete and len(clips) >= len(clip_ids):
                    logger.success("All clips completed successfully.")
                    return clips
                
                time.sleep(10) # 10s delay between polls
                
            except httpx.HTTPError as e:
                logger.error(f"HTTP Error checking status: {e}")
                time.sleep(5)
            except Exception as e:
                logger.error(f"Error in polling: {e}")
                raise
