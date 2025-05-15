from typing import Optional, Dict, Any

import aiohttp


class RequestService:

    def __init__(self, timeout: int = 10):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session = None

    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def post(self, url: str, data: Optional[Dict] = None, json: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
        session = await self._get_session()
        try:
            async with session.post(
                url=url,
                data=data,
                json=json,
                headers=headers,
                timeout=self.timeout
            ) as response:
                status = response.status
                text = await response.text()

                if 200 <= status < 300:
                    try:
                        data = await response.json()
                        return {"success": True, "data": data, "error": None}
                    except aiohttp.ContentTypeError:
                        return {"success": True, "data": text, "error": None}
                else:
                    try:
                        error_data = await response.json(content_type=None)
                        status_code = error_data.get("statusCode", status)
                        message_text = error_data.get("message", "Unknown error")

                        validation_errors = error_data.get("validationErrors", {})
                        if validation_errors:
                            error_message = "\n".join(
                                f"Ошибка:{'\n' + error}" for field, error in validation_errors.items()
                            )
                        else:
                            error_message = f"HTTP Error {status_code}: {message_text}"
                    except (aiohttp.ContentTypeError, ValueError):
                        error_message = f"HTTP Error {status}: {text or 'No response body'}"

                    return {"success": False, "data": None, "error": error_message}

        except aiohttp.ClientError as e:
            error_message = f"Client Error: {str(e)}"
            return {"success": False, "data": None, "error": error_message}
        except Exception as e:
            error_message = f"Unexpected Error: {str(e)}"
            return {"success": False, "data": None, "error": error_message}
        finally:
            if self.session and not self.session.closed:
                await self.session.close()

request_service = RequestService()