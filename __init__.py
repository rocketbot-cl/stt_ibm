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

import os
import sys
base_path = tmp_global_obj["basepath"]
cur_path = base_path + 'modules' + os.sep + 'STT_IBM' + os.sep + 'libs' + os.sep
if cur_path not in sys.path:
    sys.path.append(cur_path)
import magic
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

module = GetParams("module")

if module == "GetSTT":
    audio_file = GetParams("audio_path")
    api_key = GetParams("api_key")
    url_service = GetParams("url_service")
    result = GetParams("result")
    try:
        authenticator = IAMAuthenticator(api_key)
        service = SpeechToTextV1(authenticator=authenticator)
        service.set_service_url(url_service)

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
    except Exception as e:
        PrintException()
        raise e
