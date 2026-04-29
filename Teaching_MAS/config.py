import os
from datetime import datetime
from langchain.chat_models import init_chat_model
from tavily import TavilyClient
import requests
from dotenv import load_dotenv
load_dotenv()

# ── API Keys — ضعها في environment variables للأمان ──
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
GROQ_API_KEY   = os.environ.get("GROQ_API_KEY")
mistral_api_key = os.environ.get("MISTRAL_API_KEY")
os.environ.get("LANGSMITH_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "new"
os.environ.get("LANGSMITH_API_KEY")

# ── Clients ──
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
COMPOSIO_API_KEY=os.environ.get("COMPOSIO_API_KEY")


# llm = init_chat_model(model="openrouter:openai/gpt-4o ", temperature=0.0,api_key=openrouter_api_key)



# model = init_chat_model(model="openrouter:openai/gpt-4o ", temperature=0.0,api_key=openrouter_api_key)
# ── Model ──


model = init_chat_model(
    model="groq:openai/gpt-oss-safeguard-20b",
    # model="ollama:gemma4:31b-cloud",
    temperature=0,
    # model_provider="groq",
    api_key=GROQ_API_KEY,
    max_tokens=2000
)

model2 = init_chat_model(
    model="groq:openai/gpt-oss-120b",
    # model="ollama:gemma4:31b-cloud",
    temperature=0,
    # model_provider="",
    api_key=GROQ_API_KEY,
    max_tokens=2000
)
# ── Date ──
def get_current_date() -> str:
    try:
        r  = requests.get("https://worldtimeapi.org/api/ip", timeout=3)
        dt = datetime.fromisoformat(r.json()["datetime"])
        return dt.strftime("%B %d, %Y")
    except Exception:
        return datetime.now().strftime("%B %d, %Y")

TODAY = get_current_date()
