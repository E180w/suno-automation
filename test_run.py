from suno_auto import SunoAuto
import time

def get_valid_count(prompt_text):
    try:
        user_input = input(prompt_text)
        count = int(user_input)
        if count > 0:
            return count
        print("Количество должно быть больше 0. Используем значение по умолчанию: 1")
        return 1
    except ValueError:
        print("Некорректный ввод. Используем значение по умолчанию: 1")
        return 1

def main():
    print("--- Suno AI Interactive Generator ---")
    
    # 1. Get User Input
    lyrics = input("Введите текст песни (Lyrics): ").strip()
    if not lyrics:
        print("Текст не введен, используется стандартный тестовый текст.")
        lyrics = "Test lyrics for a song about code"
        
    tags = input("Введите стиль (Tags): ").strip()
    if not tags:
        print("Стиль не введен, используется стандартный: pop, energetic")
        tags = "pop, energetic"
        
    count = get_valid_count("Введите количество генераций (Count): ")

    # Replacing any potential non-standard dashes just in case
    lyrics = lyrics.replace("—", "-")

    suno = SunoAuto()
    all_clip_ids = []

    print(f"\nЗапуск генерации {count} раз(а)...")

    try:
        # 2. Generation Loop
        for i in range(count):
            print(f"Запрос {i+1}/{count}...")
            result = suno.generate(lyrics, tags)
            
            if result and 'clips' in result:
                ids = [c['id'] for c in result['clips']]
                all_clip_ids.extend(ids)
                print(f"  -> Получены ID клипов: {ids}")
            else:
                print("  -> Ошибка: не удалось получить ID клипов в ответе.")
            
            # Small pause between requests to be polite to the API
            if i < count - 1:
                time.sleep(2)

        if not all_clip_ids:
            print("Нет клипов для отслеживания. Завершение.")
            return

        print(f"\nОжидание готовности {len(all_clip_ids)} клипов: {all_clip_ids}")
        
        # 3. Wait for all clips
        final_clips = suno.wait_for_clips(all_clip_ids)
        
        # 4. Output Results
        print("\n--- Generation Complete ---")
        print("Итоговый список ссылок:")
        for clip in final_clips:
            clip_id = clip.get('id')
            audio_url = clip.get('audio_url')
            title = clip.get('title', 'Untitled')
            status = clip.get('status')
            
            if status == 'complete':
                print(f"[{title}] {audio_url}")
            else:
                print(f"[Ошибка/Не готов] Клип {clip_id}: статус {status}")
            
    except Exception as e:
        print(f"\nПроизошла ошибка в процессе выполнения: {e}")

if __name__ == "__main__":
    main()
