import os
from langchain.tools import tool
import uuid
from teacher_assistant import teacher_assistant_agent
from planner import planner_agent
from composio import Composio
from composio_langchain import LangchainProvider
from langchain.agents import create_agent
from config import  *


composio = Composio(provider=LangchainProvider(),api_key=COMPOSIO_API_KEY)
# Create a session for your user
session = composio.create(user_id="user_123")
tools = session.tools()

@tool
def ask_planner(query: str) -> str:
    """Delegate to Planner agent for roadmaps, schedules, and learning plans."""
    config = {"configurable": {"thread_id": f"planner_{uuid.uuid4()}"}}
    result = planner_agent.invoke(
        {"messages": [{"role": "user", "content": query}]},
        config=config
    )
    messages = result.get("messages", [])
    for msg in reversed(messages):
        if hasattr(msg, "content") and msg.content:
            if not hasattr(msg, "tool_calls") or not msg.tool_calls:
                return msg.content
    return ""


@tool
def ask_teacher_assistant(query: str) -> str:
    """
    Delegate to the Teacher Assistant agent for technical implementation,
    code examples, troubleshooting, or practical hands-on guidance.
    Use when the query needs technical depth beyond theory.
    """
    config = {"configurable": {"thread_id": f"assistant_{uuid.uuid4()}"}}
    
    result = teacher_assistant_agent.invoke(
        {"messages": [{"role": "user", "content": query}]},
        config=config
    )
    
    messages = result.get("messages", [])
    for msg in reversed(messages):
        if hasattr(msg, "content") and msg.content:
            if not hasattr(msg, "tool_calls") or not msg.tool_calls:
                return msg.content
    return ""

@tool
def composio_agent_tool(task: str) -> str:
    """
    Delegate tasks that require external tools and integrations via Composio.
    Use for: creating forms, sending emails, managing files, calendar events,
    spreadsheets, or any task requiring third-party service integration.
    
    Args:
        task: A detailed description of what to create or do
    """
    session = composio.create(user_id="user_123")
    tools   = session.tools()
    agent   = create_agent(tools=tools, model=model)
    
    result  = agent.invoke({
        "messages": [("user", task)]
    })
    
    messages = result.get("messages", [])
    for msg in reversed(messages):
        if hasattr(msg, "content") and msg.content:
            if not hasattr(msg, "tool_calls") or not msg.tool_calls:
                return msg.content
    return ""

# @tool
# def composio_agent_tool(task: str) -> str:
#     """
#     Delegate tasks that require external tools and integrations via Composio.
#     Use for: creating forms, sending emails, managing files, calendar events,
#     spreadsheets, or any task requiring third-party service integration.
    
#     Args:
#         task: A detailed description of what to create or do
#     """
#     session = composio.create(user_id="user_123")
#     tools   = session.tools()
#     agent   = create_agent(tools=tools, model=llm)
    
#     result  = agent.invoke({
#         "messages": [("user", task)]
#     })
    
#     messages = result.get("messages", [])
#     for msg in reversed(messages):
#         if hasattr(msg, "content") and msg.content:
#             if not hasattr(msg, "tool_calls") or not msg.tool_calls:
#                 return msg.content
#     return ""