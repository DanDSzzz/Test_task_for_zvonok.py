import sys
import json
import os
from pydub import AudioSegment
from vosk import Model, KaldiRecognizer
import soundfile as sf
import imageio_ffmpeg as ffmpeg


# Настройка пути к ffmpeg, установленному через imageio-ffmpeg
AudioSegment.ffmpeg = ffmpeg.get_ffmpeg_exe()


def modify_audio(file_path='sample-3s.wav', speed=1.0, volume_change=0):
    # Открываем аудиофайл
    audio = AudioSegment.from_wav(file_path)

    # Изменяем скорость воспроизведения
    audio = audio.speedup(playback_speed=speed)

    # Изменяем громкость
    audio = audio + volume_change

    # Сохраняем модифицированный файл
    modified_file_path = f"modified_{os.path.basename(file_path)}"
    audio.export(modified_file_path, format="wav")
    print(f"Модифицированный файл сохранен как {modified_file_path}")


def transcribe_audio(file_path, language_model="en"):
    # Загрузка модели
    if language_model == "ru":
        model = Model("model_ru")
    else:
        model = Model("model_en")

    # Открываем аудиофайл
    with sf.SoundFile(file_path) as audio_file:
        recognizer = KaldiRecognizer(model, audio_file.samplerate)
        recognizer.SetWords(True)

        results = []
        while True:
            data = audio_file.read(4000, dtype='int16')
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                results.append(json.loads(recognizer.Result()))
            else:
                recognizer.PartialResult()

        results.append(json.loads(recognizer.FinalResult()))

    # Логирование результата в JSON-файл
    transcription = [result.get('text', '') for result in results]
    transcription_text = ' '.join(transcription).strip()

    json_result = {
        "file": os.path.basename(file_path),
        "transcription": transcription_text
    }

    log_file = f"{os.path.basename(file_path)}_transcription.json"
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(json_result, f, ensure_ascii=False, indent=4)

    print(f"Результат расшифровки сохранен в файл {log_file}")


def main():
    if len(sys.argv) < 3:
        print("Использование:")
        print("  python app.py modify <path_to_wav> <speed> <volume_change>")
        print("  python app.py transcribe <path_to_wav> <language>")
        sys.exit(1)

    command = sys.argv[1]
    file_path = sys.argv[2]

    if command == "modify":
        if len(sys.argv) != 5:
            print("Ошибка: Укажите скорость и изменение громкости.")
            sys.exit(1)

        speed = float(sys.argv[3])
        volume_change = int(sys.argv[4])
        modify_audio(file_path, speed, volume_change)

    elif command == "transcribe":
        if len(sys.argv) != 4:
            print("Ошибка: Укажите язык (en или ru).")
            sys.exit(1)

        language_model = sys.argv[3]
        transcribe_audio(file_path, language_model)

    else:
        print("Неизвестная команда.")
        sys.exit(1)


if __name__ == "__main__":
    main()