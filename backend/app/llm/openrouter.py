from langchain_openai import ChatOpenAI
from app.config.settings import settings

def get_openrouter_llm():

    llm = ChatOpenAI(
        model="deepseek/deepseek-chat-v3-0324:free",
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.OPENROUTER_API_KEY
    )

    return llm