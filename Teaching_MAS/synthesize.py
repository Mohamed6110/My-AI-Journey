
import os
from typing import Literal,Annotated,Callable
from typing_extensions import Annotated, TypedDict, Literal
from typing_extensions import TypedDict
from langchain.tools import tool
from langgraph.graph import StateGraph,MessagesState,START,END
from langgraph.types import Send
from pydantic import BaseModel,Field
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage,SystemMessage
import operator
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
from teacher import teacher_agent
from teacher_assistant import teacher_assistant_agent
from planner import planner_agent
from config import *




ROUTER_SYSTEM_PROMPT =  """                                                                                         
     You are a routing agent. Analyze the query and return ONLY this JSON:

{"classifications": [{"source": "teacher", "query": "the question"}]}

Rules:
- "teacher"           → theory, concepts, explanations, definitions
- "teacher_assistant" → code, debugging, implementation, technical errors  
- "planner"           → roadmaps, study plans, schedules, learning paths
- Pick ONE agent only
- Return ONLY the JSON, nothing else
If a request requires more agents than are currently assigned, assign additional agents to it
Valid source values: "teacher", "teacher_assistant", "planner"
"""                                                                                                                                                                                                                                                 
      





# ================================================================
# STATE SCHEMAS  — single source of truth, consistent key names
# ================================================================

class AgentInput(TypedDict):
    """Input passed to each agent node"""
    query: str

class AgentOutput(TypedDict):
    """Output collected from each agent node"""
    source: str
    result: str

class Classification(TypedDict):
    """A single routing decision"""
    source: Literal["teacher", "teacher_assistant", "planner"]
    query: str

class RouterState(TypedDict):
    query: str
    classifications: list[Classification]          
    results: Annotated[list[AgentOutput], operator.add]  
    final_answer: str

class ClassificationResult(BaseModel):
    """Structured output from the classifier LLM"""
    classifications: list[Classification] = Field(
        description="List of agents to invoke with their targeted sub-questions"
    )



SMALL_TALK = {"hi", "hello", "hey", "thanks", "thank you", "ok", "okay", "bye", "good", "nice", "cool"}

# ================================================================
# CLASSIFIER NODE — fixed
# ================================================================

# def classify_query(state: RouterState) -> dict:
#     query = state["query"].strip().lower()

#     # bypass LLM entirely for small talk
#     if query in SMALL_TALK or len(query.split()) <= 1:
#         return {
#             "classifications": [],
#             "final_answer": "Hello! How can I help you today?"
#         }

#     structured_llm = router_llm.with_structured_output(ClassificationResult)

#     result = structured_llm.invoke([
#         {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
#         {"role": "user",   "content": state["query"]}
#     ])

#     return {"classifications": result.classifications}

import json
import re

def classify_query(state: RouterState) -> dict:
    query = state["query"].strip().lower()

    # ✅ small talk bypass
    if query in SMALL_TALK or len(query.split()) <= 1:
        return {
            "classifications": [],
            "final_answer": "Hello! How can I help you today?"
        }

    # ✅ بدل with_structured_output — استخدم plain invoke + JSON parsing
    messages = [
        {
            "role": "system",
            "content": ROUTER_SYSTEM_PROMPT + """

CRITICAL: Return ONLY a valid JSON object. No markdown, no explanation, no code blocks.
Exactly this format:
{"classifications": [{"source": "teacher", "query": "the question"}]}

Valid source values: "teacher", "teacher_assistant", "planner"
"""
        },
        {
            "role": "user",
            "content": state["query"]
        }
    ]

    try:
        response = model2.invoke(messages)
        raw = response.content.strip()

        # ✅ نظف الـ response من markdown لو موجود
        raw = re.sub(r"```json|```", "", raw).strip()

        # ✅ parse الـ JSON
        parsed = json.loads(raw)
        classifications = parsed.get("classifications", [])

        # ✅ validate
        valid_sources = {"teacher", "teacher_assistant", "planner"}
        classifications = [
            c for c in classifications
            if c.get("source") in valid_sources and c.get("query")
        ]

        # ✅ fallback لو فاضي
        if not classifications:
            classifications = [{"source": "teacher", "query": state["query"]}]

        print(f"🧭 [Router] → {[c['source'] for c in classifications]}")
        return {"classifications": classifications}

    except json.JSONDecodeError as e:
        print(f"⚠️ [Router] JSON parse failed: {e} — raw: {raw[:100]}")
        # ✅ fallback — روح للـ teacher دايماً
        return {
            "classifications": [{"source": "teacher", "query": state["query"]}]
        }
    except Exception as e:
        print(f"❌ [Router] Error: {e}")
        return {
            "classifications": [{"source": "teacher", "query": state["query"]}]
        }
# ================================================================
# ROUTING FUNCTION
# ================================================================

AGENT_NODE_MAP = {
    "teacher":     "teacher",        # 
    "teacher_assistant": "teacher_assistant",
    "planner":           "planner",
}

def route_to_agents(state: RouterState) -> list[Send]:
    return [
        Send(AGENT_NODE_MAP.get(c["source"], c["source"]), {"query": c["query"]})
        for c in state["classifications"]
    ]


def query_teacher(state: AgentInput) -> dict:
    print(" [Teacher] Agent started — query:", state["query"][:50])  
    config = {"configurable": {"thread_id": "teacher_session"}}
    full_response = ""

    result = teacher_agent.invoke(
        {"messages": [{"role": "user", "content": state["query"]}]},
        config=config
    )

    messages = result.get("messages", [])
    for msg in reversed(messages):
        if hasattr(msg, "content") and msg.content:
            if not hasattr(msg, "tool_calls") or not msg.tool_calls:
                full_response = msg.content
                break

    print(f" [Teacher] Agent finished — response length: {len(full_response)}") 
    return {"results": [{"source": "teacher", "result": full_response}]}


def query_teacher_assistant(state: AgentInput) -> dict:
    print(" [Teacher_Assistant] Agent started — query:", state["query"][:50]) 
    config = {"configurable": {"thread_id": "assistant_session"}}
    full_response = ""

    result = teacher_assistant_agent.invoke(
        {"messages": [{"role": "user", "content": state["query"]}]},
        config=config
    )

    messages = result.get("messages", [])
    for msg in reversed(messages):
        if hasattr(msg, "content") and msg.content:
            if not hasattr(msg, "tool_calls") or not msg.tool_calls:
                full_response = msg.content
                break

    print(f" [Teacher_Assistant] Agent finished — response length: {len(full_response)}") 
    return {"results": [{"source": "teacher_assistant", "result": full_response}]}


def query_planner(state: AgentInput) -> dict:
    print(" [Planner] Agent started — query:", state["query"][:50])  
    config = {"configurable": {"thread_id": "planner_session"}}
    full_response = ""

    result = planner_agent.invoke(
        {"messages": [{"role": "user", "content": state["query"]}]},
        config=config
    )

    messages = result.get("messages", [])
    for msg in reversed(messages):
        if hasattr(msg, "content") and msg.content:
            if not hasattr(msg, "tool_calls") or not msg.tool_calls:
                full_response = msg.content
                break

    print(f"[Planner] Agent finished — response length: {len(full_response)}")  
    return {"results": [{"source": "planner", "result": full_response}]}



# ================================================================
# SYNTHESIZE — fixed
# ================================================================
def synthesize_results(state: RouterState) -> dict:
    print(f"\n [Synthesize] received {len(state.get('results', []))} result(s)")  
    for r in state.get("results", []):
        print(f"   - {r['source']}: {len(r['result'])} chars") 
    #  already answered upstream (small talk)
    if state.get("final_answer"):
        return {"final_answer": state["final_answer"]}

    results = state.get("results", [])

    if not results:
        return {"final_answer": "I could not find an answer. Please try rephrasing."}

    # single result — return directly, no synthesis needed
    if len(results) == 1:
        return {"final_answer": results[0]["result"]}

    #  multiple results — synthesize using llm 
    formatted = "\n\n---\n\n".join([
        f"[{r['source'].upper()}]\n{r['result']}"
        for r in results
    ])

    messages = [
        {
            "role": "system",
            "content": (
                "You are a synthesis expert. "
                "You will receive outputs from multiple educational agents. "
                "Combine them into one clear, unified, non-redundant response. "
                "Do not mention agent names. Write all agent outputs."
                "Do not summarize or remove any details and do not add any new information from your data."
            )
        },
        {
            "role": "user",
            "content": f"Original question: {state['query']}\n\n{formatted}"
        }
    ]

    full_response = ""
    for chunk in model2.stream(messages): 
        if chunk.content:
            full_response += chunk.content

    return {"final_answer": full_response}


workflow = (
    StateGraph(RouterState)
    .add_node("classify",          classify_query)
    .add_node("teacher",           query_teacher)
    .add_node("teacher_assistant", query_teacher_assistant)
    .add_node("planner",           query_planner)
    .add_node("synthesize",        synthesize_results)  

    .add_edge(START, "classify")   

    .add_conditional_edges(
        "classify",
        route_to_agents,
        ["teacher", "teacher_assistant", "planner", "synthesize"],
    )

    
    .add_edge("teacher",           "synthesize")
    .add_edge("teacher_assistant", "synthesize")
    .add_edge("planner",           "synthesize")

    .add_edge("synthesize", END)  

    .compile()
)
