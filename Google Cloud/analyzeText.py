from google.cloud import language_v1
from google.cloud import storage
from google.cloud import translate_v2 as translate
import json

bucket_name = "mi-bucket-pdf"

def main(request):
    '''Función principal que maneja la solicitud de la función.

    Args:
        request (flask.Request): La solicitud HTTP.

    Returns:
        str: El idioma detectado del texto.
    '''
    try:
        text = get_text_storage(request.data.decode("utf-8"))

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

        bucket = storage_client.bucket(bucket_name)
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

        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(document_location)
        blob.upload_from_string(text, content_type='text/plain')
    
    except Exception as e:
        print(f"Error en upload_text_to_storage: {e}")
