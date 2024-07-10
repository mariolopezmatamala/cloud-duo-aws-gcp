# cloud-duo-aws-gcp

## Descripción
Archivos para las funciones lambda del bot de AWS.

## Contenido
En esta carpeta se almacena el código necesario para las funciones lambda.  El contenido de esta sección es el siguiente:
* Documentación/: Contiene los archivos en formato pdf para cargar en S3 y comenzar su extracción, para posterior uso del bot.
* campos_dynamoDB.py: Script que carga las preguntas y respuestas a la base de datos.
* invoke_textract.py: Script en Python encargado de invocar el servicio Amazon Textract para la extracción de texto de documentos.
* lex_integration.py: Script en Python que maneja la integración con Amazon Lex.
* result_textract.py: Script en Python que procesa los resultados obtenidos de Amazon Textract. 
