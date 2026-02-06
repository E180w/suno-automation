from suno_auto import SunoAuto

LYRICS = """
Утекай
В подворотне нас ждет маньяк
Хочет нас посадить на крючок
Красавицы уже лишились своих чар
Машины в парк
И все гангстеры спят
Осталась одна только ты
Утекай
""".strip()

# Replacing any potential non-standard dashes just in case
LYRICS = LYRICS.replace("—", "-")

TAGS = "indian raga, sitar, tabla, hypnotic, psychedelic"

def main():
    suno = SunoAuto()
    try:
        # Step 1: Initialize generation
        result = suno.generate(LYRICS, TAGS)
        print("Generation started. Result:", result)
        
        # Step 2: Extract clip IDs
        clip_ids = [c['id'] for c in result['clips']]
        print(f"Waiting for clips: {clip_ids}")
        
        # Step 3: Wait for completion
        final_clips = suno.wait_for_clips(clip_ids)
        
        # Step 4: Output results
        print("\n--- Generation Complete ---")
        for clip in final_clips:
            print(f"Clip ID: {clip['id']}")
            print(f"Title: {clip.get('title', 'Untitled')}")
            print(f"Audio URL: {clip['audio_url']}")
            print("-" * 30)
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
