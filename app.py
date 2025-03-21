import os
import json
from flask import Flask, request, jsonify, render_template, session
import uuid
import sys

print("Starting LinguaLift AI application...")

# Add the current directory to the path so we can import the conversation_engine module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Import the LinguaLiftAI class
try:
    from conversation_engine import LinguaLiftAI
except ImportError:
    # If we can't import from the module, define it here as a fallback
    class LinguaLiftAI:
        def __init__(self):
            print("Initializing LinguaLift AI...")
            # Load conversation data - using relative paths
            self.topics = self._load_json_file('linguaLift-topics-json.json')
            self.responses = self._load_json_file('linguaLift-responses-json.json')
            self.corrections = self._load_json_file('linguaLift-corrections-json.json')
            self.grammar_rules = self._load_json_file('linguaLift-grammar-rules-json.json')
            
            # Initialize session
            self.session = {
                "user_name": "",
                "level": "beginner",  # beginner, intermediate, advanced
                "current_topic": "",
                "conversation_history": [],
                "errors_made": [],
                "session_start": self._get_current_time()
            }
        
        def _load_json_file(self, filename):
            """Load JSON file with error handling"""
            try:
                print(f"Loading file: {filename}")
                with open(filename, 'r') as file:
                    return json.load(file)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Error loading {filename}: {e}")
                if 'topics' in filename:
                    return {"beginner": [], "intermediate": []}
                elif 'responses' in filename:
                    return {}
                elif 'corrections' in filename:
                    return {}
                else:  # grammar_rules
                    return []
        
        def _get_current_time(self):
            """Get current timestamp as string"""
            from datetime import datetime
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        def greet_user(self, user_name="friend"):
            """Generate a greeting for the user"""
            self.session["user_name"] = user_name
            
            import random
            greetings = [
                f"Hello, {user_name}! I am LinguaLift AI. How are you today?",
                f"Hi {user_name}! Nice to meet you. I'm here to help you practice English.",
                f"Good day, {user_name}! Ready to practice some English together?"
            ]
            
            return random.choice(greetings)
        
        def suggest_topic(self):
            """Suggest a conversation topic based on user level"""
            import random
            level_topics = self.topics.get(self.session["level"], [])
            if not level_topics:
                level_topics = self.topics["beginner"]
            
            if not level_topics:
                return "Let's have a conversation. How are you today?"
            
            topic = random.choice(level_topics)
            self.session["current_topic"] = topic["name"]
            
            return f"Let's talk about {topic['name']}. {topic['starter_question']}"
        
        def detect_errors(self, user_input):
            """Detect basic grammar and vocabulary errors"""
            errors = []
            
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
            
            import random
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
                "timestamp": self._get_current_time()
            })
            
            # Detect any errors
            errors = self.detect_errors(user_message)
            if errors:
                self.session["errors_made"].extend(errors)
            
            # Generate appropriate response
            import random
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
                "timestamp": self._get_current_time()
            })
            
            return response_text
        
        def _generate_answer(self, question):
            """Generate an answer to user question"""
            import random
            # Simplified logic - in a real system this would use NLP
            if "how are you" in question.lower():
                return "I am doing well, thank you for asking! How about you?"
            
            elif "your name" in question.lower():
                return "My name is LinguaLift AI. I'm here to help you practice English."
            
            elif "weather" in question.lower():
                return "I don't know about the weather where you are. Can you tell me what it's like today?"
            
            else:
                # Check if we have a response for the current topic
                current_topic = self.session.get("current_topic", "")
                if current_topic in self.responses:
                    topic_responses = self.responses[current_topic]
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
            import random
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
            # Create sessions directory if it doesn't exist
            os.makedirs('sessions', exist_ok=True)
            
            # Save session data
            try:
                with open(f'sessions/{user_id}.json', 'w') as file:
                    json.dump(self.session, file, indent=4)
                return True
            except Exception as e:
                print(f"Error saving session: {e}")
                return False
        
        def load_session(self, user_id):
            """Load session data for returning user"""
            try:
                with open(f'sessions/{user_id}.json', 'r') as file:
                    self.session = json.load(file)
                return True
            except FileNotFoundError:
                return False

# Initialize chatbot
print("Initializing chatbot...")
chatbot = LinguaLiftAI()
print("Chatbot initialized successfully!")

# Flask routes
@app.route('/')
def index():
    """Render the main chat interface"""
    print("Rendering index page...")
    # Generate a user ID if not exists
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    return render_template('index.html')

@app.route('/api/start_session', methods=['POST'])
def start_session():
    """Start a new chat session or load existing one"""
    print("Starting session...")
    data = request.json
    user_name = data.get('user_name', 'friend')
    user_id = session.get('user_id')
    
    # Try to load existing session
    if chatbot.load_session(user_id):
        greeting = f"Welcome back, {chatbot.session['user_name']}! Let's continue practicing English."
    else:
        # New session
        greeting = chatbot.greet_user(user_name)
    
    return jsonify({
        'message': greeting,
        'topic_suggestion': chatbot.suggest_topic()
    })

@app.route('/api/send_message', methods=['POST'])
def send_message():
    """Process user message and return response"""
    print("Receiving message...")
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Get chatbot response
    response = chatbot.respond_to_message(user_message)
    
    # Save session
    chatbot.save_session(session.get('user_id'))
    
    return jsonify({
        'response': response
    })

@app.route('/api/change_topic', methods=['POST'])
def change_topic():
    """Change the conversation topic"""
    print("Changing topic...")
    new_topic = chatbot.suggest_topic()
    
    return jsonify({
        'topic_suggestion': new_topic
    })

@app.route('/api/get_vocabulary', methods=['GET'])
def get_vocabulary():
    """Get vocabulary list for current topic"""
    print("Getting vocabulary...")
    current_topic = chatbot.session.get('current_topic', '')
    
    vocabulary = []
    for topic_category in chatbot.topics.values():
        for topic in topic_category:
            if topic['name'] == current_topic:
                vocabulary = topic.get('vocabulary', [])
                break
    
    return jsonify({
        'topic': current_topic,
        'vocabulary': vocabulary
    })

# For debugging purposes, add a test route
@app.route('/test')
def test():
    return "LinguaLift AI is running!"

if __name__ == '__main__':
    print("Flask app is starting on http://127.0.0.1:5000")
    # Create necessary directories
    os.makedirs('sessions', exist_ok=True)
    
    # Start the Flask app
    app.run(debug=True)
    print("Flask app has started!")