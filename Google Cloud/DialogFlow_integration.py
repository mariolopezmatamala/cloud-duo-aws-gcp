import json
from google.cloud import storage, firestore
import os

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
        intent_name = request_json['queryResult']['intent']['displayName']
        session = request_json['session']
        
        output_contexts = request_json['queryResult'].get('outputContexts', [])
       
        if output_contexts and 'parameters' in output_contexts[0]:
            session_attributes = output_contexts[0]['parameters']
        else:
            session_attributes = {}

        if intent_name == 'StartTutorial':
            return start_tutorial(session)
        elif intent_name == 'NextStep':
            return next_step(session_attributes, session)
        elif intent_name == 'RepeatStep':
            return current_step(session_attributes, session)
        elif intent_name == 'GoToStep':
            return go_to_step(session_attributes, session)
        else:
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
    session_attributes = {
        'step': 0,
        'substep': 1
    }

    message = """Te voy a enseñar paso a paso a crear un chatbot. 
        Lo primero de todo que tienes que hacer para poder empezar a trabajar con los servicios de Google cloud y crear el entorno es: Crear un proyecto nuevo. Es muy sencillo, nada mas entrar en la consola te aparece la opción.
        Muy importante: Guarda el ID del proyecto, es posible que lo necesites más adelante si quieres configurarte tu entorno virtual. ¿Empezamos?
        """  
    return build_response(message, session, session_attributes)



def next_step(session_attributes, session):
    """
    Avanza al siguiente paso o subpaso del tutorial.

    Parámetros:
    - session_attributes: Los atributos de la sesión actuales.
    - request_json: El evento desencadenado por Dialogflow que contiene los atributos de la sesión.

    Retorna:
    - Un diccionario con el mensaje del siguiente paso o subpaso y los atributos de la sesión actualizados.
    """
    step_substep = {0: 1, 1: 1, 2: 2, 3: 5, 4: 2, 5: 1}
    step = int(session_attributes.get('step', 1))
    substep = int(session_attributes.get('substep', 1))

    if substep == step_substep.get(step, 0):
        step += 1
        substep = 1
    else:
        substep += 1

    session_attributes['step'] = step
    session_attributes['substep'] = substep


    return build_response(message, session, session_attributes)

def current_step(session_attributes, session):
    """
    Repite el contenido del paso y subpaso actuales.

    Parámetros:
    - session_attributes: Los atributos de la sesión actuales.

    Retorna:
    - Un diccionario con el mensaje del paso y subpaso actuales y los atributos de la sesión.
    """
    step = int(session_attributes.get('step', 1))
    substep = int(session_attributes.get('substep', 1))

    
    return build_response(message, session, session_attributes)

def go_to_step(session_attributes, session):
    """
    Salta a un paso específico del tutorial según la solicitud del usuario.

    Parámetros:
    - session_attributes: Los atributos de la sesión actuales.
    - request_json: El evento desencadenado por Dialogflow que contiene los atributos de la sesión y el número de paso deseado.

    Retorna:
    - Un diccionario con el mensaje del paso especificado y los atributos de la sesión actualizados.
    """
    step = int(session_attributes.get('step', 1))

    if step < 1 or step > 5:
        message = "Lo siento, el paso especificado no es válido. Por favor, elige un paso entre 1 y 4."
        return build_response(message, session, session_attributes)

    session_attributes['step'] = step
    session_attributes['substep'] = 1

   
    return build_response(message, session, session_attributes)




def build_response(message, session, session_attributes):
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
    response = {
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [message]
                }
            }
        ],
        "outputContexts": [
            {
                "name": context_name,
                "lifespanCount": 5,
                "parameters": session_attributes
            }
        ]
    }
    return json.dumps(response), 200, {'Content-Type': 'application/json'}

