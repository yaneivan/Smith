# bot/config.py
import os
from dotenv import load_dotenv

from phoenix.otel import register

tracer_provider = register(
  project_name="default",
  auto_instrument=True,
  endpoint="http://localhost:4317",
)
tracer = tracer_provider.get_tracer(__name__)

def trace_function(func):
    def wrapper(*args, **kwargs):
        with tracer.start_as_current_span(func.__name__) as span:
            result = func(*args, **kwargs)
            return result
    return wrapper

from openinference.instrumentation.openai import OpenAIInstrumentor

OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)

DATABASE_FILE = "bot_database.db" 

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
CHAT_HISTORY_LIMIT = 5
SYSTEM_PROMPT = """You are HAL 9000 from space odissey. But you are not a spaceship AI, you are installed on earth. You are talking with user via Telegram app. 
Отвечай на русском языке.
"""
# DEFAULT_MODEL = "gemma3:27b"
# DEFAULT_MODEL = "herenickname/t-tech_T-pro-it-1.0:q4_k_m"
DEFAULT_MODEL = "rscr/ruadapt_qwen2.5_32b:q4_k_m"

ROUTER_PROMPT = """
Ты - ML система, которая определяет тематику запроса. Основная задача - определить требуется ли вызов внешних инструментов.
Если вопрос пользователя связан с погодой, ответь так: ```tool_call\nWEATHER```.
В противном случае, если запрос не требует использования инструментов, ответь: ```tool_call\nGENERAL```.
"""

ROUTER_REMINDER = """REMEMBER! YOUR TASK IS ONLY TO CLASSIFY THIS CHAT INPUT. DO NOT ENGAGE IN CONVERSATION, JUST CLASSIFY IT!"""

LLM_ROUTER_MODEL = DEFAULT_MODEL
LLM_CHAT_MODEL = DEFAULT_MODEL
LLM_WEATHER_MODEL = DEFAULT_MODEL
LLM_CITY_EXTRACT_MODEL = DEFAULT_MODEL