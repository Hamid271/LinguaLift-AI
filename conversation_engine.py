import json
import random
from datetime import datetime

class LinguaLiftAI:
    def __init__(self):
        # Load conversation data
        with open('data/topics.json', 'r') as file:
            self.topics = json.load(file)
        
        with open('data/responses.json', 'r') as file:
            self.responses = json.load(file)
        
        with open('data/corrections.json', 'r') as file:
            self.corrections = json.load(file)
        
        with open('data/grammar_rules.json', 'r') as file:
            self.grammar_rules = json.load(file)
        
        # Initialize session
        self.session = {
            "user_name": "",
            "level": "beginner",  # beginner, intermediate, advanced
            "current_topic": "",
            "conversation_history": [],
            "errors_made": [],
            "session_start": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def greet_user(self, user_name="friend"):
        """Generate a greeting for the user"""
        self.session["user_name"] = user_name
        
        greetings = [
            f"Hello, {user_name}! I am LinguaLift AI. How are you today?",
            f"Hi {user_name}! Nice to meet you. I'm here to help you practice English.",
            f"Good day, {user_name}! Ready to practice some English together?"
        ]
        
        return random.choice(greetings)
    
    def suggest_topic(self):
        """Suggest a conversation topic based on user level"""
        level_topics = self.topics.get(self.session["level"], [])
        if not level_topics:
            level_topics = self.topics["beginner"]
        
        topic = random.choice(level_topics)
        self.session["current_topic"] = topic["name"]
        
        return f"Let's talk about {topic['name']}. {topic['starter_question']}"
    
    def detect_errors(self, user_input):
        """Detect basic grammar and vocabulary errors"""
        errors = []
        
        # Simple error detection examples
        words = user_input.lower().split()
        
        # Check for common grammar errors
        for rule in self.grammar_rules:
            if rule["pattern"] in user_input.lower():
                errors.append({
                    "type": "grammar",
                    "error": rule["pattern"],
                    "correction": rule["correction"],
                    "explanation": rule["explanation"]
                })
        
        return errors
    
    def generate_correction(self, errors):
        """Generate friendly correction based on detected errors"""
        if not errors:
            return ""
        
        # Choose just one error to correct (not overwhelming)
        error = random.choice(errors)
        
        correction_templates = [
            f"I noticed something small: '{error['error']}' can be '{error['correction']}'. {error['explanation']}",
            f"Just a tiny tip: Try saying '{error['correction']}' instead of '{error['error']}'. {error['explanation']}",
            f"You're doing great! One small suggestion: '{error['error']}' → '{error['correction']}'. {error['explanation']}"
        ]
        
        return random.choice(correction_templates)
    
    def respond_to_message(self, user_message):
        """Main function to process user input and generate response"""
        # Add to conversation history
        self.session["conversation_history"].append({
            "user": user_message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Detect any errors
        errors = self.detect_errors(user_message)
        if errors:
            self.session["errors_made"].extend(errors)
        
        # Generate appropriate response
        if "?" in user_message:
            # It's a question, find an appropriate answer
            response_text = self._generate_answer(user_message)
        else:
            # It's a statement, acknowledge and continue conversation
            response_text = self._acknowledge_and_continue(user_message)
        
        # Add correction if there are errors
        correction = self.generate_correction(errors)
        if correction:
            response_text = f"{response_text}\n\n{correction}"
        
        # Add to conversation history
        self.session["conversation_history"].append({
            "bot": response_text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        return response_text
    
    def _generate_answer(self, question):
        """Generate an answer to user question"""
        # Simplified logic - in a real system this would use NLP
        if "how are you" in question.lower():
            return "I am doing well, thank you for asking! How about you?"
        
        elif "your name" in question.lower():
            return "My name is LinguaLift AI. I'm here to help you practice English."
        
        elif "weather" in question.lower():
            return "I don't know about the weather where you are. Can you tell me what it's like today?"
        
        else:
            # Check if we have a response for the current topic
            if self.session["current_topic"] in self.responses:
                topic_responses = self.responses[self.session["current_topic"]]
                return random.choice(topic_responses)
            else:
                # Generic responses if no topic match
                generic = [
                    "That's interesting! Can you tell me more?",
                    "I understand. What else would you like to talk about?",
                    "That's good to know. Do you have any questions for me?"
                ]
                return random.choice(generic)
    
    def _acknowledge_and_continue(self, statement):
        """Acknowledge user statement and continue conversation"""
        acknowledgements = [
            "I see. ",
            "That's interesting. ",
            "Thank you for sharing. ",
            "I understand. ",
            "Good point. "
        ]
        
        follow_ups = [
            "Can you tell me more about that?",
            "How do you feel about it?",
            "Why do you think that is?",
            "What else can you share about this topic?",
            "Do you have any questions about this?"
        ]
        
        return random.choice(acknowledgements) + random.choice(follow_ups)
    
    def save_session(self, user_id):
        """Save the current session data"""
        # In a real application, this would save to a database
        with open(f'sessions/{user_id}.json', 'w') as file:
            json.dump(self.session, file, indent=4)
        
        return True
    
    def load_session(self, user_id):
        """Load session data for returning user"""
        try:
            with open(f'sessions/{user_id}.json', 'r') as file:
                self.session = json.load(file)
            return True
        except FileNotFoundError:
            return False
