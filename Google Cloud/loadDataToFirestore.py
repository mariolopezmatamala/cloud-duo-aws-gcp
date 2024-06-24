from google.cloud import firestore

def loadDataToFirestore(request):
    """
    Esta función carga datos en la base de datos de Firestore.
    
    Parámetros:
    request: La solicitud HTTP que activa la función. Este parámetro no se utiliza dentro de la función, pero es necesario para que funcione como una Cloud Function. 
    La función se activa como prueba para cargar los datos.

    Acciones:
    - Conecta con el cliente de Firestore.
    - Define el nombre de la colección en la que se insertarán los documentos.
    - Define una lista de diccionarios, donde cada diccionario representa un documento con campos 'IntentName', 'Question' y 'Response'.
    - Itera sobre la lista de diccionarios, generando un ID de documento único para cada diccionario combinando 'IntentName' y 'Question'.
    - Inserta cada documento en la colección de Firestore utilizando el ID de documento generado.
    
    Retorno:
    - Devuelve un mensaje indicando que los datos se han cargado exitosamente.
    """
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
            {"IntentName": "DialogflowES", "Question": "¿Qué son las frases de entrenamiento en Dialogflow ES?", "Response": "Las frases de entrenamiento son ejemplos de entradas que los usuarios pueden decir para activar un intent, ayudando a entrenar el modelo de lenguaje del agente."}
        ]
        

        for response in responses:
            doc_id = f"{response['IntentName']}_{response['Question']}"
            collection_ref.document(doc_id).set(response)

        collection_name = 'chatbotsteps'
        collection_ref = db.collection(collection_name)

        responses2 =  [
            {"IntentName": "NextStep", "Question": "1_1", "Response": "Paso1_SubPaso1.txt"},
            {"IntentName": "NextStep", "Question": "2_1", "Response": "Paso2_SubPaso1.txt"},
            {"IntentName": "NextStep", "Question": "2_2", "Response": "Paso2_SubPaso2.txt"},
            {"IntentName": "NextStep", "Question": "3_1", "Response": "Paso3_SubPaso1.txt"},
            {"IntentName": "NextStep", "Question": "3_2", "Response": "Paso3_SubPaso2.txt"},
            {"IntentName": "NextStep", "Question": "3_3", "Response": "Paso3_SubPaso3.txt"},
            {"IntentName": "NextStep", "Question": "3_4", "Response": "Paso3_SubPaso4.txt"},
            {"IntentName": "NextStep", "Question": "3_5", "Response": "Paso3_SubPaso5.txt"},
            {"IntentName": "NextStep", "Question": "4_1", "Response": "Paso4_SubPaso1.txt"},
            {"IntentName": "NextStep", "Question": "4_2", "Response": "Paso4_SubPaso2.txt"},
            {"IntentName": "NextStep", "Question": "5_1", "Response": "Paso5_SubPaso1.txt"},
        ]   

        for response in responses2:
            doc_id = f"{response['IntentName']}_{response['Question']}"
            collection_ref.document(doc_id).set(response)

        return "Datos cargados exitosamente."
        
    except Exception as e:
        return f"Error al cargar los datos: {str(e)}"
