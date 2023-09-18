from typing import TypedDict, List

from serpapi import GoogleSearch
import openai

class Message(TypedDict):
    role: str
    content: str

class SearchAgent:
    def __init__ (self, serpapi_key):
        self.serpapi_key = serpapi_key

    def generate_query(self, context: List[Message]) -> str:
        context.extend ([
            {"role": "system", "content": "You only respond in queries generated for Google search."},
            {"role": "assistant", "content": "I need to find out the best locations to visit in 2023."},
            {"role": "user", "content": "Create a search query that will help solve the problem."},
            {"role": "assistant", "content": "best places to visit in 2023"},
        ])

        return openai.ChatCompletion.create (
            model="gpt-4-0613",
            messages=context,
            temperature=0.7,
            max_tokens=4000,
        )["choices"][0]["message"]["content"]
    
    def search_google(self, query: str) -> dict:
        engine = GoogleSearch({
            "engine": "google",
            "q": query,
            "api_key": self.serpapi_key,
        })
        return engine.get_dict()["organic_results"]
    
    