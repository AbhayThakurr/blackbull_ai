from langchain_aws import ChatBedrock
from app.config.bedrock import get_bedrock_client

def get_nova_micro():
    """
    Returns an instance of Amazon Nova Micro.
    Uses the centralized Bedrock client from config.
    """
    llm = ChatBedrock(
        model="amazon.nova-micro-v1:0",
        client=get_bedrock_client()
    )

    return llm
