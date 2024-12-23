import whisper

DIR = 'C:\\Users\\lfben\\Desktop\\IaVideos_3.0\\generador_shorts\\audios\\' 

# Carga el modelo de Whisper
model = whisper.load_model("medium")

# Transcribe el archivo .mp3
result = model.transcribe(DIR + "ghost_saucing.mp3", task="transcribe")

# Guarda como .srt
with open("subtitulos.srt", "w", encoding="utf-8") as srt_file:
    for i, segment in enumerate(result["segments"]):
        start = segment["start"]
        end = segment["end"]
        text = segment["text"]
        srt_file.write(f"{i + 1}\n{start:.2f} --> {end:.2f}\n{text.strip()}\n\n")