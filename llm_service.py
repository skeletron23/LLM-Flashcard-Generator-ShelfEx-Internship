# llm_service.py
import os
from dotenv import load_dotenv
from openai import OpenAI
import httpx # This import is crucial for the proxy fix

# Load environment variables from .env file
load_dotenv()

class LLMService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set. Please create a .env file with OPENAI_API_KEY='your_api_key_here'.")

        # Temporarily clear proxy environment variables for the current process
        # This is a robust way to ensure httpx does not pick up unexpected proxy settings.
        original_http_proxy = os.environ.pop("HTTP_PROXY", None)
        original_https_proxy = os.environ.pop("HTTPS_PROXY", None)
        original_no_proxy = os.environ.pop("NO_PROXY", None)
        original_http_proxy_lower = os.environ.pop("http_proxy", None)
        original_https_proxy_lower = os.environ.pop("https_proxy", None)
        original_no_proxy_lower = os.environ.pop("no_proxy", None)

        configured_http_client = None
        try:
            # --- LAST RESORT: TRYING A BARE HTTPX CLIENT INITIALIZATION ---
            # If proxies={} or other arguments are triggering an internal httpx proxy detection,
            # this might bypass it.
            configured_http_client = httpx.Client()
        except Exception as e:
            # Fallback if even a bare httpx.Client() fails
            print(f"Warning: Could not initialize a bare httpx.Client: {e}. Proceeding without explicit httpx client configuration.")
            configured_http_client = None

        # Initialize OpenAI client. Only pass http_client if it was successfully configured.
        if configured_http_client:
            self.client = OpenAI(
                api_key=api_key,
                http_client=configured_http_client # Pass the configured httpx client
            )
        else:
            # Fallback: Initialize OpenAI without an explicit http_client if configuration failed
            self.client = OpenAI(
                api_key=api_key
            )

        # Restore original environment variables after client initialization (optional, but good practice)
        if original_http_proxy is not None:
            os.environ["HTTP_PROXY"] = original_http_proxy
        if original_https_proxy is not None:
            os.environ["HTTPS_PROXY"] = original_https_proxy
        if original_no_proxy is not None:
            os.environ["NO_PROXY"] = original_no_proxy
        if original_http_proxy_lower is not None:
            os.environ["http_proxy"] = original_http_proxy_lower
        if original_https_proxy_lower is not None:
            os.environ["https_proxy"] = original_https_proxy_lower
        if original_no_proxy_lower is not None:
            os.environ["no_proxy"] = original_no_proxy_lower

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
            {"role": "system", "content": system_message_content},
            {"role": "user", "content": user_message_content}
        ]

        try:
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Or "gpt-4", "gpt-4o" if you have access and prefer
                response_format={"type": "json_object"}, # Ensure JSON output
                messages=messages,
                temperature=0.7 # Adjust creativity as needed
            )
            # Parse the JSON response
            flashcards_json = response.choices[0].message.content
            import json
            flashcards = json.loads(flashcards_json)

            # Basic validation of flashcard structure
            if not isinstance(flashcards, list):
                raise ValueError("LLM did not return a JSON array.")
            for card in flashcards:
                if not all(k in card for k in ["question", "answer"]):
                    raise ValueError("Flashcard missing 'question' or 'answer'.")
            return flashcards

        except Exception as e:
            print(f"Error generating flashcards: {e}")
            return []
