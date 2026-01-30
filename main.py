
import colorama
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from upi_agent.main_agents import get_payment_agent

colorama.init(autoreset=True)

llm = ChatOpenAI(
    model="NPCI_Greviance",
    base_url="http://183.82.7.228:9519/v1",
    api_key="sk-api",
    temperature=0.1,
)

agent = get_payment_agent(llm)


print(colorama.Fore.CYAN + " PAYMENT AGENT CHAT")


messages = []

while True:
    user_input = input(colorama.Fore.WHITE + "User: ")
    
    if user_input.strip() == 'quit':
        print(colorama.Fore.CYAN + "\n Goodbye!")
        break
    
    if not user_input.strip():
        continue
    
    # Add user message
    messages.append(HumanMessage(content=user_input))
    
    try:
        # Invoke agent
        resp = agent.invoke({'messages': messages})
        
        # Get AI response
        ai_response = resp['messages'][-1].content
        print(colorama.Fore.GREEN + f"AI: {ai_response}\n")
        
        # Update messages with full conversation
        messages = resp['messages']
        
    except Exception as e:
        print(colorama.Fore.RED + f" Error: {str(e)}\n")