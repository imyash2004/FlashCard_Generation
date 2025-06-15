import openai
import re
from typing import List, Dict, Optional
import traceback

class Agent:
    def __init__(self, openai_api_key: str):
        """Minimal initialization approach."""
        print(f"OpenAI library version: {openai.__version__}")
        
        if not openai_api_key:
            raise Exception("API key is required")
        
        # The most basic initialization possible
        self.client = openai.OpenAI(api_key=openai_api_key)
        
        # Quick test
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            print("✓ OpenAI client initialized successfully!")
        except Exception as e:
            raise Exception(f"Connection test failed: {e}")

    def generate_flashcards(self, text: str, subject: Optional[str] = None) -> List[Dict[str, str]]:
        """Generate flashcards from input text using OpenAI API."""
        
        subject_context = ""
        if subject and subject != "General":
            subject_context = f"Focus on {subject} concepts and terminology. "
        
        prompt = f"""You are an expert educator creating study flashcards. {subject_context}

Create exactly 10-12 high-quality flashcards from the following educational content.

STRICT FORMATTING RULES:
- Start each question with "Q:" on its own line
- Start each answer with "A:" on its own line  
- Leave a blank line between each flashcard
- Do not number the questions

Example format:
Q: What is photosynthesis?
A: Photosynthesis is the process by which plants convert light energy into chemical energy.

Q: What are the main products of photosynthesis?
A: The main products are glucose and oxygen.

Guidelines:
- Make questions clear and specific
- Make answers complete but concise (1-3 sentences)
- Cover key concepts, definitions, and important facts
- Vary question types: definitions, explanations, applications

Text to analyze:
{text[:3000]}

Generate the flashcards now:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7
            )
            content = response.choices[0].message.content.strip()
            
            flashcards = self._parse_flashcards(content)
            
            if not flashcards:
                raise Exception("No flashcards could be parsed from the response")
            
            return flashcards
            
        except Exception as e:
            print(f"Error generating flashcards: {e}")
            raise Exception(f"Failed to generate flashcards: {str(e)}")

    def _parse_flashcards(self, content: str) -> List[Dict[str, str]]:
        """Parse the AI response into structured flashcard data."""
        flashcards = []
        
        try:
            # Split by blank lines to get individual flashcards
            sections = re.split(r'\n\s*\n', content.strip())
            
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                
                # Look for Q: and A: patterns
                lines = section.split('\n')
                question = ""
                answer = ""
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('Q:'):
                        question = line[2:].strip()
                    elif line.startswith('A:'):
                        answer = line[2:].strip()
                    elif question and not answer and line:
                        question += " " + line
                    elif answer and line and not line.startswith('Q:'):
                        answer += " " + line
                
                if question and answer:
                    question = re.sub(r'\s+', ' ', question).strip()
                    answer = re.sub(r'\s+', ' ', answer).strip()
                    question = re.sub(r'^\d+\.\s*', '', question)
                    
                    if (len(question) > 5 and len(answer) > 5 and 
                        len(question) < 300 and len(answer) < 500):
                        flashcards.append({
                            "question": question,
                            "answer": answer
                        })
            
            # Fallback parsing if we got too few cards
            if len(flashcards) < 3:
                flashcards = self._fallback_parse(content)
            
            return flashcards
            
        except Exception as e:
            print(f"Error parsing flashcards: {e}")
            return []

    def _fallback_parse(self, content: str) -> List[Dict[str, str]]:
        """Fallback parsing method."""
        flashcards = []
        
        q_pattern = r'Q\d*[:.]?\s*([^QA]+?)(?=A\d*[:.])'
        a_pattern = r'A\d*[:.]?\s*([^QA]+?)(?=Q\d*[:.}]|$)'
        
        questions = re.findall(q_pattern, content, re.DOTALL | re.IGNORECASE)
        answers = re.findall(a_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for i in range(min(len(questions), len(answers))):
            q = re.sub(r'\s+', ' ', questions[i]).strip()
            a = re.sub(r'\s+', ' ', answers[i]).strip()
            
            if len(q) > 5 and len(a) > 5:
                flashcards.append({
                    "question": q,
                    "answer": a
                })
        
        return flashcards

    def assign_difficulty_levels(self, flashcards: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Assign difficulty levels to flashcards."""
        try:
            for card in flashcards:
                question = card["question"].lower()
                answer = card["answer"]
                
                difficulty_score = 0
                
                if any(word in question for word in ["what is", "define", "who is"]):
                    difficulty_score += 1
                elif any(word in question for word in ["explain", "describe", "how"]):
                    difficulty_score += 2
                elif any(word in question for word in ["analyze", "compare", "why"]):
                    difficulty_score += 3
                
                word_count = len(answer.split())
                if word_count > 30:
                    difficulty_score += 1
                
                if difficulty_score <= 2:
                    difficulty = "Easy"
                elif difficulty_score <= 3:
                    difficulty = "Medium"
                else:
                    difficulty = "Hard"
                
                card["difficulty"] = difficulty
            
            return flashcards
            
        except Exception as e:
            print(f"Error assigning difficulty levels: {e}")
            for card in flashcards:
                if "difficulty" not in card:
                    card["difficulty"] = "Medium"
            return flashcards