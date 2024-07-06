"""
Este módulo interactúa con Google Cloud Firestore y Storage para manejar solicitudes de webhook de Dialogflow,
procesando comandos basados en intenciones y gestionando flujos de conversación en un chatbot. Las funciones
incluidas manejan la extracción y procesamiento de texto, detectan intenciones, y devuelven respuestas apropiadas
según la lógica del chatbot.

El flujo general de la función incluye la recepción de una solicitud de Dialogflow, el procesamiento de la
intención especificada en la solicitud, la ejecución de acciones como la lectura de texto de Cloud Storage,
la traducción de texto y la recuperación de respuestas de Firestore. Además, se proporcionan funcionalidades para
administrar los pasos de un tutorial interactivo dentro del chatbot.

Funciones:
- dialogflow_webhook: Procesa la solicitud de Dialogflow y determina la acción a tomar basada en la intención del usuario.
- start_tutorial: Inicia un tutorial interactivo configurando atributos iniciales de la sesión.
- handle_step: Avanza a través de los pasos de un tutorial basado en la sesión actual y los atributos almacenados.
- get_step_content: Recupera contenido específico de un paso de Firestore.
- handle_question: Responde a preguntas específicas basadas en la intención y el contexto del usuario.
- get_most_similar_response: Busca en Firestore la respuesta más adecuada a la pregunta del usuario.
- calculate_similarity: Calcula la similitud entre la entrada del usuario y las preguntas almacenadas para determinar la mejor respuesta.
- build_response: Construye y devuelve una respuesta formateada para Dialogflow.
- read_text_from_file: Lee el contenido de un archivo de texto almacenado en Cloud Storage.

Este módulo es esencial para la operación eficiente de un chatbot interactivo que utiliza Dialogflow y Google Cloud
Services para manejar y responder a las interacciones del usuario.
"""
import os
import json
from google.cloud import storage, firestore

storage_client = storage.Client()
db = firestore.Client()

bucket_name = os.environ['bucket_name']
folder_name = os.environ['folder_name']

def dialogflow_webhook(request):
    """
    Función principal que maneja las solicitudes entrantes de Dialogflow.

    Parámetros:
    - request: La solicitud HTTP que contiene el evento desencadenado por Dialogflow.

    Retorna:
    - Una respuesta HTTP con el mensaje apropiado basado en la intención del usuario.
    """
    request_json = request.get_json()

    if request_json and 'queryResult' in request_json:
        intent_list = ['CreacionStorage', 'DocumentAI', 'CloudFunctions', 'DialogflowES', 'CreacionTask', 'IdeaTrabajo','QueHace','Objetivos','ConceptosTeoricos','TecnicasHerramientas','TrabajosRelacionados','Conclusiones','LineasFuturas','GitHubInfo','EstructuraMemoria','Metodologias','ServiciosAWS','Sprints']
        intent_name = request_json['queryResult']['intent']['displayName']
        session = request_json['session']
        
        output_contexts = request_json['queryResult'].get('outputContexts', [])
       
        if output_contexts and 'parameters' in output_contexts[0]:
            session_attributes = output_contexts[0]['parameters']
        else:
            session_attributes = {}

        if intent_name == 'StartTutorial':
            return start_tutorial(session)
        if intent_name == 'NextStep':
            return handle_step(session_attributes, session, next_step=True)
        if intent_name == 'GoToStep':
            return handle_step(session_attributes, session, next_step=False)
        if intent_name in intent_list:
            user_input = request_json['queryResult']['queryText']
            return handle_question(intent_name,session_attributes,user_input, session)
        
        message = "No puedo manejar esa solicitud en este momento."
        return build_response(message, session, session_attributes)


def start_tutorial(session):
    """
    Inicia el tutorial configurando los atributos iniciales de la sesión y devolviendo un mensaje de bienvenida.

    Parámetros:
    - session: La sesión de Dialogflow.

    Retorna:
    - Un diccionario con el mensaje de bienvenida y los atributos de la sesión inicializados.
    """
    session_attributes = {'step': 0}

    message = """Te voy a enseñar paso a paso a crear un chatbot. 
        Lo primero de todo que tienes que hacer para poder empezar a trabajar con los servicios de Google cloud y crear el entorno es: Crear un proyecto nuevo. Es muy sencillo, nada mas entrar en la consola te aparece la opción.
        Muy importante: Guarda el ID del proyecto, es posible que lo necesites más adelante si quieres configurarte tu entorno virtual. ¿Empezamos?
        """  
    return build_response(message, session, session_attributes)

def handle_step(session_attributes, session, next_step):
    """
    Maneja la lógica para avanzar al siguiente paso o ir a un paso específico del tutorial.

    Parámetros:
    - session_attributes: Los atributos actuales de la sesión.
    - session: La sesión actual de Dialogflow.
    - next_step: Booleano que indica si se debe avanzar al siguiente paso o ir a un paso específico.

    Retorna:
    - Un diccionario con el mensaje del paso o subpaso correspondiente y los atributos de la sesión actualizados.
    """
    step_substep = {0: 1, 1: 1, 2: 2, 3: 5, 4: 3, 5: 3, 6: 1}

    if next_step:
        step = int(session_attributes.get('step', 0))
    else:
        step = int(session_attributes.get('stepNumber', 1))
        session_attributes['step'] = step
        if step < 1 or step > 6:
            message = "Lo siento, el paso especificado no es válido. Por favor, elige un paso entre 1 y 7."
            return build_response([message], session, session_attributes)

    response_messages = []

    for substep in range(step_substep.get(step, 1)):
        file_name = get_step_content(step, substep)
        text = read_text_from_file(file_name)
        response_messages.append(text)

    session_attributes['step'] = step + 1

    return build_response(response_messages, session, session_attributes)

def get_step_content(step, substep):
    """
    Obtiene el contenido del paso y subpaso actuales desde Firestore.

    Parámetros:
    - step: El paso actual del tutorial.
    - substep: El subpaso actual dentro del paso.

    Retorna:
    - El contenido correspondiente al paso y subpaso desde Firestore, o un mensaje de error si no se encuentra el contenido.
    """
    try:
        doc_ref = db.collection("chatbotsteps").document(f"{step}_{substep}")
        doc = doc_ref.get()
        if not doc.exists:
            return "No se encontró contenido para este paso y subpaso."
        return doc.to_dict().get('Response', "No se encontró contenido para este paso y subpaso.")
    except Exception as e:
        print(f"Error al obtener contenido desde Firestore: {e}")
        return "Ocurrió un error al obtener el contenido del paso."


def handle_question(intent_name, session_attributes, user_input, session):
    """
    Maneja las preguntas específicas del usuario durante el tutorial.

    Parámetros:
    - intent_name: El nombre de la intención que contiene la pregunta.
    - session_attributes: Los atributos de la sesión actuales.
    - user_input: La pregunta realizada por el usuario.

    Retorna:
    - Un diccionario con la respuesta a la pregunta del usuario y los atributos de la sesión.
    """
    response_message = get_most_similar_response(intent_name, user_input)
    return build_response(response_message, session, session_attributes)

def get_most_similar_response(intent_name, user_input):
    """
    Busca la respuesta más similar a la pregunta del usuario en Firestore.

    Parámetros:
    - intent_name: El nombre de la intención que contiene la pregunta.
    - user_input: La pregunta realizada por el usuario.

    Retorna:
    - La respuesta más similar encontrada en Firestore o un mensaje de error si no se encuentra una respuesta.
    """
    try:
        docs = db.collection("chatbotresponses").where('IntentName', '==', intent_name).stream()

        max_similarity = -1
        best_response = "Lo siento, no tengo la respuesta a esa pregunta en este momento."
        for doc in docs:
            item = doc.to_dict()
            similarity = calculate_similarity(user_input, item['Question'])
            if similarity > max_similarity:
                max_similarity = similarity
                best_response = item['Response']
        
        return best_response

    except Exception as e:
        print(f"Error al obtener la respuesta desde Firestore: {e}")
        return "Lo siento, ocurrió un error al procesar tu solicitud."

def calculate_similarity(user_input, stored_question):
    """
    Calcula la similitud entre la pregunta del usuario y las preguntas almacenadas.

    Parámetros:
    - user_input: La pregunta realizada por el usuario.
    - stored_question: La pregunta almacenada en Firestore.

    Retorna:
    - Un valor de similitud basado en la cantidad de palabras comunes entre las preguntas.
    """
    user_words = set(user_input.lower().split())
    question_words = set(stored_question.lower().split())
    common_words = user_words.intersection(question_words)
    return len(common_words) / max(len(user_words), len(question_words))

def build_response(messages, session, session_attributes):
    """
    Construye la respuesta en el formato esperado por Dialogflow.

    Parámetros:
    - message: El mensaje de respuesta.
    - session: La sesión actual de Dialogflow.
    - session_attributes: Los atributos de la sesión actuales.

    Retorna:
    - Un diccionario con la estructura de respuesta esperada por Dialogflow.
    """
    context_name = f"{session}/contexts/session_attributes"
    if isinstance(messages, str):
        messages = [messages]
    fulfillment_messages = [
        {
            "text": {
                "text": [message]
            }
        } for message in messages
    ]
    
    response = {
        "fulfillmentMessages": fulfillment_messages,
        "outputContexts": [
            {
                "name": context_name,
                "lifespanCount": 5,
                "parameters": session_attributes
            }
        ]
    }
    return json.dumps(response), 200, {'Content-Type': 'application/json'}

def read_text_from_file(file_name):
    """
    Lee el contenido de un archivo de texto almacenado en Google Cloud Storage.

    Parámetros:
    - file_name: El nombre del archivo de texto en Google Cloud Storage.

    Retorna:
    - El contenido del archivo de texto o un mensaje de error si no se puede leer el archivo.
    """
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(f"{folder_name}/{file_name}")
        text = blob.download_as_text()
        print(text)
        return text
    except Exception as e:
        print(f"Error al leer el archivo desde Google Cloud Storage: {e}")
        return "Ocurrió un error al leer el archivo desde Google Cloud Storage."
    