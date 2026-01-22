import asyncio
import json
import uuid
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langchain_core.messages import ToolMessage, AIMessage
from pydantic import BaseModel
from typing import Any
import datetime
from upi_agent.prompts import SYSTEM_PROMPT_TEMPLATE, HUMAN_PROMPT_TEMPLATE
from upi_agent.schemas import AgentDecision
from upi_agent.mcp_tools import load_mcp_tools
from upi_agent.tools import output, error_handler
from upi_agent.enums import Tool  


def get_payment_agent(llm: ChatOpenAI):
    class AgentState(BaseModel):
        messages: list[Any]
        last_decision: Any = None
        date: str | None = None
        time: str | None = None
        amount: float | None = None
        sender_last4: str | None = None

        has_transaction_details: bool = False
    mcp_tools = load_mcp_tools()
    all_tools = [output, error_handler] + list(mcp_tools.values())

    prompt = ChatPromptTemplate.from_messages([
        ('system', SYSTEM_PROMPT_TEMPLATE),
        ('human', HUMAN_PROMPT_TEMPLATE),
    ])
    llm_with_structure = llm.with_structured_output(AgentDecision)
    llm_chain = prompt | llm_with_structure

    def tool(state: AgentState):
        """Main LLM decision node"""
        last_msg = state.messages[-1]
        if hasattr(last_msg, 'content'):
            user_input = last_msg.content
        else:
            user_input = str(last_msg)
        
        chat_history = []
        for m in state.messages[:-1]:
            if hasattr(m, 'content'):
                chat_history.append(m.content)
            else:
                chat_history.append(str(m))
        
        ai_message = llm_chain.invoke({
            'user_input': user_input,
            'chat_history': chat_history,
            'available_tools': list(mcp_tools.keys()),
            'current_date': str(datetime.datetime.now())
        })
        
        state.last_decision = ai_message
        return state

    def router(state: AgentState):
        """Route to appropriate node based on action"""
        action = state.last_decision.action
        # Convert to string for routing
        if isinstance(action, str):
            return action
        return str(action)  # Handle both string and enum

    def tool_call_node(state: AgentState):
        """Execute tool calls"""
        last_decision = state.last_decision
        tool_name = last_decision.action
        
        # Convert to string if it's an enum or has .value
        if hasattr(tool_name, 'value'):
            tool_name = tool_name.value
        elif not isinstance(tool_name, str):
            tool_name = str(tool_name)
        
        print(f"Executing tool: {tool_name}")
        print(f"Tool input: {last_decision.action_input}")

        try:
            # Parse action_input if it's a string
            if isinstance(last_decision.action_input, str):
                tool_input = json.loads(last_decision.action_input)
            else:
                tool_input = last_decision.action_input
            
            # Execute the appropriate tool
            if tool_name == 'error_handler':
                tool_resp = error_handler.invoke(tool_input)
            elif tool_name == 'get_transaction_details':
                # Handle MCP tool asynchronously
                tool_resp = asyncio.run(mcp_tools['get_transaction_details'].ainvoke(tool_input))
            
                
            
            else:
                tool_resp = {"error": f"Unknown tool: {tool_name}"}
            
            print(f"Tool response: {tool_resp}")
            state.messages.append(ToolMessage(str(tool_resp), tool_call_id=str(uuid.uuid4())))
            
        except Exception as e:
            print(f"Tool error: {str(e)}")
            error_msg = {"error": f"Tool execution failed: {str(e)}"}
            state.messages.append(ToolMessage(str(error_msg), tool_call_id=str(uuid.uuid4())))
        
        return state

    def output_node(state: AgentState):
        """Output final message to user"""
        last_decision = state.last_decision
        message_content = last_decision.action_input
        
        # Handle both dict and string formats
        if isinstance(message_content, dict):
            message_text = message_content.get('message', str(message_content))
        elif isinstance(message_content, str):
            message_text = message_content
        else:
            message_text = str(message_content)
        
        state.messages.append(AIMessage(message_text))
        return state

    # Build the graph
    state_graph = StateGraph(AgentState)
    state_graph.add_node('process_input', tool)
    state_graph.add_node('output', output_node)
    state_graph.add_node('tool_call', tool_call_node)

    state_graph.add_edge(START, 'process_input')
    state_graph.add_conditional_edges('process_input', router, {
        'get_transaction_details': 'tool_call',
        'error_handler': 'tool_call',
        'output': 'output'
    })
    state_graph.add_edge('tool_call', 'process_input')
    state_graph.add_edge('output', END)

    agent = state_graph.compile()
    return agent




from langchain_core.messages import HumanMessage
from upi_agent.main_agents import get_payment_agent


def run_upi_agent(user_query: str, llm, upi_state: dict | None = None):
    """
    Runs UPI agent with persistent state controlled by Supervisor.
    """

    if upi_state is None or not upi_state:
        agent = get_payment_agent(llm)
        upi_state = {
            "agent": agent,
            "messages": []
        }
    else:
        agent = upi_state["agent"]

    # ✅ append new user message
    upi_state["messages"].append(HumanMessage(content=user_query))

    # ✅ invoke agent with full memory
    result = agent.invoke({"messages": upi_state["messages"]})

    # ✅ update memory from agent result
    upi_state["messages"] = result.get("messages", upi_state["messages"])

    # ✅ extract final assistant message
    messages = upi_state["messages"]
    if messages:
        return messages[-1].content, upi_state

    return "I couldn't process your UPI request.", upi_state
