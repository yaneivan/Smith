# bot/router.py
import re
from openai import OpenAI
from .config import ROUTER_PROMPT, OLLAMA_BASE_URL, OLLAMA_API_KEY, LLM_ROUTER_MODEL, tracer, ROUTER_REMINDER
from .utils import colored_print
from pydantic import BaseModel
from enum import Enum

client = OpenAI(base_url=OLLAMA_BASE_URL, api_key=OLLAMA_API_KEY)

class RouteChoiceOptions(str, Enum):
    general = "general"
    weather = "weather"

class RouterChoice(BaseModel):
    choice: RouteChoiceOptions

async def route_request(messages: list):
    with tracer.start_as_current_span("router", openinference_span_kind="chain") as route:
        router_messages = [{"role": "system", "content": ROUTER_PROMPT}]
        router_messages.extend(messages)

        route.set_input(router_messages)
        completion = client.beta.chat.completions.parse(
            model=LLM_ROUTER_MODEL,
            messages=router_messages + [{"role": "system", "content": ROUTER_REMINDER}],
            temperature=0.1,
            response_format=RouterChoice
        )

        response_content = completion.choices[0].message.parsed
        colored_print(f"Router response: {response_content}", "magenta")

        return response_content.choice