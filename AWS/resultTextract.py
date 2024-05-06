from logging import exception
import boto3
import json
from botocore.exceptions import ClientError
import os

s3 = boto3.client('s3')
comprehend = boto3.client('comprehend')
translate = boto3.client('translate')
textract = boto3.client("textract")
bucket_name = os.environ['BUCKET_NAME']


def detect_language(text):
    """
    Detecta el idioma predominante del texto utilizando AWS Comprehend.

    Parámetros:
    - text: Texto a analizar.

    Devuelve:
    - Código del idioma predominante del texto.
    - En caso de error, se maneja la excepción y se eleva.
    """

    try:
        response = comprehend.detect_dominant_language(Text=text)
        dominant_language = response['Languages'][0]['LanguageCode']
        return dominant_language
    except Exception as e:
        print("Error al detectar el idioma:", e)
        raise

def translate_text(text, source_lang, target_lang):
    """
    Traduce el texto de un idioma de origen a un idioma de destino utilizando AWS Translate.

    Parámetros:
    - text: Texto a traducir.
    - source_lang: Idioma de origen.
    - target_lang: Idioma de destino.

    Devuelve:
    - Texto traducido.
    - En caso de error, se maneja la excepción y se eleva.
    """
    try:
        translation_response = translate.translate_text(
            Text=text,
            SourceLanguageCode=source_lang,
            TargetLanguageCode=target_lang
        )
        translated_text = translation_response['TranslatedText']
        return translated_text
    except Exception as e:
        print("Error al traducir el texto:", e)
        raise

def translate_content(columnas_por_pagina):
    """
    Traduce el contenido de las páginas si está mayoritariamente en inglés.

    Parámetros:
    - columnas_por_pagina: Diccionario con el contenido de las páginas.

    Devuelve:
    - Diccionario con el contenido traducido.
    - En caso de error, se maneja la excepción y se eleva.
    """
    translated_columnas_por_pagina = {}
    for page_number, page_content in columnas_por_pagina.items():
        content = page_content['Content']
        try:
            dominant_language = detect_language(content)
            if dominant_language == 'en':
                translated_content = translate_text(content, 'en', 'es')
                page_content['Content'] = translated_content
            translated_columnas_por_pagina[page_number] = page_content
        except Exception as e:
            print("Error al traducir el contenido de la página:", e)
            raise
    return translated_columnas_por_pagina

def lambda_handler(event, context):
    """
    Función principal que maneja el evento Lambda.

    Parámetros:
    - event: Evento que desencadena la función Lambda.
    - context: Objeto de contexto que proporciona información sobre la ejecución.

    Devuelve:
    - Respuesta HTTP con el estado del procesamiento del archivo.
    - En caso de error, se maneja la excepción y se devuelve un mensaje de error.
    """
    try:
        message = json.loads(event['Records'][0]['Sns']['Message'])
        
        if  message['Status'] == 'SUCCEEDED':
        
            job_id =  message["JobId"]
            print("el job id es:", job_id)
        
            columnas_por_pagina=process_response(job_id)
            
            
            translated_columnas_por_pagina = translate_content(columnas_por_pagina)
            
            with open("/tmp/file.txt", "w") as f:
                for page_number, page_content in translated_columnas_por_pagina.items():
                    content = page_content['Content']
                    f.write(f"Page {page_number}:\n{content}\n\n")
            s3_response = s3.upload_file("/tmp/file.txt", bucket_name, "resultados-textract/" + job_id + ".txt")

            return {"statusCode": 200, "body": json.dumps("File uploaded successfully!")}
            
        else:
            print("El estado del trabajo no es 'SUCCEEDED'. Estado actual:", message['Status'])
            return {"statusCode": 400, "body": json.dumps("Error: Job status is not 'SUCCEEDED'")}
        
    except Exception as e:
        print("Se produjo una excepción:", e)
        return {"statusCode": 500, "body": json.dumps("Error: An unexpected error occurred")}

def process_response(job_id):
    """
    Procesa la respuesta de Textract para obtener el texto detectado en las diferentes páginas del documento.

    Parámetros:
    - job_id: Identificador del trabajo de Textract.

    Devuelve:
    - Diccionario con el número de página y el contenido de texto detectado en cada página.
    """
    pages = []

    next_token = None

    response = textract.get_document_text_detection(JobId=job_id)
    pages.append(response)
    
    if "NextToken" in response:
        nextToken = response["NextToken"]

    while nextToken:
        response = textract.get_document_text_detection(
            JobId=job_id, NextToken=nextToken
        )
        pages.append(response)
        nextToken = None
        if "NextToken" in response:
            nextToken = response["NextToken"]

    columnas_por_pagina  = {}
    
    for page in pages:
        for item in page["Blocks"]:
            if item["BlockType"] == "LINE":
                left = item["Geometry"]["BoundingBox"]["Left"]
                
                if left < 0.5:  
                    columna = "izquierda"
                else:
                    columna = "derecha"
                
                page_number = item["Page"]
                
                if page_number not in columnas_por_pagina:
                    columnas_por_pagina[page_number] = {"izquierda": [], "derecha": []}
                columnas_por_pagina[page_number][columna].append(item["Text"])

    combined_text = combinar_columnas(columnas_por_pagina)
    
    extracted_text = {}
    
    for page_number, text in combined_text.items():
        extracted_text[page_number] = {
            "Number": page_number,
            "Content": "".join(text)
        }

    return extracted_text
    
def combinar_columnas(columnas_por_pagina):
    """
    Combina las columnas de texto de cada página. Útil para cuando el documento está dividido en dos columnas

    Parámetros:
    - columnas_por_pagina: Diccionario con el contenido de las páginas.

    Devuelve:
    - Diccionario con el texto combinado de cada página.
    """
    texto_combinado = {}
    for pagina, columnas in columnas_por_pagina.items():
        texto_izquierda = columnas['izquierda']
        texto_derecha = columnas['derecha']
        texto_combinado[pagina] = texto_izquierda + texto_derecha
    return texto_combinado

