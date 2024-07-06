"""
Este módulo se encarga de procesar textos almacenados en Google Cloud Storage mediante una función de Google Cloud Function.
Detecta el idioma del texto, lo traduce al español si no está en ese idioma y luego sube el texto traducido de vuelta al almacenamiento.

El flujo completo de la función se inicia con una solicitud HTTP que lleva la ubicación de un documento en Cloud Storage como parte
de la carga de la solicitud. La función recupera el texto del documento, detecta su idioma, lo traduce si es necesario,
y finalmente sube el texto traducido de vuelta al mismo bucket pero potencialmente bajo un nombre de archivo modificado.

Funciones:
- main: Función principal que maneja la solicitud HTTP, orquestando el flujo de procesamiento del texto.
- get_text_storage: Recupera el texto de un documento almacenado en Cloud Storage.
- detect_language: Utiliza Google Cloud Natural Language para detectar el idioma del texto.
- translate_text_to_spanish: Utiliza Google Cloud Translate para traducir el texto al español.
- upload_text_to_storage: Sube el texto procesado de vuelta a Cloud Storage.

Este módulo es ideal para ser usado en entornos donde se necesite procesamiento automático y traslación de documentos almacenados,
especialmente útil en entornos multilingües donde la traducción al español es frecuentemente requerida.
"""
from google.cloud import language_v1
from google.cloud import storage
from google.cloud import translate_v2 as translate

BUCKET_NAME = "mi-bucket-pdf"

def main(request):
    '''Función principal que maneja la solicitud de la función.

    Args:
        request (flask.Request): La solicitud HTTP.

    Returns:
        str: El idioma detectado del texto.
    '''
    try:
        document_location = request.data.decode("utf-8")
        text = get_text_storage(document_location)
        

        language = detect_language(text)

        if language != 'es':
            translated_text = translate_text_to_spanish(text)
            upload_text_to_storage(document_location, translated_text)

        return language
    except Exception as e:
        print(f"Error en main: {e}")
        return "Error en main"

def get_text_storage(document_location):
    '''Obtiene el texto del documento txt almacenado en Google Cloud Storage.

    Args:
        document_location (str): La ubicación del documento en el almacenamiento.

    Returns:
        str: El texto del documento.
    '''
    try:
        storage_client = storage.Client()

        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(document_location)
        text = blob.download_as_text()
        return text
    except Exception as e:
        print(f"Error en get_text_storage: {e}")
        return None

def detect_language(text):
    '''Detecta el idioma del texto utilizando el servicio de lenguaje de Google Cloud.

    Args:
        text (str): El texto a analizar.

    Returns:
        str: El código del idioma detectado.
    '''
    try:
        language_client = language_v1.LanguageServiceClient()

        document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
        response = language_client.analyze_sentiment(request={'document': document})
        return response.language
    except Exception as e:
        print(f"Error en detect_language: {e}")
        return None

def translate_text_to_spanish(text):
    '''Traduce el texto a español utilizando el servicio de traducción de Google Cloud.

    Args:
        text (str): El texto a traducir.

    Returns:
        str: El texto traducido.
    '''
    try:
        translate_client = translate.Client()

        translation = translate_client.translate(text, target_language='es')
        translated_text = translation['translatedText']
        return translated_text
    
    except Exception as e:
        print(f"Error en translate_text_to_spanish: {e}")
        return None

def upload_text_to_storage(document_location, text):
    '''Sube el texto traducido al almacenamiento en Google Cloud Storage.

    Args:
        document_location (str): La ubicación del documento en el almacenamiento.
        text (str): El texto a subir.
    '''
    try:
        storage_client = storage.Client()

        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(document_location)
        blob.upload_from_string(text, content_type='text/plain')
    
    except Exception as e:
        print(f"Error en upload_text_to_storage: {e}")
        