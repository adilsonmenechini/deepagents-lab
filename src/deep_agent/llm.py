from langchain.chat_models import init_chat_model
from deep_agent.settings import settings


llm = init_chat_model(
    model=settings.model,
    temperature=settings.temperature,
    api_key=settings.api_key,
    base_url=settings.base_url,
)
