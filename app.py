from flask import Flask, request, jsonify, render_template
import re
from spellchecker import SpellChecker

app = Flask(__name__)


# Initialize the spell checker
spell = SpellChecker()

# Define a dictionary of responses for general chatting
response_dict = {
    "hello": "Hi there! How can I assist you today?",
    "hi": "Hello! How can I help you?",
    "hey": "Hey! What can I do for you?",
    "how are you": "I'm just a bot, but I'm here to help! How can I assist you?",
    "what's your name": "I'm a banking chatbot. How can I assist you today?",
    "thank you": "You're welcome! If you need anything else, just let me know.",
    "bye": "Goodbye! Have a great day!",
    "welcome": "Welcome! How can I assist you today?",
}

# Simulated in-memory database
credit_card_db = {
    1: {
        'name': 'Rajendra',
        'card_number': '12345',
        'expiry_date': '2025-12-31',
        'penalty_amount': 50.0
    },
    2: {
        'name': 'Raja',
        'card_number': '6789',
        'expiry_date': '2024-06-30',
        'penalty_amount': 30.0
    }
}

def correct_spelling(text):
    # Tokenize the text and correct each word
    words = text.split()
    corrected_words = [spell.correction(word) for word in words]
    return ' '.join(corrected_words)

def extract_info(text):
    user_id = re.search(r'user\s*id\s*(\d+)', text, re.IGNORECASE)
    card_number = re.search(r'card\s*number\s*(\d+)', text)
    name = re.search(r'for\s*(\w+)', text)
    return user_id, card_number, name

def find_user_id(user_id, card_number, name):
    if user_id:
        return int(user_id.group(1))
    if card_number:
        return get_user_id_by_card_number(card_number.group(1))
    if name:
        return get_user_id_from_db(name.group(1))
    return None

def get_user_id_from_db(name):
    for user_id, details in credit_card_db.items():
        if details['name'].lower() == name.lower():
            return user_id
    return None

def get_user_id_by_card_number(card_number):
    for user_id, details in credit_card_db.items():
        if details['card_number'] == card_number:
            return user_id
    return None

def get_custom_response(user_input):
    corrected_input = correct_spelling(user_input).lower().strip()
    cleaned_input = re.sub(r'[^\w\s]', '', corrected_input)

    for key, response in response_dict.items():
        if key in cleaned_input:
            return response
    
    user_id, card_number, name = extract_info(cleaned_input)
    user_id = find_user_id(user_id, card_number, name)

    if "expiry" in cleaned_input:
        if user_id in credit_card_db:
            return f"Your credit card expiry date is {credit_card_db[user_id]['expiry_date']}."
        return "What is your user ID, name, or card number to check the expiry date."

    if "penalty" in cleaned_input:
        if user_id in credit_card_db:
            return f"The penalty amount is ${credit_card_db[user_id]['penalty_amount']}."
        return "What is your user ID, name, or card number to check the penalty details."

    return "Sorry, I didn't understand that. Can you please rephrase?"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.json.get('message')
    response = get_custom_response(user_input)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
