import edge_tts
import requests
import emoji
import os
import json
import re
import shutil
import asyncio
import create_video
import random
import asyncpraw
import gender_guesser.detector as gender
import sys
from ollama import AsyncClient
sys.stdout.reconfigure(encoding='utf-8')


# Rutas para archivos
AUDIO_DIR = 'generador_shorts/audios'  # Directorio donde se guardarán los audios
SUBTITLE_DIR = 'generador_shorts/subtitulos'  # Directorio donde se guardarán los subtítulos
TEMP_DIR = 'generador_shorts/temp'  # Directorio donde se guardarán los videos sin audio
SOURCE_VIDEO_DIR = 'generador_shorts/videosRecortados'

def crear_historia():

    resultados = []

    title = "I ate cock and I liked it?"
    texto = "This is my story. One day, I (19M) ate a cock and I thoroughly enjoyed it."
    idioma = "en"   # en es
    genero = "Male" # Male Female

    print("Titulo: " + title)

    post_text = texto

    if(genero == "Male"):
        voz = idioma + "_male"
    if(genero == "Female"):
        voz = idioma + "_female"
    else:
        voz = idioma + "_male"

    resultados.append({'titulo': title, 'texto': post_text, 'idioma': voz})

    return resultados

# Función para limpiar el título y eliminar caracteres no permitidos
def limpiar_titulo(titulo):
    # Reemplazar caracteres no permitidos (como '/', '\', ':', '*', '?', '"', '<', '>', '|', ',') con '_'
    titulo = titulo[:30].replace(' ', '_')
    return re.sub(r'[\\/*?:"<>|\'",]', '_', titulo.strip())

# Función principal que conecta la obtención de historias con la generación de audios y subtítulos
async def main():
    
    # Crear las carpetas de audios y subtítulos si no existen
    if not os.path.exists(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)

    if not os.path.exists(SUBTITLE_DIR):
        os.makedirs(SUBTITLE_DIR)

    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    # Obtener historias por procesar
    historias = []

    historias.extend(crear_historia())

    print("\n\nGenerando " + str(len(historias)) + " videos\n\n")

    # Generar Videos
    for historia in historias:

        print("\n\nGenerating Video\n\n")

        titulo = historia['titulo']
        texto = historia['texto']
        idioma = historia['idioma']

        print("Procesando: " + titulo)

        tituloNuevo = limpiar_titulo(titulo)
        historia['tituloLimpio'] = tituloNuevo

        # Generar un random para elegir el video de fondo
        archivos = [f for f in os.listdir(SOURCE_VIDEO_DIR) if os.path.isfile(os.path.join(SOURCE_VIDEO_DIR, f))]
        indice_aleatorio = random.randint(0, len(archivos) - 1)
        archivo_video = "cropped_"+str(indice_aleatorio)+".mp4"

        await create_video.createVideo(historia, archivo_video)
        print(f"Video generado para: {titulo}")


        print("\n\nGenerating Description and Title\n\n")
        # Mas IA


    # Borrar los archivos temporales
    shutil.rmtree(AUDIO_DIR, ignore_errors=True)
    shutil.rmtree(SUBTITLE_DIR, ignore_errors=True)
    shutil.rmtree(TEMP_DIR, ignore_errors=True)


    print("\n\nDone\n\n")

# Ejecutar la función principal
if __name__ == "__main__":
    asyncio.run(main())
