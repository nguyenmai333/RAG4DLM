# utils/llm_deepseek.py
from openai import OpenAI
from typing import Iterator
from .query import retrive_documents
from .config import *

class DeepseekLLM:
    def __init__(self, model_name: str = 'deepseek-chat', temperature: float = 0.0, api_key: str = None):
        self.model_name = model_name
        self.temperature = temperature
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        self.system_prompt = """
            You are a helpful assistant for dialogue generation.
            Your task is to generate a response based on the user's input.
            You should be concise, relevant, and informative.
            Please avoid unnecessary details and stick to the topic.
        """

    def rag_answer(self, prompt: str) -> str:
        documents = retrive_documents(prompt)
        context = "\n".join(documents)
        full_prompt = f"{self.system_prompt}\n\nUser: {prompt}\n\nContext: {context}\n\nAssistant:"
        return full_prompt

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