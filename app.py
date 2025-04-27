from flask import Flask, render_template, request
from googlesearch import search
import google.generativeai as genai
import logging
import os
import re
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG)
load_dotenv()  
print("Gemini Key Loaded:", os.getenv('GEMINI_API_KEY'))

# Initialize Flask app
app = Flask(__name__)

# 🔑 Load Gemini API key from environment variable for security
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Gemini response function with better error handling and logging
def get_gemini_response(prompt):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        generated_text = response.text.strip()
        
        # If response is empty, return a fallback message
        if not generated_text:
            return "⚠️ Sorry, I couldn’t find a detailed response for you."
        return generated_text
    except Exception as e:
        logging.error(f"Error generating Gemini response: {str(e)}")
        return "⚠️ Sorry, I’m having trouble generating a response right now."

# Google Search function with error handling and results logging
def get_google_results(query):
    results = []
    try:
        for url in search(query, num_results=3):
            results.append(url)
        if not results:
            results.append("⚠️ No results found at the moment.")
    except Exception as e:
        logging.error(f"Error fetching Google results: {str(e)}")
        results.append("⚠️ Couldn't fetch results at the moment.")
    return results

# Function to match keywords using regex (case-insensitive)
def match_keywords(user_input, keywords):
    pattern = re.compile(r'\b(?:' + '|'.join(keywords) + r')\b', re.IGNORECASE)
    return bool(pattern.search(user_input))

# Home route to render the index page
@app.route("/")
def home():
    return render_template("index.html")

# Bot response route
@app.route("/get")
def get_bot_response():
    user_input = request.args.get('msg')
    
    # Keywords to trigger external search
    job_keywords = ['job', 'jobs', 'internship', 'internships', 'hire', 'vacancy']
    mentor_keywords = ['mentor', 'mentorship', 'guidance']
    learn_keywords = ['course', 'learn', 'skill', 'training']
    safety_keywords = ['safe', 'safety', 'secure']
    career_event_keywords = ['career event', 'career fair', 'job fair', 'conference', 'webinar']

    # Job-related query
    if match_keywords(user_input, job_keywords):
        results = get_google_results(user_input + " site:linkedin.com OR site:naukri.com OR site:internshala.com")
        response = "💼 Here are some job-related links I found:\n" + "\n".join([f"{i+1}. {link}" for i, link in enumerate(results)])
        return response

    # Career Event-related query
    elif match_keywords(user_input, career_event_keywords):
        results = get_google_results(user_input + " site:eventbrite.com OR site:meetup.com OR site:linkedin.com")
        response = "🎤 Here are some upcoming career events:\n" + "\n".join([f"{i+1}. {link}" for i, link in enumerate(results)])
        return response

    # Mentor-related query
    elif match_keywords(user_input, mentor_keywords):
        results = get_google_results(user_input + " women mentorship site:herkey.in OR site:leanin.org")
        response = "🤝 Here are some mentorship resources:\n" + "\n".join([f"{i+1}. {link}" for i, link in enumerate(results)])
        return response

    # Learning-related query
    elif match_keywords(user_input, learn_keywords):
        results = get_google_results(user_input + " site:shecodes.io OR site:futurelearn.com OR site:github.com")
        response = "📚 Here are some learning platforms/resources:\n" + "\n".join([f"{i+1}. {link}" for i, link in enumerate(results)])
        return response

    # Safety-related query
    elif match_keywords(user_input, safety_keywords):
        response = "💡 Personal safety tips:\n- Stay alert and aware of your surroundings.\n- Trust your instincts and avoid risky situations.\n- Share your travel plans with someone you trust."
        return response

    else:
        # General help — fallback to Gemini
        prompt = f"You are a helpful AI assistant. Please assist with: {user_input}. Provide relevant details or resources."
        return get_gemini_response(prompt)

if __name__ == "__main__":
    app.run(debug=True)
