# cloud-duo-aws-gcp

## Descripción
Archivos para las funciones lambda del bot de GCP.

## Contenido
En esta carpeta se almacena el código necesario para las cloud functions.  El contenido de esta sección es el siguiente:
* Documentación/: Contiene los archivos en formato pdf para cargar en storage y comenzar su extracción, para posterior uso del bot.
* load_data_to_firestore.py: Script que carga las preguntas y respuestas a la base de datos de firestore.
* document_AI_extract_text.py: Script en Python encargado de invocar el servicio DocumentAI para la extracción de texto de documentos.
* dialogflow_integration.py: Script en Python que maneja la integración con Dialogflow.
* analyze_text.py: Script en Python que procesa los resultados obtenidos de DocumentAI. 
