"""
Esta función de Google Cloud Function está diseñada para cargar datos predefinidos en Google Firestore.
Es invocada por una solicitud HTTP, típicamente como parte de una operación de inicialización o mantenimiento
para asegurar que Firestore contenga las respuestas necesarias para un chatbot.

Funcionalidades:
- Conexión con Firestore: Establece un cliente de Firestore y se conecta a una colección específica.
- Datos predefinidos: Define una lista de respuestas típicas que un chatbot podría necesitar, cubriendo
  diversas intenciones y preguntas frecuentes.
- Carga de datos: Inserta los datos en Firestore, generando un ID de documento único basado en la combinación
  de 'IntentName' y 'Question' para evitar duplicados y permitir una fácil recuperación.
- Manejo de excepciones: Captura y maneja cualquier error durante el proceso de carga, proporcionando
  retroalimentación adecuada.

Parámetros:
- request (flask.Request): El objeto request que activa la función. No se utiliza directamente
  dentro de la función, pero es necesario para cumplir con la interfaz esperada por Google Cloud Functions.

Retorno:
- str: Un mensaje que indica el resultado de la operación de carga, ya sea un éxito o un mensaje de error
  detallando cualquier problema que ocurrió.

Ejemplo de uso:
Esta función puede ser desencadenada manualmente a través de una herramienta de interfaz de línea de comandos
o automáticamente por un evento en el sistema que requiere reinitialización o actualización de los datos del
chatbot en Firestore.
"""
from google.cloud import firestore

def load_data_to_firestore(request):
    try:
        db = firestore.Client()
        collection_name = 'chatbotresponses'
        collection_ref = db.collection(collection_name)

        
        responses = [
            {"IntentName": "CreacionStorage", "Question": "¿Qué es Google Cloud Storage?", "Response": "Google Cloud Storage es un servicio de almacenamiento de objetos en la nube que permite almacenar y acceder a datos no estructurados con alta durabilidad y disponibilidad."},
            {"IntentName": "CreacionStorage", "Question": "¿Cómo se crea un bucket en Google Cloud Storage?", "Response": "Para crear un bucket, accede a Google Cloud Storage en la consola de Google Cloud, haz clic en 'Crear bucket', configura el nombre, la región y deja el resto en estándar."},
            {"IntentName": "CreacionStorage", "Question": "¿Qué son las carpetas en Google Cloud Storage?", "Response": "Las carpetas en Google Cloud Storage son una manera de organizar los objetos dentro de un bucket, proporcionando una estructura jerárquica para facilitar la gestión de archivos."},
            {"IntentName": "CreacionStorage", "Question": "¿Cómo se crean carpetas en Google Cloud Storage?", "Response": "Para crear carpetas, accede a tu bucket en Google Cloud Storage, selecciona 'Crear carpeta', ingresa el nombre de la carpeta y guarda los cambios."},
            {"IntentName": "CreacionStorage", "Question": "¿Cuál es la configuración más segura para un bucket en Google Cloud Storage?", "Response": "La configuración más segura implica habilitar el cifrado de objetos, restringir el acceso público, habilitar el registro de acceso y aplicar políticas de acceso específicas."},
            {"IntentName": "DocumentAI", "Question": "¿Qué es Google Cloud Document AI?", "Response": "Google Cloud Document AI es un servicio de Google Cloud que utiliza inteligencia artificial para extraer texto, datos y otros contenidos de documentos de forma automática."},
            {"IntentName": "DocumentAI", "Question": "¿Cómo se habilita la API de Document AI?", "Response": "Para habilitar la API de Document AI, busca el servicio en la consola de Google Cloud y haz clic en 'Habilitar API'."},
            {"IntentName": "DocumentAI", "Question": "¿Qué es un procesador en Document AI?", "Response": "Un procesador en Document AI es una configuración que define cómo se deben procesar los documentos. Hay diferentes tipos de procesadores para distintas tareas, como la extracción de texto o el análisis de formularios."},
            {"IntentName": "DocumentAI", "Question": "¿Cómo se crea un procesador en Document AI?", "Response": "Para crear un procesador, accede a Document AI, selecciona 'Crear procesador', elige el tipo de procesador (por ejemplo, Document OCR), configura el nombre y la región."},
            {"IntentName": "DocumentAI", "Question": "¿Cómo se prueba un procesador en Document AI?", "Response": "Para probar un procesador, sube un documento de prueba y verifica los resultados para asegurarte de que se ha configurado correctamente."},
            {"IntentName": "CloudFunctions", "Question": "¿Qué es Google Cloud Functions?", "Response": "Google Cloud Functions es un servicio de computación sin servidor que permite ejecutar funciones en respuesta a eventos sin necesidad de administrar servidores."},
            {"IntentName": "CloudFunctions", "Question": "¿Cómo se crea una función en Google Cloud Functions?", "Response": "Para crear una función, accede a Google Cloud Functions, haz clic en 'Crear función', elige el entorno de ejecución, configura el nombre, la región y el tipo de activador."},
            {"IntentName": "CloudFunctions", "Question": "¿Qué es un activador en Google Cloud Functions?", "Response": "Un activador es una fuente de eventos que invoca la función, como un evento de Cloud Storage, un mensaje de Pub/Sub o una solicitud HTTP."},
            {"IntentName": "CloudFunctions", "Question": "¿Cómo se configura un activador de Cloud Storage para una función?", "Response": "Para configurar un activador de Cloud Storage, selecciona el tipo de evento 'finalized', elige el bucket correspondiente y guarda los cambios."},
            {"IntentName": "CloudFunctions", "Question": "¿Qué es Cloud Tasks y cómo se usa con Cloud Functions?", "Response": "Cloud Tasks es un servicio que permite programar tareas asíncronas. Se utiliza para enviar notificaciones de una función a otra mediante colas de tareas."},
            {"IntentName": "CloudFunctions", "Question": "¿Cómo se habilitan las APIs necesarias para Cloud Functions?", "Response": "Para habilitar las APIs, busca los servicios correspondientes en la consola de Google Cloud y haz clic en 'Habilitar API'. Para esta tarea, necesitas habilitar las APIs de Cloud Functions, Cloud Storage, Cloud Tasks, Cloud Natural Language y Translate."},
            {"IntentName": "DialogflowES", "Question": "¿Qué es Dialogflow ES?", "Response": "Dialogflow ES es una plataforma de desarrollo de interfaces conversacionales que permite crear chatbots y asistentes virtuales utilizando procesamiento de lenguaje natural."},
            {"IntentName": "DialogflowES", "Question": "¿Cómo se crea un agente en Dialogflow ES?", "Response": "Para crear un agente, accede a Dialogflow ES, haz clic en 'Crear agente', proporciona un nombre, selecciona el proyecto de Google Cloud y configura el idioma y la región."},
            {"IntentName": "DialogflowES", "Question": "¿Qué es un intent en Dialogflow ES?", "Response": "Un intent es una configuración que define cómo debe responder el agente a una entrada específica del usuario, incluyendo las frases de entrenamiento y las respuestas."},
            {"IntentName": "DialogflowES", "Question": "¿Cómo se configura un fulfillment en Dialogflow ES?", "Response": "Para configurar un fulfillment, habilita el webhook en la sección de Fulfillment y proporciona la URL de tu Cloud Function que manejará las solicitudes."},
            {"IntentName": "DialogflowES", "Question": "¿Qué son las frases de entrenamiento en Dialogflow ES?", "Response": "Las frases de entrenamiento son ejemplos de entradas que los usuarios pueden decir para activar un intent, ayudando a entrenar el modelo de lenguaje del agente."},
            {"IntentName": "IdeaTrabajo", "Question": "¿Cuál es la idea del proyecto?", "Response": "La idea principal es desarrollar y comparar dos chatbots utilizando los servicios en la nube de AWS y GCP."},
            {"IntentName": "QueHace", "Question": "¿Qué hace este proyecto?", "Response": "Este proyecto desarrolla dos chatbots utilizando AWS y GCP. Integra múltiples servicios en la nube como Amazon Lex, Lambda, S3, Textract, Comprehend, y Google Dialogflow, Cloud Functions, y Storage para manejar consultas del tutorial de creación de chatbots."},
            {"IntentName": "Objetivos", "Question": "¿Cuáles son los objetivos del proyecto?", "Response": "- Evaluar la eficacia y eficiencia de las herramientas y servicios proporcionados por AWS y GCP para el desarrollo de chatbots. - Proporcionar una guía detallada y práctica para la implementación de chatbots en entornos empresariales utilizando tecnologías de computación en la nube."},
            {"IntentName": "ConceptosTeoricos", "Question": "¿Qué conceptos teóricos se utilizan en el proyecto?", "Response": "Los conceptos teóricos más destacables de este proyecto residen en el procesamiento del lenguaje natural(NLP en adelante) el cual es una subdisciplina de la inteligencia artificial que se dedica a la interacción entre las computadoras y los lenguajes humanos."},
            {"IntentName": "TecnicasHerramientas", "Question": "¿Qué técnicas y herramientas se han utilizado?", "Response": "Estas son las herramientas utilizadas en el proyecto: Scrum, Git, GitHub Desktop, GitHub, Email, Microsoft Teams, Visual Studio Code, Texmaker, Pylint, Coverage, HTML, CSS, Amazon Lex, AWS Lambda, Amazon S3, Amazon Textract, Amazon Comprehend, Amazon Translate, Amazon DynamoDB, Dialogflow, Cloud Functions y Cloud Storage."},
            {"IntentName": "TrabajosRelacionados", "Question": "¿Qué trabajos similares existen?", "Response": "Estos son los trabajos similares y en los que se ha basado el proyecto: Estudio sobre la creación de un asistente virtual interactivo para la programación en C utilizando Amazon Lex y Lambda, Trabajo en GitHub sobre la extracción de insights conversacionales de facturas con Amazon Textract, Amazon Comprehend y Amazon Lex, Documentación proporcionada por AWS, Trabajo sobre la creación de un chatbot utilizando Dialogflow y Google Cloud Functions."},
            {"IntentName": "Conclusiones", "Question": "¿Cuáles son las conclusiones del proyecto?", "Response": "A lo largo de este proyecto, se han desarrollado dos chatbots utilizando los servicios en la nube de AWS y GCP. Estos chatbots integran servicios avanzados como Amazon Lex, Lambda, S3, Textract, Comprehend, Translate, y DynamoDB, así como Dialogflow, Cloud Functions y Cloud Storage. Se ha adquirido un profundo conocimiento sobre microservicios, integración de múltiples servicios en la nube y mejores prácticas para el despliegue de chatbots."},
            {"IntentName": "LineasFuturas", "Question": "¿Cuáles son las líneas de trabajo futuras?", "Response": "En un futuro, se puede mejorar el proyecto en estos ámbitos: Creación de Nuevos Intents, Integración de un Mayor Número de Servicios, Mejora de la Lógica en Funciones Lambda, Implementación de Aprendizaje Automático."},
            {"IntentName": "GitHubInfo", "Question": "¿Dónde puedo encontrar el código en GitHub?", "Response": "Lo puedes encontrar desde este enlace de github: https://github.com/mariolopezmatamala/cloud-duo-aws-gcp/tree/main/docs"},
            {"IntentName": "GitHubInfo", "Question": "¿Dónde está la memoria y los anexos?", "Response": "Lo puedes encontrar desde este enlace de github: https://github.com/mariolopezmatamala/cloud-duo-aws-gcp/tree/main/docs"},
            {"IntentName": "GitHubInfo", "Question": "¿Cómo accedo a los documentos del proyecto?", "Response": "Lo puedes encontrar desde este enlace de github: https://github.com/mariolopezmatamala/cloud-duo-aws-gcp/tree/main/docs"},
            {"IntentName": "EstructuraMemoria", "Question": "¿Cuál es la estructura de la memoria del proyecto?", "Response": "La memoria se divide en: Introducción, Objetivos del proyecto, Conceptos teóricos, Técnicas y herramientas, Aspectos relevantes del desarrollo, Trabajos relacionados, Conclusiones y líneas de trabajo futuras, Plan del proyecto software, Especificación de requisitos del software, Especificación de diseño, Manual del programador, Manual de usuario."},
            {"IntentName": "Metodologias", "Question": "¿Qué metodologías se han utilizado?", "Response": "Se ha seguido durante todo el proyecto un desarrollo iterativo basado en Scrum con Sprints"},
            {"IntentName": "Sprints", "Question": "¿Cuántos sprints se realizaron?", "Response": "Se han realizado 7 sprints y una fase inicial."},
        ]
        

        for response in responses:
            doc_id = f"{response['IntentName']}_{response['Question']}"
            collection_ref.document(doc_id).set(response)

        #=================================#
        #Introducción de pasos del tutorial
        steps = {1: 1, 2: 2, 3: 5, 4: 3, 5: 3, 6: 1}
        
        responses = []

        collection_name = 'chatbotsteps'
        collection_ref = db.collection(collection_name)

        for step, substeps in steps.items():
            for substep in range(1, substeps + 1):
                entry = {
                    "IntentName": "tutorial",
                    "Question": f"{step}_{substep}",
                    "Response": f"Paso{step}_Subpaso{substep}.txt"
                }
                responses.append(entry)   

        for response in responses:
            doc_id = f"{response['IntentName']}_{response['Question']}"
            collection_ref.document(doc_id).set(response)

        return "Datos cargados exitosamente."
        
    except Exception as e:
        return f"Error al cargar los datos: {str(e)}"
