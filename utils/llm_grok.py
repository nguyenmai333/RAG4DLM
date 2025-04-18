from openai import OpenAI
from typing import Iterator
from .query import retrive_documents
from .config import *

class GrokLLM:
    def __init__(self, model_name: str = 'grok-3-mini-latest', temperature: float = 0.0, api_key: str = None):
        self.model_name = model_name
        self.temperature = temperature
        self.client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
        self.system_prompt = """
            You are a helpful assistant for dialogue generation.
            Your task is to generate a response based on the user's input.
            You should be concise, relevant, and informative.
            Please avoid unnecessary details and stick to the topic.
        """

    def rag_answer(self, prompt: str) -> str:
        documents = retrive_documents(prompt)
        context = "\n".join(documents)
        return f"{self.system_prompt}\n\nUser: {prompt}\n\nContext: {context}\n\nAssistant:"

    def streaming_answer(self, prompt: str) -> Iterator[str]:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": self.rag_answer(prompt)}],
            temperature=self.temperature,
            stream=True
        )

        for chunk in response:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content