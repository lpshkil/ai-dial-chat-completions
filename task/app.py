import asyncio

from task.clients.client import DialClient
# from task.clients.custom_client import DialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role


async def start(stream: bool) -> None:
    #TODO:
    # 1.1. Create DialClient
    #    - deployment_name: available gpt model. Sample: `gpt-4o`
    #      (you can get available deployment_name via https://ai-proxy.lab.epam.com/openai/models
    #       you can import Postman collection to make a request, file in the project root `dial-basics.postman_collection.json`
    #       don't forget to add your API_KEY)
    dial_client = DialClient(deployment_name="gpt-4o")
    
    # 1.2. Create CustomDialClient
    
    # 2. Create Conversation object
    conversation = Conversation()
    
    # 3. Get System prompt from console or use default -> constants.DEFAULT_SYSTEM_PROMPT and add to conversation
    #    messages. To do that use the `input()` function
    print("Provide System prompt or press 'enter' to continue.")
    system_promt = input("> ")
    if not system_promt:
        system_promt = DEFAULT_SYSTEM_PROMPT

    conversation.add_message(Message(role=Role.SYSTEM, content=system_promt))  

    # 4. Use infinite cycle (while True) and get yser message from console
 
    is_processsing = True
    print("Type your question or 'exit' to quit.")
    while is_processsing:
        user_message = input("> ")

    # 5. If user message is `exit` then stop the loop
        if user_message == "exit":
            print("Exiting the chat. Goodbye!")
            is_processsing = False
            continue

    # 6. Add user message to conversation history (role 'user')
        conversation.add_message(Message(role=Role.USER, content=user_message))

    # 7. If `stream` param is true -> call DialClient#get_completion()
    #    else -> call DialClient#stream_completion()

        if stream:
            completition_message = await dial_client.stream_completion(messages=conversation.get_messages())
        else:
            completition_message = dial_client.get_completion(messages=conversation.get_messages())
        
    # 8. Add generated message to history
        conversation.add_message(completition_message)
    
    # 9. Test it with DialClient and CustomDialClient
    # 10. In CustomDialClient add print of whole request and response to see what you send and what you get in response

asyncio.run(
    start(True)
)
