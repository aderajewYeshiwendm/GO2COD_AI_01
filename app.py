import random
import re
import json
import nltk
from flask import Flask, render_template, request, jsonify

nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)


def load_responses():

    with open("../response_mappings.json","r") as responses_file:
        return json.load(responses_file)



def random_string():

    fallback_responses = [
        "Please try writing something more descriptive.",
        "Oh! It appears you wrote something I don't understand yet.",
        "Do you mind trying to rephrase that?",
        "I'm terribly sorry, I didn't quite catch that.",
        "I can't answer that yet, please try asking something else."
    ]
    return random.choice(fallback_responses)

def extract_keywords(user_input):

    try:
        tokens = nltk.word_tokenize(user_input.lower())
        stopwords = set(nltk.corpus.stopwords.words('english'))
        keywords = [word for word in tokens if word not in stopwords]
        return keywords
    except Exception as e:
        print(f"Keyword extraction error: {e}")
        return []

def get_response(user_input, responses):

    user_input = user_input.lower().strip()
    user_keywords = extract_keywords(user_input)

    for response in responses:
        required_keywords = response.get("required_words", [])
        if required_keywords:
            
            matched_keywords = sum(1 for word in required_keywords if word in user_keywords)
            if matched_keywords / len(required_keywords) >= 0.6:  # At least 60% match
                bot_response = response["bot_response"]
                follow_up = response.get("follow_up")
                if follow_up:
                    bot_response += "\n" + follow_up
    
                return bot_response
            
        pattern = response.get("pattern")
        if pattern and re.search(pattern, user_input, re.IGNORECASE):
            bot_response = response["bot_response"]
            follow_up = response.get("follow_up")
            if follow_up:
                bot_response += "\n" + follow_up

            return bot_response

    # Fallback response
    return random_string()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form.get("user_input", "").strip()
    responses = load_responses()
    bot_response = get_response(user_input, responses)
    return jsonify({"user_input": user_input, "bot_response": bot_response})

if __name__ == "__main__":
    app.run(debug=True)

app=app