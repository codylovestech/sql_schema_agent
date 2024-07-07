import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
from langchain_groq import ChatGroq

def get_chat(model="llama3-8b-8192", temperature=0.3):

    chat = ChatGroq(
        temperature=temperature,
        model=model,
        api_key=GROQ_API_KEY
    )
    return chat