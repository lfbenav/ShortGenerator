from PIL import Image, ImageDraw, ImageFont
import textwrap

def crear_imagen_con_texto(texto, ruta_imagen_fondo, ruta_salida, margen=20, fuente_tamaño=50, fuente_path="arial.ttf"):
    """
    Crea una imagen con texto ajustado dinámicamente a varias líneas.
    
    :param texto: El texto a colocar en la imagen.
    :param ruta_imagen_fondo: Ruta de la imagen de fondo.
    :param ruta_salida: Ruta donde se guardará la imagen generada.
    :param margen: Margen entre el texto y los bordes de la imagen.
    :param fuente_tamaño: Tamaño fijo de la fuente.
    :param fuente_path: Ruta a la fuente TrueType.
    """
    # Cargar la imagen de fondo
    imagen_fondo = Image.open(ruta_imagen_fondo)
    ancho_img, alto_img = imagen_fondo.size

    # Crear objeto de dibujo
    draw = ImageDraw.Draw(imagen_fondo)


    fuente = ImageFont.load_default()

    # Ajustar el texto a múltiples líneas
    max_ancho_linea = ancho_img - 2 * margen  # Considerar márgenes
    lineas = textwrap.wrap(texto, width=max_ancho_linea // fuente_tamaño * 2)

    # Calcular el alto total del texto
    alto_texto = sum(draw.textbbox((0, 0), linea, font=fuente)[3] for linea in lineas)

    # Calcular posición centrada
    y_actual = (alto_img - alto_texto) // 2  # Centrar verticalmente
    for linea in lineas:
        bbox = draw.textbbox((0, 0), linea, font=fuente)
        ancho_linea = bbox[2] - bbox[0]
        alto_linea = bbox[3] - bbox[1]
        x = (ancho_img - ancho_linea) // 2  # Centrar horizontalmente
        draw.text((x, y_actual), linea, font=fuente, fill="black")  # Cambiado a negro
        y_actual += alto_linea

    # Guardar la imagen resultante
    imagen_fondo.save(ruta_salida)
    print(f"Imagen generada y guardada en: {ruta_salida}")

# Ejemplo de uso
template_path = "C:\\Users\\lfben\\Desktop\\IaVideos_4.0\\generador_shorts\\overlay.png"
output_path = "C:\\Users\\lfben\\Desktop\\IaVideos_4.0\\generador_shorts\\overlay_res_wand.png"
text = "Este es un texto muy largo que debe ajustarse automáticamente a la imagen, dividiéndose en varias líneas si es necesario para evitar que se corte o desborde."
font_path = "C:\\Windows\\Fonts\\Arial.ttf"

crear_imagen_con_texto(
    texto=text,
    ruta_imagen_fondo=template_path,
    ruta_salida=output_path,
    margen=10,
    fuente_tamaño=50,  # Tamaño fijo de la fuente
    fuente_path=font_path
)
