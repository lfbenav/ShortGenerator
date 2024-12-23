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
JSON_FILE = "generador_shorts/post_ids.json"
DESCRIPTIONS_FILE = "generador_shorts/descripciones/descripciones.txt"

SUBREDDITS = {
    #'LetsNotMeet': 'en', 
    #'TrueOffMyChest': 'en',
    'AmITheJerk': 'en',
    'AITAH': 'en',
    #'self': 'en'
}

async def corregir_texto(texto):
    prompt = f"""
    I want you to apply all these rules:
    - I will give you a text about a person asking if they are the jerks for doing something.
    - I want you to use the text to rewrite the story with good grammar and make it more comprehensive and short, make it last about 1 minute.
    - If the story says anything about the age and geneder of the characters, keep them. For example, I(20M) or my wife (20F).
    - Dont use abreviations, replace them for their meaning (except if the abreviation is I(20M) or they(20F), in this cases, keep them as it is).
    - Return only the text and nothing else. Do not add any comments or explanations about what you did, I only need the corrected text.
    - Do not write "Here's the rewritten text".
    - Do not reply with "Here's a rewritten version of the text with improved grammar and clarity", "Here's the rewritten text", "Here is a rewritten version of the text" or anything like that, seriously, I only need the story, any coments may ruin it.

    Text: {texto}
    """
    
    response = await AsyncClient().generate('llama3.2', prompt)
    texto_corregido = response['response']
    
    #print(texto_corregido)

    return texto_corregido

async def crear_titulo(texto):
    prompt = f"""
    - I will give you a text about a person asking if they are the jerks for doing something.
    - I want you to create a question about the text, like, I am the jerk for x. Write it in first person.
    - Dont use abreviations.
    - Do not add any comments or explanations about what you did, I only need the corrected text.
    - Do not tell me "Here's a rewritten version of the text with improved grammar and clarity" or anything like that, seriously, I only need the story, any coments may ruin it.

    Text: {texto}
    """
     
    response = await AsyncClient().generate('llama3.2', prompt)
    titulo = response['response']
    
    #print(titulo)

    return titulo

async def obtener_genero(texto):
    prompt = f"""
    - Analyze this text, and reply "Male" or "Female" depending on what you think is right.
    - Dont reply anything else except "Male" or "Female".
    - You can base the decision based on key words, like when they say I(12M), wich is Male, or I(12F), which means a Female.
    - If there are no keywords, base the decision on social stereotypes.
    - If you are not certain, reply "Male".
    Text: {texto}
    """
    
    response = await AsyncClient().generate('llama3.2', prompt)
    genero = response['response']
    
    #print(genero)

    return genero

async def generar_descripcion(texto, url):
    prompt = f"""
    - Generate a short description for this text.
    - Return only the created description and nothing else.
    - Do not add any comments or explanations about what you did, I only need description.

    Text: {texto}
    """
    
    response = await AsyncClient().generate('llama3.2', prompt)
    descripcion = response['response']

    tags = "#reddit #redditstories #aita #shorts\n\n"
    tags += descripcion
    tags += "\n\n"
    tags += f"Original Submission: {url}"
    
    #print(tags)

    return tags

def guardar_id_en_json(post_id):
    # Carga el archivo JSON o inicializa una lista vacía
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r") as file:
            ids = json.load(file)
    else:
        ids = []

    # Verifica si el ID ya está en la lista
    if post_id not in ids:
        ids.append(post_id)
        with open(JSON_FILE, "w") as file:
            json.dump(ids, file, indent=4)
        print(f"ID {post_id} guardado.")
    else:
        print(f"ID {post_id} ya existe en el archivo.")

def validar_id_en_json(post_id):
    if not os.path.exists(JSON_FILE):
        with open(JSON_FILE, "w") as file:
            json.dump([], file)  # Inicia el archivo con una lista vacía
            print(f"Archivo '{JSON_FILE}' creado.")

    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r") as file:
            ids = json.load(file)
        return post_id in ids
    return False

async def obtener_historias(subreddit):

    resultados = []

    # Configurar cliente de Reddit con las credenciales
    reddit = asyncpraw.Reddit(client_id='J8ByLE2aTELSgPFCHnp9DQ',  
                        client_secret='0Z5tTYTOha2PKvFxfoBL7qRLUL3NVg', 
                        user_agent='python:MyRedditApp:1.0 (by /u/my_reddit_username)') 

    # Seleccionar los subreddit y obtener los posts más populares
    subreddit_object = await reddit.subreddit(subreddit)

    # Obtener los posts más populares de las últimas 24 horas
    async for submission in subreddit_object.top(time_filter='day', limit=15): 
        if validar_id_en_json(submission.id) == False:
            if submission.is_self:  # Verifica si la publicación tiene texto 
                if(len(submission.selftext.split()) <= 500):
                    print("\nNueva Historia\n")

                    post_text = submission.selftext
                    post_text = emoji.replace_emoji(post_text, replace='')
                    post_text = await corregir_texto(post_text)

                    titulo = await crear_titulo(submission.title)

                    # if(len(post_text)<350):
                    if(len(post_text)<200):
                        print("Muy corto")
                        guardar_id_en_json(submission.id)
                        continue

                    idioma = SUBREDDITS[subreddit]


                    genero = await obtener_genero(post_text)
                    if(genero == "Male"):
                        voz = idioma + "_male"
                    if(genero == "Female"):
                        voz = idioma + "_female"
                    else:
                        voz = idioma + "_male"

                    print(titulo + "\n" + post_text + "\n" + voz)

                    guardar_id_en_json(submission.id)
                    resultados.append({'titulo': titulo, 'texto': post_text, 'idioma': voz, 'url': submission.url})
            else:
                print(f"Text: No text content (This is a link post)")
                guardar_id_en_json(submission.id)

    await reddit.close()
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

    for reddit in SUBREDDITS.keys():
        historias.extend(await obtener_historias(reddit))

    print("\n\nGenerando " + str(len(historias)) + " videos\n\n")

    # Generar Descripciones
    with open(DESCRIPTIONS_FILE, 'a', encoding='utf-8') as archivo:
        archivo.write(f"\n\nNuevo Batch de Historias\n\n")
        for historia in historias:

            print("\n\nGenerating Description and Title\n\n")

            titulo = historia['titulo']
            texto = historia['texto']
            idioma = historia['idioma']
            url = historia['url']

            print("Generando: " + titulo)

            # Escribir título y URL en el archivo de texto
            archivo.write(f"{titulo} 💔 ~ Reddit Stories\n\n")
            archivo.write(await generar_descripcion(texto, url))
            archivo.write(f"\n\n")
            archivo.write(f"-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-\n\n")

    # Generar Videos
    for historia in historias:

        print("\n\nGenerating Video\n\n")

        titulo = historia['titulo']
        texto = historia['texto']
        idioma = historia['idioma']
        url = historia['url']

        print("Procesando: " + titulo)

        tituloNuevo = limpiar_titulo(titulo)
        historia['tituloLimpio'] = tituloNuevo

        # Generar un random para elegir el video de fondo
        archivos = [f for f in os.listdir(SOURCE_VIDEO_DIR) if os.path.isfile(os.path.join(SOURCE_VIDEO_DIR, f))]
        indice_aleatorio = random.randint(0, len(archivos) - 1)
        archivo_video = "cropped_"+str(indice_aleatorio)+".mp4"

        await create_video.createVideo(historia, archivo_video)
        print(f"Video generado para: {titulo}")

    print("\n\nSe generaron " + str(len(historias)) + " videos\n\n")

    # Borrar los archivos temporales
    shutil.rmtree(AUDIO_DIR, ignore_errors=True)
    shutil.rmtree(SUBTITLE_DIR, ignore_errors=True)
    shutil.rmtree(TEMP_DIR, ignore_errors=True)


    print("\n\nDone\n\n")

# Ejecutar la función principal
if __name__ == "__main__":
    asyncio.run(main())
