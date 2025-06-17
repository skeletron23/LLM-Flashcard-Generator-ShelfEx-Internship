# llm_service.py
import os
from dotenv import load_dotenv
import openai # Changed from google.generativeai
import json

# Load environment variables from .env file
load_dotenv()

class LLMService:
    def __init__(self):
        # OpenRouter API Key
        api_key = os.getenv("OPENROUTER_API_KEY") # Changed environment variable name
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set. Please add it to your Streamlit Cloud secrets.")

        # Configure the OpenRouter client (OpenAI compatible)
        # The base_url points to OpenRouter's API
        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

    def generate_flashcards(self, content: str, subject_type: str = None) -> list:
        # Define the system message for the LLM
        system_message_content = """You are an AI assistant specialized in generating educational flashcards.
        Your task is to convert provided content into concise question-answer flashcards.
        Each flashcard should have a clear question and a factual, self-contained answer.
        Generate at least 10-15 flashcards.
        If a subject type is provided, tailor questions and answers to that domain where appropriate.
        For each flashcard, also try to identify a concise topic.

        Output format:
        [
            {
                "question": "...",
                "answer": "...",
                "topic": "..."
            },
            {
                "question": "...",
                "answer": "...",
                "topic": "..."
            }
        ]
        Ensure the output is a valid JSON array of objects.
        """

        # Define the user message based on the input content and optional subject type
        user_message_content = f"Generate flashcards from the following content:\n\n{content}"
        if subject_type:
            user_message_content = f"Generate flashcards for a {subject_type} subject from the following content:\n\n{content}"

        messages = [
            {"role": "system", "content": system_message_content}, # Changed to system role for OpenAI
            {"role": "user", "content": user_message_content}
        ]

        try:
            # Call the OpenRouter API with a Phi model
            response = self.client.chat.completions.create(
                model="microsoft/phi-4-reasoning:free", # Using the Phi-4 Reasoning model from OpenRouter
                messages=messages,
                temperature=0.7,
                response_format={"type": "json_object"} # Request JSON output for OpenAI compatible APIs
            )

            # Parse the JSON response
            flashcards_json = response.choices[0].message.content
            
            # OpenRouter should return clean JSON if response_format is set, but keep parsing robust
            if flashcards_json.strip().startswith("```json") and flashcards_json.strip().endswith("```"):
                flashcards_json = flashcards_json.strip()[7:-3].strip()
            
            flashcards = json.loads(flashcards_json)

            # Basic validation of flashcard structure
            if not isinstance(flashcards, list):
                raise ValueError("LLM did not return a valid JSON array or a parsable JSON string.")
            
            for card in flashcards:
                if not all(k in card for k in ["question", "answer", "topic"]):
                    raise ValueError("Flashcard missing 'question', 'answer', or 'topic'.")
            return flashcards

        except openai.APIStatusError as e:
            print(f"OpenRouter API Error: {e.status_code} - {e.response}")
            return []
        except Exception as e:
            print(f"Error generating flashcards with OpenRouter: {e}")
            return []
