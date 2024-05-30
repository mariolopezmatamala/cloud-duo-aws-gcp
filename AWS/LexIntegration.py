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
    elif intent_name == 'GoToStep':
        return goToStep(event)
    elif intent_name == 'AskQuestion':
        return handleQuestion(event)
    
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

def goToStep(event):
    session_attributes = event['sessionState'].get('sessionAttributes', {})
    step = int(event['sessionState']['intent']['slots']['StepNumber']['value']['interpretedValue'])
    
    if step < 1 or step > 4:
        message = "Lo siento, el paso especificado no es válido. Por favor, elige un paso entre 1 y 4."
        return build_response(message, session_attributes, 'GoToStep')
    
    session_attributes['step'] = step
    session_attributes['substep'] = 1
    
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

def handleQuestion(event):
    session_attributes = event['sessionState'].get('sessionAttributes', {})
    step = int(session_attributes.get('step', 1))
    question = event['inputTranscript'].lower()
    value = event['sessionState']['intent']['slots']['Question']['value']['resolvedValues'][0]
    
    if value == 'IAM' and step == 1:
        response = handleQuestionIAM(question)
    elif step == 'S3' and step == 2:
        response = handleQuestionS3(question)
    elif step == 'SNS' and step == 3:
        response = handleQuestionSNS(question)
    elif step == 'Lambda' and step == 4:
        response = handleQuestionLambda(question)
    else: response = "Haz una pregunta correspondiente al paso en el que estamos, no te adelantes."
    return build_response(response, session_attributes, 'AskQuestion')

def handleQuestionIAM(question):
    phrases_list = [
        "qué es", 
        "explícame", 
        "para qué sirve", 
        "quiero saber sobre", 
        "definición de", 
        "qué significa"
    ]
    if any(phrase in question for phrase in phrases_list):
        return "Un rol IAM es una entidad que define un conjunto de permisos para realizar acciones en AWS. Un rol no está asociado a un usuario o grupo específico y puede ser asumido por cualquier entidad que necesite los permisos definidos."
    elif "creo" in question:
        return "Para crear un rol en IAM, accede al servicio IAM en la consola de AWS, selecciona 'Roles' y haz clic en 'Create role'. Luego, sigue los pasos para definir la entidad de confianza y asignar permisos."
    else:
        return "No tengo información sobre esa pregunta específica en este paso. Por favor, pregunta algo relacionado con la creación del rol IAM."

def handleQuestionS3(question):
    phrases_list = [
        "qué es", 
        "explícame", 
        "para qué sirve", 
        "quiero saber sobre", 
        "definición de", 
        "qué significa"
    ]
    if any(phrase in question for phrase in phrases_list):
        return "Un bucket S3 es un contenedor de objetos en Amazon S3 (Simple Storage Service). Puedes almacenar cualquier número de objetos en un bucket."
    elif "creo" in question:
        return "Para crear un bucket en S3, accede al servicio Amazon S3 en la consola de AWS, haz clic en 'Create bucket', elige un nombre único y configura las opciones según tus necesidades."
    elif "carpetas" in question:
        return "Las carpetas en S3 son una manera de organizar los objetos dentro de un bucket. Aunque S3 es un almacenamiento plano, las carpetas se utilizan para simular una estructura jerárquica."
    elif "creo carpetas" in question:
        return "Para crear carpetas en S3, accede a tu bucket, selecciona 'Create folder', ingresa el nombre de la carpeta y guarda los cambios."
    elif "configuración más segura" in question:
        return "La configuración más segura para un bucket S3 implica habilitar el cifrado de objetos, restringir el acceso público, habilitar el registro de acceso y aplicar políticas de acceso específicas."
    else:
        return "No tengo información sobre esa pregunta específica en este paso. Por favor, pregunta algo relacionado con la creación del bucket S3."

def handleQuestionSNS(question):
    phrases_list = [
        "qué es", 
        "explícame", 
        "para qué sirve", 
        "quiero saber sobre", 
        "definición de", 
        "qué significa"
    ]
    if any(phrase in question for phrase in phrases_list):
        return "SNS (Simple Notification Service) es un servicio de mensajería de AWS que coordina y administra la entrega o el envío de notificaciones a suscriptores o endpoints."
    elif "creo" in question:
        return "Para crear un tema en SNS, accede al servicio SNS en la consola de AWS, haz clic en 'Create topic', elige un nombre y tipo de tema, y configura las opciones."
    elif "tema estándar" in question:
        return "Un tema estándar en SNS permite el envío de mensajes a múltiples suscriptores con un mecanismo de entrega 'al menos una vez' (at least once) y sin orden de entrega garantizado."
    elif "endpoint" in question:
        return "Un endpoint en SNS es un destino al que se envían los mensajes, como una dirección de correo electrónico, un número de teléfono (para SMS) o una URL HTTP/S."
    elif "suscribir los endpoints a un tema" in question:
        return "Para suscribir endpoints a un tema de SNS, accede al tema, selecciona 'Create subscription', elige el protocolo (email, SMS, HTTP, etc.) y proporciona el endpoint."
    else:
        return "No tengo información sobre esa pregunta específica en este paso. Por favor, pregunta algo relacionado con la creación de un tema en SNS."

def handleQuestionLambda(question):
    phrases_list = [
        "qué es", 
        "explícame", 
        "para qué sirve", 
        "quiero saber sobre", 
        "definición de", 
        "qué significa"
    ]
    
    if any(phrase in question for phrase in phrases_list):
        return "AWS Lambda es un servicio de computación sin servidor que ejecuta código en respuesta a eventos y administra automáticamente los recursos de computación."
    elif "creo" in question:
        return "Para crear una función Lambda, accede al servicio Lambda en la consola de AWS, haz clic en 'Create function', elige crear desde cero, proporciona un nombre y elige el tiempo de ejecución (como Python), luego configura los permisos."
    elif "desencadenador" in question:
        return "Un desencadenador (trigger) es una fuente de eventos que invoca la función Lambda. Puede ser un bucket S3, un tema SNS, una tabla DynamoDB, entre otros."
    elif "configurar un desencadenador s3" in question:
        return "Para configurar un desencadenador S3, accede a la función Lambda, selecciona 'Add trigger', elige S3, especifica el bucket y los filtros de prefijo y sufijo, y guarda los cambios."
    elif "tiempo de espera" in question:
        return "El tiempo de espera (timeout) en Lambda define el tiempo máximo que una función puede ejecutarse antes de ser terminada por el servicio. Puedes configurar este tiempo según las necesidades de tu función."
    else:
        return "No tengo información sobre esa pregunta específica en este paso. Por favor, pregunta algo relacionado con la creación de las funciones Lambda."

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
