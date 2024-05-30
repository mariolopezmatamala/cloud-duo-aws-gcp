import json
import boto3
import os

s3 = boto3.client('s3')
bucket_name = os.environ['bucket_name']
folder_name = os.environ['folder_name']

def lambda_handler(event, context):
    intent_name = event['sessionState']['intent']['name']
            
    print(event)
    print(context)
    
    if intent_name == 'StartTutorial':
        return startTutorial()
    elif intent_name == 'NextStep':
        return nextStep(event)
    elif intent_name=='RepeatStep':
        return currentStep(event)
    
def startTutorial():
    session_attributes = {'step':0,'substep':1}

    print("hola",session_attributes)
    message = """Te voy a ayudar a crear un chatBot. Estos van a ser los pasos, si quieres puedes ir a uno en concreto. 
        1 - Configuración del rol IAM.
        2 - Creación del bucket
        3 - Configuración de la notificación
        4 - Creación de las funciones lambda
    Además, siempre puedes hacerme alguna pregunta acerca del paso en el que estemos. ¿Estás preparado?"""
    return build_response(message,session_attributes,'StartTutorial')

def nextStep(event):
    step_substep = {0: 1, 1: 2, 2: 1, 3: 1, 4: 4}
    session_attributes = event['sessionState'].get('sessionAttributes', {})
    step = int(session_attributes.get('step', 1))
    substep = int(session_attributes.get('substep', 1))
    
    if substep == step_substep.get(step, 0):
        step += 1  
        substep = 1  
    else:
        substep += 1  

    session_attributes['step'] = step
    session_attributes['substep'] = substep
    
    if step == 1:
        return rol_IAM(session_attributes)
    elif step == 2:
        return bucket_S3(session_attributes)
    elif step == 3:
        return create_SNS(session_attributes)
    elif step == 4:
        return create_lambda_functions(session_attributes)
    else:
        return finTutorial()

def currentStep(event):
    session_attributes = event['sessionState'].get('sessionAttributes', {})
    step = int(session_attributes.get('step', 1))
    substep = int(session_attributes.get('substep', 1))
    
    if step == 1:
        return rol_IAM(session_attributes)
    elif step == 2:
        return bucket_S3(session_attributes)
    elif step == 3:
        return create_SNS(session_attributes)
    elif step == 4:
        return create_lambda_functions(session_attributes) 

def rol_IAM(session_attributes):    
   
    substep = int(session_attributes.get('substep', 1))
    
    if substep == 1:
        message = read_text_file_from_s3("Paso1Subpaso1.txt")
        return build_response(message,session_attributes,'NextStep')
        
    elif substep == 2:
            
        message = read_text_file_from_s3("Paso1Subpaso2.txt")
        return build_response(message,session_attributes,'NextStep')

def bucket_S3(session_attributes):
    message = read_text_file_from_s3("Paso2Subpaso1.txt")
    
    return build_response(message,session_attributes,'NextStep')

def create_SNS(session_attributes):
    message = read_text_file_from_s3("Paso3Subpaso1.txt")
    return build_response(message, session_attributes, 'NextStep') 
    
def create_lambda_functions(session_attributes):
    substep = int(session_attributes.get('substep', 1))

    if substep == 1:
        message = read_text_file_from_s3("Paso4Subpaso1.txt")
        
        return build_response(message, session_attributes, 'NextStep')

    elif substep == 2:
        message = read_text_file_from_s3("Paso4Subpaso2.txt")
        
        return build_response(message, session_attributes, 'NextStep')

    elif substep == 3:
        message = read_text_file_from_s3("Paso4Subpaso3.txt")
        
        return build_response(message, session_attributes, 'NextStep')

    elif substep == 4:
        message = read_text_file_from_s3("Paso4Subpaso4.txt")        
        return build_response(message, session_attributes, 'NextStep')

def finTutorial():
    message = "Enhorabuena, has creado un chatbot"
    return build_response(message, {}, 'NextStep')

def read_text_file_from_s3(file_name):
    
    try:
        response = s3.get_object(Bucket=bucket_name, Key=f"{folder_name}/{file_name}")
        text = response['Body'].read().decode('utf-8')
        print(text)
        return text
    except Exception as e:
        print(f"Error al leer el archivo desde S3: {e}")
        return None

def build_response(message, session_attributes, intent_name,content_type='CustomPayload'):
    response = {
        "sessionState": {
            "dialogAction": {
                "type": "Close"
            },
            "sessionAttributes": session_attributes,
            "intent": {
                'name': intent_name,
                'state': 'Fulfilled'
            }
        },
        "messages": [
            {
                "contentType": content_type,
                "content": message
            }
        ]
    }
    return response
