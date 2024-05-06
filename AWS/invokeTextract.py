import boto3
import botocore
from botocore.exceptions import ClientError
from logging import exception
import os

SNSTopicArn=os.environ['SNSTopicArn']
roleArn=os.environ['roleArn']

def StartTextractDocumentAnalysis(s3_bucket, s3_key):
    """
    Inicia el análisis de un documento utilizando AWS Textract.

    Parámetros:
    - s3_bucket: Nombre del bucket de S3 donde se encuentra el documento.
    - s3_key: Clave del objeto en el bucket de S3 que apunta al documento.

    Devuelve:
    - Devuelve el ID del trabajo de Textract si se inicia correctamente.
    - En caso de error durante el inicio del análisis, devuelve False.
    """
    
    textract_client = boto3.client('textract')
    try:
        response = textract_client.start_document_text_detection(
            DocumentLocation={
                'S3Object': {
                    'Bucket': s3_bucket,
                    'Name': s3_key
                }
            },
            NotificationChannel={"SNSTopicArn": SNSTopicArn, "RoleArn": roleArn},
        )
        print(response)
        
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print('Start Job Id: ' + response['JobId'])
            return response['JobId']
        else:
            print("No se pudo obtener el ID del trabajo de Textract.")
            return False
            
    except Exception as e :
        print("Exception happend message is: ", e)
        return False
   

def lambda_handler(event, context):
    """
    Función principal que maneja el evento y desencadena el inicio del análisis de Textract.

    Parámetros:
    - event: El evento que desencadenó la invocación de la función Lambda.
    - context: El contexto de la función Lambda que proporciona información sobre la ejecución y el entorno.

    Devuelve:
    - Devuelve el ID del trabajo de Textract si el análisis se inicia con éxito.
    - En caso de error durante el inicio del análisis, devuelve False.
    """
    print("event collected is {}".format(event))
    
    for record in event['Records']:
        s3_bucket = record['s3']['bucket']['name']
        print("Bucket name is {}".format(s3_bucket))
        
        s3_key = record['s3']['object']['key']
        print("Bucket key name is {}".format(s3_key))
        from_path = "s3://{}/{}".format(s3_bucket, s3_key)
        print("from path {}".format(from_path))
        
        job_id = StartTextractDocumentAnalysis(s3_bucket, s3_key)
        if job_id:
            print("Job ID returned: {}".format(job_id))
            return job_id
        else:
            return False