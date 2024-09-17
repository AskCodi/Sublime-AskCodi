import json
import urllib.request
from typing import Dict, List, Optional
from .error_logger import UnknownException

# Assuming you have defined these types elsewhere in your Python code
Messages = List[Dict[str, str]]
GenericDict = Dict[str, any]

# You'll need to define these variables
url = "https://apiv5.askcodi.com/"
# url = "http://localhost:8000/"
version = "5.4"


def get_models(api_key: str):
    try:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "apikey": api_key,
            "source": "VSCode",
            "version": version
        }

        req = urllib.request.Request(
            url + "api/codi-models",
            headers=headers,
            method="GET"
        )

        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))

        return result["content"]
    except Exception as error:
        raise UnknownException(str(error))


def initiate_stream(chat_id: str, app: str, instruction: Optional[str], history: Optional[Messages], context: Optional[str], language: str, model: str, api_key: str) -> GenericDict:
    try:
        data = {
            "chatId": chat_id,
            "app": app,
            "instruction": instruction,
            "history": history,
            "context": context,
            "inputLanguage": language,
            "model": {
                "model": model,
                "apiKey": "",
                "image": False
            }
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "apikey": api_key,
            "source": "VSCode",
            "version": version
        }

        req = urllib.request.Request(
            url + "api/initiate-stream-extension",
            data=json.dumps(data).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))

        return result
    except Exception as error:
        raise UnknownException(str(error))

        
def connect_sse(provider, session_id):
    try:
        req = urllib.request.Request(url + "api/stream-response?session_id=" + session_id)
        try:
            with urllib.request.urlopen(req) as response:
                provider.handle_data(response)
        except urllib.error.URLError as e:
            raise UnknownException(str(error))
    except Exception as error:
        raise UnknownException(str(error))
        