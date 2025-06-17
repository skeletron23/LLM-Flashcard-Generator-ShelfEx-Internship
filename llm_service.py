# llm_service.py
import os
from dotenv import load_dotenv
import google.generativeai as genai
import json # Import json for parsing the model's output

# Load environment variables from .env file
load_dotenv()

class LLMService:
    def __init__(self):
        # Gemini API Key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set. Please add it to your Streamlit Cloud secrets.")

        # Configure the Google Generative AI client
        genai.configure(api_key=api_key)
        self.client = genai

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
            {{
                "question": "...",
                "answer": "...",
                "topic": "..."
            }},
            {{
                "question": "...",
                "answer": "...",
                "topic": "..."
            }}
        ]
        Ensure the output is a valid JSON array of objects.
        """

        # Define the user message based on the input content and optional subject type
        user_message_content = f"Generate flashcards from the following content:\n\n{content}"
        if subject_type:
            user_message_content = f"Generate flashcards for a {subject_type} subject from the following content:\n\n{content}"

        messages = [
            {"role": "user", "parts": [system_message_content]}, # System instructions as first user part
            {"role": "model", "parts": ["Okay, I will generate flashcards based on the provided content."]},
            {"role": "user", "parts": [user_message_content]}
        ]

        try:
            # Call the Gemini API
            model = self.client.GenerativeModel('gemini-pro') # Using gemini-pro for text generation
            
            response = model.generate_content(
                messages,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7, # Adjust creativity as needed
                    response_mime_type="application/json" # Request JSON output
                )
            )

            # Parse the JSON response
            flashcards_json = response.text
            
            # Gemini sometimes wraps JSON in markdown, so attempt to clean it
            if flashcards_json.strip().startswith("```json") and flashcards_json.strip().endswith("```"):
                flashcards_json = flashcards_json.strip()[7:-3].strip()
            
            flashcards = json.loads(flashcards_json)

            # Basic validation of flashcard structure
            if not isinstance(flashcards, list):
                raise ValueError("LLM did not return a valid JSON array or a parsable JSON string.")
            
            for card in flashcards:
                if not all(k in card for k in ["question", "answer", "topic"]):
                    # Ensure 'topic' is also present as per the prompt
                    raise ValueError("Flashcard missing 'question', 'answer', or 'topic'.")
            return flashcards

        except Exception as e:
            print(f"Error generating flashcards with Gemini: {e}")
            return []
