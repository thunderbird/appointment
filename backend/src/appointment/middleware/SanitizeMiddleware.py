import json
import nh3
from starlette.types import ASGIApp, Scope, Receive, Send
from ..utils import is_json


class SanitizeMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    @staticmethod
    def sanitize_str(value: str) -> str:
        return nh3.clean(value, tags={""}) if isinstance(value, str) else value

    @staticmethod
    def sanitize_dict(dict_value: str) -> str:
        return {key: __class__.sanitize_str(value) for key, value in dict_value.items()}

    @staticmethod
    def sanitize_list(list_values: list) -> list:
        for index, value in enumerate(list_values):
            if isinstance(value, dict):
                list_values[index] = {key: __class__.sanitize_str(value) for key, value in value.items()}
            else:
                list_values[index] = __class__.sanitize_str(value)
        return list_values

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if "method" not in scope or scope["method"] in ("GET", "HEAD", "OPTIONS"):
            return await self.app(scope, receive, send)

        async def sanitize_request_body():
            message = await receive()
            body = message.get("body")
            if not body or not isinstance(body, bytes):
                return message
            if is_json(body):
                json_body = json.loads(body)
                for key, value in json_body.items():
                    if isinstance(value, dict):
                        json_body[key] = __class__.sanitize_dict(value)
                    elif isinstance(value, list):
                        json_body[key] = __class__.sanitize_list(value)
                    else:
                        json_body[key] = __class__.sanitize_str(value)
                message["body"] = bytes(json.dumps(json_body), encoding="utf-8")

            return message

        return await self.app(scope, sanitize_request_body, send)
