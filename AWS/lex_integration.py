"""
Este módulo implementa una función AWS Lambda diseñada para interactuar con AWS Lex, DynamoDB y S3.
Su objetivo principal es gestionar una serie de tutoriales interactivos relacionados con AWS, permitiendo
a los usuarios avanzar a través de diferentes pasos de un tutorial, responder preguntas específicas, y
recuperar información relevante almacenada tanto en S3 como en DynamoDB.

El módulo define una función principal `lambda_handler` que procesa eventos entrantes de Lex y gestiona
la lógica de decisión basada en la intención del usuario. Adicionalmente, incluye funciones auxiliares
para manejar pasos específicos del tutorial, buscar y entregar respuestas basadas en la similitud del contenido,
y leer documentos directamente desde un bucket de S3.

Características:
- Manejo de sesiones y pasos de tutoriales mediante atributos de sesión en Lex.
- Consulta a DynamoDB para obtener respuestas a preguntas y contenido de tutorial.
- Recuperación de archivos de texto desde S3 para proporcionar contenido detallado de los tutoriales.
- Gestión de errores y excepciones para asegurar la estabilidad de la función Lambda en escenarios de error.

Este módulo es parte de un sistema más grande diseñado para educar y asistir a los usuarios en el uso de
servicios AWS a través de un chatbot interactivo.
"""
import os
import boto3

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ChatbotResponses')
bucket_name = os.environ['bucket_name']
folder_name = os.environ['folder_name']


def lambda_handler(event, context):
    """
    Función principal de la Lambda que maneja las solicitudes entrantes de Lex.
    
    Parámetros:
    - event: El evento desencadenado por Lex, contiene detalles como la intención y los atributos de la sesión.
    - context: Contexto de la ejecución de la Lambda.

    Retorna:
    - Un diccionario con la respuesta apropiada basada en la intención del usuario.
    """
    intent_list = ['CreacionRolIAM', 'CreacionBucketS3', 'CrearSNS', 'CrearFuncionLambda', 'ExplicacionFuncionesLambda', 'Textract', 'ComprehendTranslate', 'Lex','IdeaTrabajo','QueHace','Objetivos','ConceptosTeoricos','TecnicasHerramientas','TrabajosRelacionados','Conclusiones','LineasFuturas','GitHubInfo','EstructuraMemoria','Metodologias','ServiciosAWS','Sprints']
    intent_name = event['sessionState']['intent']['name']
    session_attributes = event["sessionState"]["sessionAttributes"]

    if intent_name == 'StartTutorial':
        return start_tutorial()
    if intent_name == 'NextStep':
        return handle_step(event, next_step=True)
    if intent_name == 'GoToStep':
        return handle_step(event, next_step=False)
    if intent_name in intent_list:
        return handle_question(event)

    message = "No puedo manejar esa solicitud en este momento."
    return build_response([{'contentType': 'PlainText', 'content': message}], session_attributes, intent_name)
    
def start_tutorial():
    """
    Inicia el tutorial configurando los atributos iniciales de la sesión y devolviendo un mensaje de bienvenida.

    Parámetros:
    - Ninguno.

    Retorna:
    - Un diccionario con el mensaje de bienvenida y los atributos de la sesión inicializados.
    """
    session_attributes = {'step': 1}

    message = """Te voy a ayudar a crear un chatBot. Estos van a ser los pasos, si quieres puedes ir a uno de los pasos en concreto:
        1 - Creación del rol IAM.
        2 - Creación del bucket
        3 - Configuración de la notificación
        4 - Creación de las funciones lambda
        5 - Creación base de datos
        6 - Creación del bot
    Además, a lo largo del tutorial siempre puedes hacerme alguna pregunta. ¿Estás preparado?"""
    return build_response([{'contentType': 'CustomPayload', 'content': message}], session_attributes, 'StartTutorial')

def handle_step(event, next_step):
    """
    Maneja la lógica para avanzar al siguiente paso o ir a un paso específico del tutorial.

    Parámetros:
    - event: El evento desencadenado por Lex que contiene los atributos de la sesión.
    - next_step: Booleano que indica si se debe avanzar al siguiente paso o ir a un paso específico.

    Retorna:
    - Un diccionario con el mensaje del paso o subpaso correspondiente y los atributos de la sesión actualizados.
    """
    step_substep = {0: 1, 1: 2, 2: 1, 3: 1, 4: 5, 5: 2, 6: 3, 7: 1}
    session_attributes = event['sessionState'].get('sessionAttributes', {})
    
    if next_step:
        step = int(session_attributes.get('step', 0))
    else:
        step = int(event['sessionState']['intent']['slots']['StepNumber']['value']['interpretedValue'])
        session_attributes['step'] = step
        if step < 1 or step > 7:
            message = "Lo siento, el paso especificado no es válido. Por favor, elige un paso entre 1 y 7."
            return build_response([{'contentType': 'PlainText', 'content': message}], session_attributes, 'GoToStep')
    
    response = []
    
    for substep in range(1, step_substep.get(step, 1) + 1):
        file_name = get_step_content(step, substep)
        texto = read_text_file_from_s3(file_name)
        mensaje = {
            'contentType': 'CustomPayload',
            'content': texto
        }
        response.append(mensaje)
    
    session_attributes['step'] = step + 1
    
    return build_response(response, session_attributes, 'NextStep' if next_step else 'GoToStep')


def get_step_content(step, substep):
    """
    Obtiene el fichero contenido a través del paso y subpaso actuales desde DynamoDB.

    Parámetros:
    - step: El paso actual del tutorial.
    - substep: El subpaso actual dentro del paso.

    Retorna:
    - El nombre del fichero correspondiente al paso y subpaso desde DynamoDB, o un mensaje de error si no se encuentra el contenido.
    """
    try:
        key = f"{step}_{substep}"
        response = table.get_item(Key={'IntentName': 'tutorial', 'Question': key})
        item = response.get('Item')
        if not item:
            return "No se encontró contenido para este paso y subpaso."
        return item['Response']
    except Exception as e:
        print(f"Error al obtener contenido desde DynamoDB: {e}")
        return "Ocurrió un error al obtener el contenido del paso."

def handle_question(event):
    """
    Maneja las preguntas específicas del usuario durante el tutorial.

    Parámetros:
    - event: El evento desencadenado por Lex que contiene los atributos de la sesión y la pregunta del usuario.

    Retorna:
    - Un diccionario con la respuesta a la pregunta del usuario y los atributos de la sesión.
    """
    intent_name = event['sessionState']['intent']['name']
    user_input = event['inputTranscript']
    session_attributes = event['sessionState'].get('sessionAttributes', {})
    
    response_message = get_most_similar_response(intent_name, user_input)
    response = [
        {
            'contentType' : 'CustomPayload',
            'content' : response_message
        }
    ]
    
    return build_response(response, session_attributes, intent_name)

def get_most_similar_response(intent_name, user_input):
    """
    Busca la respuesta más similar a la pregunta del usuario en DynamoDB.

    Parámetros:
    - intent_name: El nombre de la intención que contiene la pregunta.
    - user_input: La pregunta realizada por el usuario.

    Retorna:
    - La respuesta más similar encontrada en DynamoDB o un mensaje de error si no se encuentra una respuesta.
    """
    try:
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('IntentName').eq(intent_name)
        )

        items = response.get('Items', [])
        if not items:
            return "Lo siento, no tengo la respuesta a esa pregunta en este momento."
        
        max_similarity = -1
        best_response = "Lo siento, no tengo la respuesta a esa pregunta en este momento."
        for item in items:
            similarity = calculate_similarity(user_input, item['Question'])
            if similarity > max_similarity:
                max_similarity = similarity
                best_response = item['Response']
        
        return best_response

    except Exception as e:
        print(f"Error al obtener la respuesta desde DynamoDB: {e}")
        return "Lo siento, ocurrió un error al procesar tu solicitud."

def calculate_similarity(user_input, stored_question):
    """
    Calcula la similitud entre la pregunta del usuario y las preguntas almacenadas.

    Parámetros:
    - user_input: La pregunta realizada por el usuario.
    - stored_question: La pregunta almacenada en DynamoDB.

    Retorna:
    - Un valor de similitud basado en la cantidad de palabras comunes entre las preguntas.
    """
    user_words = set(user_input.lower().split())
    question_words = set(stored_question.lower().split())
    common_words = user_words.intersection(question_words)
    return len(common_words) / max(len(user_words), len(question_words))

def build_response(messages, session_attributes, intent_name):
    """
    Construye la respuesta en el formato esperado por Lex.

    Parámetros:
    - message: El mensaje de respuesta.
    - session_attributes: Los atributos de la sesión actuales.
    - intent_name: El nombre de la intención actual.
    - content_type: El tipo de contenido del mensaje (por defecto es 'CustomPayload').

    Retorna:
    - Un diccionario con la estructura de respuesta esperada por Lex.
    """
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
        "messages": messages
    }
    return response

def read_text_file_from_s3(file_name):
    """
    Lee el contenido de un archivo de texto almacenado en S3.

    Parámetros:
    - file_name: El nombre del archivo de texto en S3.

    Retorna:
    - El contenido del archivo de texto o un mensaje de error si no se puede leer el archivo.
    """
    try:
        response = s3.get_object(Bucket=bucket_name, Key=f"{folder_name}/{file_name}")
        text = response['Body'].read().decode('utf-8')
        print(text)
        return text
    except Exception as e:
        print(f"Error al leer el archivo desde S3: {e}")
        return None
