# coding: utf-8
"""
Base para desarrollo de modulos externos.
Para obtener el modulo/Funcion que se esta llamando:
     GetParams("module")

Para obtener las variables enviadas desde formulario/comando Rocketbot:
    var = GetParams(variable)
    Las "variable" se define en forms del archivo package.json

Para modificar la variable de Rocketbot:
    SetVar(Variable_Rocketbot, "dato")

Para obtener una variable de Rocketbot:
    var = GetVar(Variable_Rocketbot)

Para obtener la Opcion seleccionada:
    opcion = GetParams("option")


Para instalar librerias se debe ingresar por terminal a la carpeta "libs"
    
    pip install <package> -t .

"""
from ibm_watson import SpeechToTextV1
import magic

module = GetParams("module")

if module == "GetSTT":
    audio_file = GetParams("audio_path")
    api_key = GetParams("api_key")
    url_service = GetParams("url_service")
    result = GetParams("result")

    service = SpeechToTextV1(
        iam_apikey=api_key,
        url=url_service
    )

    audio_format = magic.from_file(audio_file, mime=True)
    with open(audio_file, 'rb') as audio:
        response = service.recognize(
            audio=audio,
            content_type=audio_format,
            timestamps=False,
            word_confidence=False,
            model="es-ES_BroadbandModel").get_result()

    if result:
        SetVar(result, response["results"])
