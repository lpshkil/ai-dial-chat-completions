from aidial_client import Dial, AsyncDial

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        # TODO:
        # Documentation: https://pypi.org/project/aidial-client/
        # 1. Create Dial client with:
        #   - base_url=DIAL_ENDPOINT
        #   - api_key=self._api_key
        self.client = Dial(api_key=self._api_key, base_url=DIAL_ENDPOINT)

        # 2. Create AsyncDial client with:
        #   - base_url=DIAL_ENDPOINT
        #   - api_key=self._api_key
        self.async_client = AsyncDial(api_key=self._api_key, base_url=DIAL_ENDPOINT)

    def get_completion(self, messages: list[Message]) -> Message:
        # TODO:
        # 1. Create chat completions with client (client.chat.completions.create) with such params:
        #   - deployment_name=self._deployment_name
        #   - messages=[msg.to_dict() for msg in messages]
        # 2. Check if 'choices' are present in `response`
        #       -> check if message is present in `choices[0]`
        #           -> print message content and return message with assistant role and message content
        # 3. If choices are not present then raise Exception("No choices in response found")

        response = self.client.chat.completions.create(
            deployment_name=self._deployment_name,
            stream=False,
            messages=[msg.to_dict() for msg in messages]
        )
        
        if response.choices and len(response.choices) > 0:
            choice_0 = response.choices[0]
            if choice_0.message:
                message_content = choice_0.message.content
                print("AI: ", message_content)
                return Message(role=Role.AI, content=message_content)
        else:
            raise Exception("No choices in response found")

    async def stream_completion(self, messages: list[Message]) -> Message:
        # TODO:
        # 1. Create chat completions with client (async_client.chat.completions.create) with such params:
        #   - deployment_name=self._deployment_name
        #   - messages=[msg.to_dict() for msg in messages]
        #   - stream=True

        response = await self.async_client.chat.completions.create(
            deployment_name=self._deployment_name,
            stream=True,
            messages=[msg.to_dict() for msg in messages]
        )
                
        # 2. Create array with `contents` name (here we will collect all content chunks)
        contents = []

        # 3. Make async loop from `chunks` (from 1st step)
        async for chunk in response:
            # 4. If chunk has choices and their len > 0 then:
            if chunk.choices and len(chunk.choices) > 0:
                choice_0 = chunk.choices[0]
                #       -> get it's `delta`
                delta = choice_0.delta
                #           -> if delta is present and has content
                if delta and delta.content:
                    #               -> print(delta.content, end='') and add content to `contents` array
                    print(delta.content, end='', flush=True)
                    contents.append(delta.content)

        # 5. Print empty row `print()` (it will represent the end of streaming and in console we will print input from a new line)
        print()
        # 6. Return Message with assistant role and message content (`''.join(contents)`)
        return Message(role=Role.AI, content=''.join(contents))
