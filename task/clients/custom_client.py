import json
import aiohttp
import requests

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):
    _endpoint: str
    _api_key: str

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self._endpoint = DIAL_ENDPOINT + f"/openai/deployments/{deployment_name}/chat/completions"

    def get_completion(self, messages: list[Message]) -> Message:
        #TODO:
        # 1. Create headers dictionary with:
        #   - "api-key": self._api_key
        #   - "Content-Type": "application/json"
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json"
        }
        # 2. Create request_data dictionary with:
        #   - "messages": convert messages list to dict format using msg.to_dict() for each message
        request_data = {
            "messages": [msg.to_dict() for msg in messages]
        }

        # 3. Make POST request using requests.post() with:
        #   - URL: self._endpoint
        #   - headers: headers from step 1
        #   - json: request_data from step 2
        response = requests.post(
            url=self._endpoint,
            headers=headers,
            json=request_data
        )

        # 4. Check if response.status_code == 200:
        #   - If yes: parse JSON response using response.json()
        #   - Get "choices" from response data
        #   - If choices exist and not empty:
        #     * Extract content from choices[0]["message"]["content"]
        #     * Print the content to console
        #     * Return Message(role=Role.AI, content=content)
        #   - If no choices: raise ValueError("No Choice has been present in the response")

        if response.status_code == 200:
            response_data = response.json()
            choices = response_data.get("choices", [])
            if choices:
                content = choices[0]["message"]["content"]
                print("AI: ", content)
                return Message(role=Role.AI, content=content)
            else:
                raise ValueError("No Choice has been present in the response")
        else:     
        # 5. If status code != 200:
        #   - Raise Exception with format: f"HTTP {response.status_code}: {response.text}"
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        
    async def stream_completion(self, messages: list[Message]) -> Message:
        #TODO:
        # 1. Create headers dictionary with:
        #    - "api-key": self._api_key
        #    - "Content-Type": "application/json"
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json"
        }
        # 2. Create request_data dictionary with:
        #    - "stream": True  (enable streaming)
        #    - "messages": convert messages list to dict format using msg.to_dict() for each message
        request_data = {
            "messages": [msg.to_dict() for msg in messages],
            "stream": True
        }
        # 3. Create empty list called 'contents' to store content snippets
        contents = []

        # 4. Create aiohttp.ClientSession() using 'async with' context manager
        async with aiohttp.ClientSession() as session:
        
        # 5. Inside session, make POST request using session.post() with:
        #    - URL: self._endpoint
        #    - json: request_data from step 2
        #    - headers: headers from step 1
        #    - Use 'async with' context manager for response
            async with session.post(
                url=self._endpoint,
                json=request_data,
                headers=headers
            ) as response:
        # 6. Check if response.status == 200:
        #    - If yes: iterate through response.content using 'async for line in response.content:'
        #      * Decode line: line_str = line.decode('utf-8').strip()
        #      * Check if line starts with "data: ":
        #        - Extract data: data = line_str[6:].strip()
        #        - If data != "[DONE]":
        #          + Call self._get_content_snippet(data) to extract content
        #          + Print content snippet without newline: print(content_snippet, end='')
        #          + Append content snippet to contents list
        #        - If data == "[DONE]":
        #          + Print empty line: print()
        #    - If status != 200:
        #      * Get error text: error_text = await response.text()
        #      * Print error: print(f"{response.status} {error_text}")
                if response.status == 200:
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith("data: "):
                            data = line_str[6:].strip()
                            if data != "[DONE]":
                                content_snippet = self._get_content_snippet(data)
                                print(content_snippet, end='')
                                contents.append(content_snippet)
                            else:
                                print()
                else:
                    error_text = await response.text()
                    print(f"{response.status} {error_text}")
        # 7. Return Message(role=Role.AI, content=''.join(contents))
        return Message(role=Role.AI, content=''.join(contents))

    def _get_content_snippet(self, data: str) -> str:
        """
        Extract content from streaming data chunk.
        """
        #TODO:
        # 1. Parse JSON data using json.loads(data)
        parsed_data = json.loads(data)

        # 2. Get "choices" from parsed JSON data
        choices = parsed_data.get("choices", [])

        # 3. If choices exist and not empty:
        #    - Get delta from choices[0]["delta"]
        #    - Return content from delta.get("content", '') - use empty string as default
        if choices:
            delta = choices[0].get("delta", {})
            return delta.get("content", '')
        else:
        # 4. If no choices, return empty string
            return ''
