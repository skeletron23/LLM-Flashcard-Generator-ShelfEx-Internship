# llm_service.py
import os
import json
from typing import List, Optional
from openai import OpenAI
from dotenv import load_dotenv

from flashcard_model import Flashcard # Import Flashcard model

# Load environment variables (for API key)
load_dotenv()

class LLMService:
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if not self.client.api_key:
            raise ValueError("OPENAI_API_KEY not found. Please set it in a .env file or as an environment variable.")
        self.model_name = model_name

    def generate_flashcards(self, content: str, subject_type: Optional[str] = None) -> List[Flashcard]:
        """
        Generates flashcards (Q&A format) from educational content using an LLM. 
        """
        system_message = (
            "You are an expert educational assistant tasked with creating concise question-answer flashcards "
            "from the provided educational content. "
            "Generate a minimum of 10-15 flashcards. "
            "For each flashcard, ensure the question is clear and concise, and the answer is factually correct and self-contained.  "
            "If possible, identify a relevant topic/section from the text for each flashcard.  "
            "Output the flashcards as a JSON array, where each object has 'question' (string), 'answer' (string), "
            "and 'topic' (string, or null if no clear topic is found). "
            "Do not include any other text or explanation outside the JSON array."
        )

        user_message = f"Educational Content:\n\n{content}"
        if subject_type: # Subject-type selection to guide prompt formatting. 
            user_message = f"Subject: {subject_type}\n\n" + user_message

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                response_format={"type": "json_object"} # Ensure JSON output
            )

            response_content = response.choices[0].message.content
            json_output = json.loads(response_content)

            if isinstance(json_output, dict) and "flashcards" in json_output:
                flashcards_data = json_output["flashcards"]
            elif isinstance(json_output, list):
                flashcards_data = json_output
            else:
                raise ValueError(f"LLM response not in expected JSON array or object format: {json_output}")

            flashcards = []
            for item in flashcards_data:
                question = item.get("question")
                answer = item.get("answer")
                topic = item.get("topic")

                if question and answer: # Only create flashcard if Q&A are present
                    flashcards.append(Flashcard(question=question, answer=answer, topic=topic))
                else:
                    print(f"Skipping malformed flashcard item: {item}")

            if len(flashcards) < 10: # A minimum of 10-15 flashcards per input submission. 
                print(f"Warning: Only {len(flashcards)} flashcards generated. Expected at least 10-15.")

            return flashcards

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from LLM response: {e}")
            print(f"LLM raw response: {response.choices[0].message.content if 'response' in locals() else 'No response content available'}")
            return []
        except Exception as e:
            print(f"An error occurred during flashcard generation: {e}")
            return []