import os
import random
import subprocess
import whisper
import edge_tts
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip

SPEED = "+5%"

# Función asincrónica para generar los archivos de audio ----------------------------------------------------------------------------
async def generar_audio(titulo, texto, idioma, output_audio):

    print("\n\nGenerating Audio\n\n")

    VOICES = {
        'en_male': 'en-US-GuyNeural',      # Inglés - voz masculina
        'es_male': 'es-ES-AlvaroNeural',    # Español - voz masculina
        'en_female': 'en-US-AvaNeural',      # Inglés - voz femenina
        'es_female': 'es-SV-LorenaNeural'    # Español - voz femenina
    }

    voice = VOICES[idioma]

    guion = titulo + "\n" + texto

    communicate = edge_tts.Communicate(guion, voice, rate=SPEED)
    await communicate.save(output_audio)

    print(f"Audio generado para: {titulo}")

# Función asincrónica para obtener cuanto dura el titulo en leerse ----------------------------------------------------------------------------
async def duracion_titulo(titulo, idioma):

    print("\n\nCalculating Title Duration\n\n")

    VOICES = {
        'en_male': 'en-US-GuyNeural',      # Inglés - voz masculina
        'es_male': 'es-ES-AlvaroNeural',    # Español - voz masculina
        'en_female': 'en-US-AvaNeural',      # Inglés - voz femenina
        'es_female': 'es-SV-LorenaNeural'    # Español - voz femenina
    }

    voice = VOICES[idioma]

    # Archivo temporal para guardar el audio generado
    temp_audio_file = "temp_title_audio.mp3"

    # Generar el audio para el título
    communicate = edge_tts.Communicate(titulo, voice, rate=SPEED)
    await communicate.save(temp_audio_file)

    # Obtener la duración del archivo MP3
    with AudioFileClip(temp_audio_file) as audio:
        duration = audio.duration

    # Eliminar el archivo temporal
    os.remove(temp_audio_file)

    print(f"Duración del título '{titulo}': {duration} segundos")
    return duration

# Crear los subtitulos basados en el audio ----------------------------------------------------------------------------
def generate_srt_from_audio(audio_file, output_srt, words_per_segment=4):
    
    def format_srt_time(seconds):
        milliseconds = int((seconds % 1) * 1000)
        seconds = int(seconds)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

    def palabra_por_palabra():
        # Cargar el modelo Whisper
        model = whisper.load_model("medium")

        # Transcribir el audio con marcas de tiempo por palabra
        result = model.transcribe(audio_file, task="transcribe", word_timestamps=True)

        # Generar subtítulos en formato SRT palabra por palabra
        with open(output_srt, "w", encoding="utf-8") as srt_file:
            index = 1
            for segment in result["segments"]:
                # Verificar que 'words' esté presente en el segmento
                if 'words' in segment:
                    for word in segment['words']:
                        start_time = format_srt_time(word["start"])
                        end_time = format_srt_time(word["end"])
                        text = word.get("word", "")  # Utiliza 'word' en lugar de 'text' si no existe

                        # Escribir cada palabra con su marca de tiempo
                        srt_file.write(f"{index}\n")
                        srt_file.write(f"{start_time} --> {end_time}\n")
                        srt_file.write(f"{text}\n\n")
                        index += 1
                else:
                    print("No se encontraron palabras en este segmento")

    def segmento_por_segmento():
        # Cargar el modelo Whisper
        model = whisper.load_model("medium")

        # Transcribir el audio con marcas de tiempo por palabra
        result = model.transcribe(audio_file, task="transcribe", word_timestamps=True)

        # Generar subtítulos en formato SRT con las reglas específicas
        with open(output_srt, "w", encoding="utf-8") as srt_file:
            index = 1
            for segment in result["segments"]:
                if 'words' in segment:
                    words = segment['words']
                    buffer = []  # Almacena temporalmente palabras para el grupo
                    start_time = None
                    
                    for word in words:
                        word_text = word.get("word", "").replace(" ", "")
                        
                        # Si el buffer está vacío, establecer el inicio del segmento
                        if not buffer:
                            start_time = word["start"]
                        
                        buffer.append(word_text)

                        # Verificar si la palabra actual termina en coma/punto o si se alcanzó el tamaño máximo del grupo
                        if word_text.endswith((',', '.', ':', '?')) or len(buffer) == words_per_segment:
                            # Obtener el tiempo de fin del último elemento en el grupo
                            end_time = word["end"]
                            
                            buffer_text = ""
                            for word in buffer:
                                buffer_text += word.replace(" ", "") + " "

                            # Escribir el segmento en el archivo SRT
                            srt_file.write(f"{index}\n")
                            srt_file.write(f"{format_srt_time(start_time)} --> {format_srt_time(end_time)}\n")
                            srt_file.write(f"{buffer_text}\n\n")
                            index += 1
                            
                            # Limpiar el buffer para el siguiente grupo
                            buffer = []
                            start_time = None
                    
                    # Procesar cualquier palabra restante en el buffer
                    if buffer:
                        end_time = words[-1]["end"]
                        srt_file.write(f"{index}\n")
                        srt_file.write(f"{format_srt_time(start_time)} --> {format_srt_time(end_time)}\n")
                        srt_file.write(f"{' '.join(buffer)}\n\n")
                        index += 1
                else:
                    print("No se encontraron palabras en este segmento")

    print("\n\nGenerating Subtitles\n\n")

    # Seleccionar uno, para ver si los subtitulos van palabra por palabra u oracion por oracion
    #palabra_por_palabra()
    segmento_por_segmento()
 
    print(f"Subtítulos generados en {output_srt}")


# Agregar el audio y recortar la duracion del video ----------------------------------------------------------------------------
def add_audio(inputVideo, inputAudio, outputVideoAudio):

    print("\n\nAdding Audio\n\n")

    # Cargar el video sin audio y el audio
    video = VideoFileClip(inputVideo)
    audio = AudioFileClip(inputAudio)
    
    # Calcular la duración del video y del audio
    video_duration = video.duration
    audio_duration = audio.duration

    # Asegurar que el audio no sea más largo que el video
    if audio_duration > video_duration:
        raise ValueError("La duración del audio no puede ser mayor que la del video.")
    
    # Calcular un punto de inicio aleatorio
    max_start_time = video_duration - audio_duration
    start_time = random.uniform(0, max_start_time)
    end_time = start_time + audio_duration

    # Extraer un segmento aleatorio del video
    video_segment = video.subclip(start_time, end_time)
    
    # Unir el audio al segmento de video
    video_segment = video_segment.set_audio(audio)
    
    # Exportar el nuevo archivo de video con audio
    video_segment.write_videofile(outputVideoAudio, codec="libx264", audio_codec="aac")


# Agregar el la imagen al video ----------------------------------------------------------------------------
def add_image(inputVideo, duration, title, outputVideoImage):
    print("\n\nAdding Image Overlay\n\n")
    
    # Ruta de la imagen que se superpondrá
    image_path = "C:\\Users\\lfben\\Desktop\\IaVideos_4.0\\generador_shorts\\overlay.png"
    
    # Cargar el video
    video = VideoFileClip(inputVideo)
    video_duration = video.duration
    
    # Verificar que la duración especificada no exceda la duración del video
    if duration > video_duration:
        raise ValueError("La duración de la imagen no puede ser mayor que la duración del video.")
    
    # Crear un clip de la imagen con la duración especificada
    image_clip = (
        ImageClip(image_path)
        .set_duration(duration)  # Duración específica de la imagen
        .set_position("center")  # Centrar la imagen en el video
        .resize(height=video.size[1] // 3)  # Ajustar tamaño de la imagen (1/3 de la altura del video)
    )
    
    # Crear el clip compuesto con el video como fondo
    video_with_overlay = CompositeVideoClip(
        [video, image_clip.set_start(0)],  # El video sigue activo mientras se muestra la imagen
        size=video.size
    )
    
    # Guardar el video con la imagen superpuesta, reemplazando el original
    video_with_overlay.write_videofile(
        outputVideoImage, 
        codec="libx264", 
        audio_codec="aac"
    )
    
    print(f"Video con imagen superpuesta guardado en {outputVideoImage}")


# Crear los subtitulos quemados en el video ----------------------------------------------------------------------------
def burn_subtitles(inputVideo, subtitleName, outputVideo):
    # Añadir subtítulos quemados en el video centrado

    print("\n\nBurning Subtitles\n\n")

    inputSubtitles = "generador_shorts/subtitulos/" + subtitleName + '.srt'
    fontsize = 16
    fontname = "Arial Bold"
    height=1920
    comando = [
            'ffmpeg',
            '-i', inputVideo,  # Archivo de entrada (video)
            '-vf', f"subtitles={inputSubtitles}:force_style='Alignment=10,Fontsize={fontsize},Fontname={fontname},MarginV={int(height*0.3)}'", 
            '-c:a', 'copy',  # Copiar el audio sin cambios
            outputVideo  # Archivo de salida
        ]
    subprocess.run(comando, check=True)
    print(f"Subtítulos quemados en {outputVideo}")


# Correr todo ----------------------------------------------------------------------------
async def createVideo(story_dict, videoName):

    title = story_dict['titulo']
    texto = story_dict['texto']
    idioma = story_dict['idioma']
    tituloLimpio = story_dict['tituloLimpio']

    directorio = 'C:\\Users\\lfben\\Desktop\\IaVideos_4.0\\generador_shorts\\'

    # Define los paths de los archivos
    input_cropped_video = directorio + 'videosRecortados\\' + videoName

    # Temporal
    tempAudio = directorio + 'audios\\' + tituloLimpio + '.mp3'
    tempAudioVideo = directorio + 'temp\\' + 'audio_' + tituloLimpio + '.mp4'
    tempAudioImageVideo = directorio + 'temp\\' + 'image_' + tituloLimpio + '.mp4'
    tempSubtitles = directorio + 'subtitulos\\' + tituloLimpio + '.srt'

    # Output
    output_video = directorio + 'videosCombinados\\' + 'final_' + tituloLimpio + '.mp4'
    if os.path.exists(output_video):
        os.remove(output_video)

    # Crear el audio
    await generar_audio(title, texto, idioma, tempAudio)

    # Obtener la duracion del titulo
    #duracion = await duracion_titulo(title, idioma)
    duracion = 0

    # Agregar el audio y recortar la duracion del video
    add_audio(input_cropped_video, tempAudio, tempAudioVideo)
    
    # Agregar la imagen
    add_image(tempAudioVideo, duracion, title, tempAudioImageVideo)

    # Generar Subs
    generate_srt_from_audio(tempAudio, tempSubtitles)

    # Añadir subtítulos quemados en el video recortado
    burn_subtitles(tempAudioImageVideo, tituloLimpio, output_video)
