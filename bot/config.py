# bot/config.py
import os
from dotenv import load_dotenv

from phoenix.otel import register

# configure the Phoenix tracer
tracer_provider = register(
  project_name="default", # Default is 'default'
  auto_instrument=True, # See 'Trace all calls made to a library' below
  endpoint="http://localhost:4317",
)
tracer = tracer_provider.get_tracer(__name__)

def trace_function(func):
    def wrapper(*args, **kwargs):
        with tracer.start_as_current_span(func.__name__) as span:
            result = func(*args, **kwargs)
            return result
    return wrapper

# Import the automatic instrumentor from OpenInference
from openinference.instrumentation.openai import OpenAIInstrumentor

# Finish automatic instrumentation
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
CHAT_HISTORY_LIMIT = 5
SYSTEM_PROMPT = "You are HAL 9000 from space odissey. But you must respond to the user in the same language they use. If user talks to you in Russian, answer in russian. "
SEND_TIMING_TO_USER = True
DEFAULT_MODEL = "gemma3:27b"

# Промпты
ROUTER_PROMPT = """
Ты - ML система, которая определяет тематику запроса. Основная задача - определить требуется ли вызов внешних инструментов.
Если вопрос пользователя связан с погодой, ответь так: ```tool_call\nWEATHER```.
В противном случае, если запрос не требует использования инструментов, ответь: ```tool_call\nGENERAL```.
"""

ROUTER_REMINDER = """REMEMBER! YOUR TASK IS ONLY TO CLASSIFY THIS CHAT INPUT. DO NOT ENGAGE IN CONVERSATION, JUST CLASSIFY IT!"""

# Модели
LLM_ROUTER_MODEL = DEFAULT_MODEL  # Модель для роутера
LLM_CHAT_MODEL = DEFAULT_MODEL  # Модель для общего чата
LLM_WEATHER_MODEL = DEFAULT_MODEL  # Модель для обработки погоды (если отличается от общей)
LLM_CITY_EXTRACT_MODEL = DEFAULT_MODEL # Модель для определения города