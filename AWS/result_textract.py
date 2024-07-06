"""
Este módulo facilita la interacción con varios servicios de AWS para procesar y traducir documentos.
Utiliza AWS Comprehend para detectar el idioma de un texto, AWS Translate para traducir texto de un idioma a otro,
y AWS Textract para extraer texto de documentos almacenados en S3. Las funciones están diseñadas para ser
invocadas a través de AWS Lambda, lo que permite un procesamiento automático y escalable de documentos.

Funciones:
- detect_language: Detecta el idioma predominante en un texto dado.
- translate_content: Traduce el texto a español si no está ya en ese idioma.
- lambda_handler: Función principal de Lambda que maneja los eventos de SNS para el procesamiento de documentos.
- process_response: Procesa la salida de Textract para extraer texto de documentos.
- combinar_columnas: Combina el texto de dos columnas para documentos que están formateados en dos columnas.

Estas funcionalidades están integradas en un flujo de trabajo que detecta el idioma de un documento, traduce su contenido
si es necesario y maneja la estructura del documento para facilitar una presentación adecuada del texto traducido.

"""
import os
import json
import boto3

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

def translate_content(text):
    """
    Traduce el contenido de las páginas si está mayoritariamente en inglés.

    Parámetros:
    - columnas_por_pagina: Diccionario con el contenido de las páginas.

    Devuelve:
    - Diccionario con el contenido traducido.
    - En caso de error, se maneja la excepción y se eleva.
    """
    try:
        language_code=detect_language(text)
        if language_code != 'es':
            translation_response = translate.translate_text(
                Text=text,
                SourceLanguageCode=language_code,
                TargetLanguageCode='es'
            )
            translated_text = translation_response['TranslatedText']
            return translated_text
        return text

    except Exception as e:
        print("Error al traducir el texto: ", e)

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
        
            extracted_text=process_response(job_id)
            
            es_text = translate_content(extracted_text)
            
            with open("/tmp/file.txt", "w", encoding="utf-8") as f:
                f.write(es_text)
                
            s3.upload_file("/tmp/file.txt", bucket_name, "resultados-textract/" + job_id + ".txt")

            return {"statusCode": 200, "body": json.dumps("File uploaded successfully!")}
            
        
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
        next_token = response["NextToken"]

    while next_token:
        response = textract.get_document_text_detection(
            JobId=job_id, NextToken=next_token
        )
        pages.append(response)
        next_token = None
        if "NextToken" in response:
            next_token = response["NextToken"]

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
       
    extracted_text = " ".join(combined_text).replace("&&n", "\n")
        
    return extracted_text
    
def combinar_columnas(columnas_por_pagina):
    """
    Combina las columnas de texto de cada página. Útil para cuando el documento está dividido en dos columnas

    Parámetros:
    - columnas_por_pagina: Diccionario con el contenido de las páginas.

    Devuelve:
    - Lista con el texto combinado de cada página, junto en una lista.
    """
    texto_listas = []
    for _, columnas in columnas_por_pagina.items():
        texto_izquierda = columnas['izquierda']
        texto_derecha = columnas['derecha']
        
        texto_listas.extend(texto_izquierda + texto_derecha)
        

    return texto_listas
