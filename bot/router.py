# bot/router.py
import re
from openai import OpenAI
from .config import ROUTER_PROMPT, OLLAMA_BASE_URL, OLLAMA_API_KEY, LLM_ROUTER_MODEL, tracer, trace_function, ROUTER_REMINDER
from .utils import colored_print

client = OpenAI(base_url=OLLAMA_BASE_URL, api_key=OLLAMA_API_KEY)

# @tracer.start_as_current_span("route_request")
async def route_request(messages: list):  # Принимаем список сообщений
    with tracer.start_as_current_span("router", openinference_span_kind="chain") as route:
        # Добавляем системный промпт для роутера
        router_messages = [{"role": "system", "content": ROUTER_PROMPT}]
        router_messages.extend(messages) # Добавляем всю историю

        route.set_input(router_messages)
        completion = client.chat.completions.create(
            model=LLM_ROUTER_MODEL,  # Используем модель из конфига
            messages=router_messages + [{"role": "system", "content": ROUTER_REMINDER}],
            temperature=0  # Устанавливаем температуру 0
        )

        response_content = completion.choices[0].message.content.strip()
        colored_print(f"Router response: {response_content}", "magenta")
        # Используем regex для поиска tool_call
        match = re.search(r"```tool_call\n(\w+)```", response_content)
        if match:
            route.set_output(match.group(1))
            tool_name = match.group(1)
            if tool_name == "WEATHER":
                return "weather"
            else:
                return "general"
        else:
            return "general"