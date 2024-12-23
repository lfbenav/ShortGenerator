import os
import subprocess

# Cambiar el recorte de los bordes del video ----------------------------------------------------------------------------
def crop_video(inputVideo, outputVideo):
    # Recortar video al formato 9:16 manteniendo el centro
    cmd_size = f"ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0:s=x {inputVideo}"
    result = subprocess.run(cmd_size, shell=True, capture_output=True, text=True)
    
    # Obtener las dimensiones del video
    width, height = map(int, result.stdout.strip().split('x'))
    print(f"Dimensiones originales del video: {width}x{height}")

    # Calcular el recorte para mantener el aspecto 9:16
    new_height = height  # Mantener la altura original
    new_width = int(new_height * (9 / 16))  # Calcular el ancho para 9:16

        # Asegurarse de que el ancho no exceda las dimensiones originales
    if new_width > width:
        new_width = width
        new_height = int(new_width * (16 / 9))

    x_offset = (width - new_width) // 2  # Calcular el offset horizontal
    y_offset = (height - new_height) // 2  # Calcular el offset vertical

    print("\n\nCropping Video\n\n")

    cmd_crop = f"ffmpeg -i {inputVideo} -vf \"crop={new_width}:{new_height}:{x_offset}:{y_offset}\" -c:a copy {outputVideo}"
    subprocess.run(cmd_crop, shell=True)
    print(f"Video recortado guardado en {outputVideo}")

def process_videos(input_folder, output_folder):
    # Verificar si la carpeta de salida existe, si no, crearla
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Recorrer todos los archivos de la carpeta de videos
    for filename in os.listdir(input_folder):
        inputVideo = os.path.join(input_folder, filename)
        
        # Verificar si es un archivo de video
        if os.path.isfile(inputVideo) and filename.lower().endswith(('.mp4', '.mov', '.avi')):
            # Generar el nombre de salida con el prefijo "cropped_"
            outputVideo = os.path.join(output_folder, f"cropped_{filename}")
            
            # Verificar si el video ya existe en la carpeta de salida
            if not os.path.exists(outputVideo):
                print(f"Procesando video: {filename}")
                crop_video(inputVideo, outputVideo)
            else:
                print(f"El video {filename} ya existe en la carpeta de salida. Omitiendo...")

# Ruta a las carpetas
input_folder = 'generador_shorts/videosLimpios'
output_folder = 'generador_shorts/videosRecortados'

# Procesar los videos
process_videos(input_folder, output_folder)