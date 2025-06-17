# flashcard_model.py
import csv
import json
import io
from typing import List, Dict, Optional

class Flashcard:
    def __init__(self, question: str, answer: str, topic: Optional[str] = None, difficulty: Optional[str] = None):
        self.question = question
        self.answer = answer
        self.topic = topic  # Bonus: Auto-group flashcards under detected topic headers or sections. 
        self.difficulty = difficulty # Bonus: Add difficulty levels. 

    def to_dict(self):
        return {
            "question": self.question,
            "answer": self.answer,
            "topic": self.topic,
            "difficulty": self.difficulty
        }

    def __str__(self):
        return f"Q: {self.question}\nA: {self.answer}"

    def to_anki_cloze(self) -> str:
        """Converts the flashcard to Anki cloze deletion format (simplified for now)."""
        return f"{{c1::{self.question}}}:: {self.answer}"

def flashcards_to_csv(flashcards: List[Flashcard]) -> str:
    """Converts a list of Flashcard objects to a CSV string."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Question", "Answer", "Topic", "Difficulty"]) # Header row
    for card in flashcards:
        writer.writerow([card.question, card.answer, card.topic, card.difficulty])
    return output.getvalue()

def flashcards_to_json(flashcards: List[Flashcard]) -> str:
    """Converts a list of Flashcard objects to a JSON string."""
    return json.dumps([card.to_dict() for card in flashcards], indent=2)