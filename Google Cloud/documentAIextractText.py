import os
import asyncio
from google.api_core.client_options import ClientOptions
from google.cloud import storage
from google.cloud import tasks_v2
from google.cloud import documentai_v1beta3 as documentai


endpoint = os.environ['endpoint']
project_id = os.environ['project_id']
processor_id = os.environ['processor_id']
input_bucket = os.environ['input_bucket']
output_bucket = os.environ['output_bucket']
url_funcion_destino = os.environ['url_funcion_destino']

async def process_pdf_async(content):
    '''Procesa un documento PDF asincrónicamente y extrae su texto.

    Args:
        content (str): URI del PDF en Google Cloud Storage.

    Returns:
        str: Texto extraído del documento PDF.
    '''
    try:        
        client = documentai.DocumentProcessorServiceAsyncClient(client_options=ClientOptions(api_endpoint=endpoint))
        name=client.processor_path(project_id,'eu',processor_id)
        
        gcs_document = documentai.GcsDocument(gcs_uri=content, mime_type='application/pdf')
        
        request = documentai.ProcessRequest(name=name, gcs_document=gcs_document)
        
        response=await client.process_document(request=request)

        document=response.document
               
        return document.text

    except Exception as e:
        print(f"Hubo un error {e}")

def extract_text_and_save(data, context):
    '''Funcion principal que obtiene el archivo y llama a las funciones para extraer y guardar el texto del documento.

    Args:
        data (dict): Datos del evento de Cloud Functions.
        context (google.cloud.functions.Context): Contexto del evento.
    '''
    try:

        file_name = data['name']
        bucket_name = data['bucket']
        
        if file_name.endswith('.pdf') and file_name.startswith(input_bucket):         
            content_uri = f"gs://{bucket_name}/{file_name}"

            text = asyncio.run(process_pdf_async(content_uri))

            if text:
                guardar_texto_en_storage(text, file_name, bucket_name)
           
        else:
            print('No se realiza ninguna acción')
       
    except Exception as e:
        print(f"Hubo un error al extraer y guardar el texto: {e}")       


def guardar_texto_en_storage(texto, nombre_archivo, nombre_bucket):
    '''Guarda el texto extraído en un archivo de texto en Cloud Storage.

    Args:
        texto (str): Texto extraído del documento PDF.
        nombre_archivo (str): Nombre del archivo PDF.
        nombre_bucket (str): Nombre del bucket de Cloud Storage.
    '''
    try:
        # Generar el nombre de archivo de salida
        nombre_archivo_salida = nombre_archivo.replace(input_bucket, output_bucket).replace('.pdf', '.txt')

        # Obtener el bucket
        cliente_storage = storage.Client()
        bucket = cliente_storage.get_bucket(nombre_bucket)

        # Crear el blob de salida y subir el texto
        blob_salida = bucket.blob(nombre_archivo_salida)
        blob_salida.upload_from_string(texto, content_type='text/plain')
        enviar_notificacion(nombre_archivo_salida)
        print(f'Texto extraído y guardado en gs://{nombre_bucket}/{nombre_archivo_salida}')
    except Exception as e:
        print(f"Hubo un error al guardar el texto en Cloud Storage: {e}")

def enviar_notificacion(text):
    '''Envía una notificación indicando que el archivo ya ha sido procesado.

    Args:
        text (str): Texto para la notificación. Contiene la localización del archivo txt
    '''
    try:
        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(project_id, "europe-west6", "task-completed-queue") 

        task = {
            "http_request": {
                "http_method": "POST",
                "url": url_funcion_destino,
                "body": text.encode("utf-8"),
                "headers": {"Content-type": "text/plain"},
            }
        }

        response = client.create_task(request={"parent": parent, "task": task})
    except Exception as e:
        print("No se pudo enviar la notificacion: ", e)