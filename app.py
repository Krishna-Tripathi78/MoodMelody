from flask import Flask, render_template, request, jsonify
from textblob import TextBlob
import logging
import requests
import json
import os
import random
import nltk
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

try:
    nltk.download('punkt', quiet=True)
except Exception as e:
    logger.warning(f"Failed to download NLTK data: {e}")

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
USE_OPENAI = os.getenv("USE_OPENAI", "False").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_api_key_here")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

EMOTION_TO_GENRE = {
    "ecstatic": "party",
    "happy": "happy vibes",
    "calm": "chill",
    "neutral": "study music",
    "relaxed": "acoustic",
    "melancholic": "indie",
    "sad": "sad songs",
    "motivated": "workout",
    "romantic": "romance",
    "nostalgic": "throwback",
    "energetic": "pop",
    "focused": "instrumental",
    "angry": "rock",
    "peaceful": "nature sounds",
    "festive": "holiday",
    "love": "love songs"
}

GENRE_TO_PLAYLIST = {
    "party": "https://open.spotify.com/playlist/37i9dQZF1DXaXB8fQg7xif",
    "happy vibes": "https://open.spotify.com/playlist/37i9dQZF1DX3rxVfibe1L0",
    "chill": "https://open.spotify.com/playlist/37i9dQZF1DX4WYpdgoIcn6",
    "study music": "https://open.spotify.com/playlist/37i9dQZF1DX8NTLI2TtZa6",
    "acoustic": "https://open.spotify.com/playlist/37i9dQZF1DX6ziVCJnEm59",
    "indie": "https://open.spotify.com/playlist/37i9dQZF1DX2Nc3B70tvx0",
    "sad songs": "https://open.spotify.com/playlist/37i9dQZF1DX7qK8ma5wgG1",
    "workout": "https://open.spotify.com/playlist/37i9dQZF1DX76Wlfdnj7AP",
    "romance": "https://open.spotify.com/playlist/37i9dQZF1DX50QitC6Oqtn",
    "throwback": "https://open.spotify.com/playlist/37i9dQZF1DX4o1oenSJRJd",
    "pop": "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",
    "instrumental": "https://open.spotify.com/playlist/37i9dQZF1DX4sWSpwq3LiO",
    "rock": "https://open.spotify.com/playlist/37i9dQZF1DWXRqgorJj26U",
    "nature sounds": "https://open.spotify.com/playlist/37i9dQZF1DX4PP3DA4J0N8",
    "holiday": "https://open.spotify.com/playlist/37i9dQZF1DX6R7QUWePReA",
    "love songs": "https://open.spotify.com/playlist/37i9dQZF1DX50QitC6Oqtn"
}

SAMPLE_TRACKS = {
    "party": [
        {"name": "Don't Start Now", "artist": "Dua Lipa", "preview_url": "https://open.spotify.com/track/6WrI0LAC5M1Rw2MnX2ZvEg"},
        {"name": "Blinding Lights", "artist": "The Weeknd", "preview_url": "https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b"},
        {"name": "Physical", "artist": "Dua Lipa", "preview_url": "https://open.spotify.com/track/5px6upUHM3fhOP621Edp4V"},
        {"name": "Levitating", "artist": "Dua Lipa ft. DaBaby", "preview_url": "https://open.spotify.com/track/5nujrmhLynf4yMoMtj8AQF"},
        {"name": "Save Your Tears", "artist": "The Weeknd", "preview_url": "https://open.spotify.com/track/5QO79kh1waicV47BqGRL3g"}
    ],
    "happy vibes": [
        {"name": "Good as Hell", "artist": "Lizzo", "preview_url": "https://open.spotify.com/track/3Yh9lZcWyKrK9GjbhuS0hR"},
        {"name": "Walking on Sunshine", "artist": "Katrina & The Waves", "preview_url": "https://open.spotify.com/track/05wIrZSwuaVWhcv5FfqeH0"},
        {"name": "Happy", "artist": "Pharrell Williams", "preview_url": "https://open.spotify.com/track/60nZcImufyMA1MKQY3dcCH"},
        {"name": "Can't Stop the Feeling!", "artist": "Justin Timberlake", "preview_url": "https://open.spotify.com/track/1WkMMavIMc4JZ8cfMmxHkI"},
        {"name": "Uptown Funk", "artist": "Mark Ronson ft. Bruno Mars", "preview_url": "https://open.spotify.com/track/32OlwWuMpZ6b0aN2RZOeMS"}
    ],
    "chill": [
        {"name": "Circles", "artist": "Post Malone", "preview_url": "https://open.spotify.com/track/21jGcNKet2qwijlDFuPiPb"},
        {"name": "Watermelon Sugar", "artist": "Harry Styles", "preview_url": "https://open.spotify.com/track/6UelLqGlWMcVH1E5c4H7lY"},
        {"name": "Sunday Best", "artist": "Surfaces", "preview_url": "https://open.spotify.com/track/1Cv1YLb4q0RzL6pybtaMLo"},
        {"name": "Adore You", "artist": "Harry Styles", "preview_url": "https://open.spotify.com/track/3jjujdWJ72nww5eGnfs2E7"},
        {"name": "Memories", "artist": "Maroon 5", "preview_url": "https://open.spotify.com/track/2b8fOow8UzyDFAE27YhOZM"}
    ]
}

@app.route("/")
def home():
    return render_template("splash.html")

@app.route("/app")
def main_app():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    user_text = request.args.get('msg')
    if not user_text:
        return jsonify({"response": "Please provide a valid message."})
    
    try:
        sentiment_score = TextBlob(user_text).sentiment.polarity
        emotion = classify_emotion(sentiment_score)

        logger.info(f"User input: {user_text}")
        logger.info(f"Sentiment polarity: {sentiment_score}")
        logger.info(f"Classified emotion: {emotion}")

        bot_response = fetch_ollama_response(user_text)
        
        if emotion in EMOTION_TO_GENRE:
            genre = EMOTION_TO_GENRE[emotion]
            if not bot_response.startswith("I'm having trouble") and not bot_response.startswith("I'm not sure"):
                bot_response += f"\n\nI sense you're feeling {emotion}. Would you like me to recommend some {genre} music? Click the 'Get Music' button!"
            else:
                bot_response = f"I sense you're feeling {emotion}. Would you like me to recommend some {genre} music? Click the 'Get Music' button!"
        
        return jsonify({"response": bot_response, "emotion": emotion})
    except Exception as e:
        logger.error(f"Error processing user input: {e}", exc_info=True)
        return jsonify({"response": "Sorry, I couldn't process your request."})

@app.route("/forward/", methods=["POST"])
def get_music_recommendations():
    try:
        data = request.get_json()
        if not data or 'msg' not in data:
            return jsonify({"error": "Invalid request data"}), 400
        
        user_text = data['msg']
        
        sentiment_score = TextBlob(user_text).sentiment.polarity
        emotion = classify_emotion(sentiment_score)
        
        genre = EMOTION_TO_GENRE.get(emotion, "pop")
        
        playlist_url = GENRE_TO_PLAYLIST.get(genre, "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
        
        tracks = SAMPLE_TRACKS.get(genre, SAMPLE_TRACKS.get("happy vibes"))
        
        if not tracks:
            tracks = generate_sample_tracks(genre)
        
        logger.info(f"Music recommendation - Emotion: {emotion}, Genre: {genre}")
        
        return jsonify({
            "emotion": emotion,
            "genre": genre,
            "playlist_url": playlist_url,
            "tracks": tracks
        })
        
    except Exception as e:
        logger.error(f"Error generating music recommendations: {e}", exc_info=True)
        return jsonify({"error": "Failed to generate music recommendations"}), 500

def classify_emotion(sentiment_score):
    if sentiment_score >= 0.75:
        return "ecstatic"
    elif sentiment_score >= 0.5:
        return "happy"
    elif sentiment_score >= 0.25:
        return "motivated"
    elif sentiment_score >= 0.1:
        return "relaxed"
    elif sentiment_score > -0.1:
        return "neutral"
    elif sentiment_score > -0.25:
        return "melancholic"
    elif sentiment_score > -0.5:
        return "sad"
    else:
        return "angry"

def fetch_ollama_response(user_text):
    try:
        custom_response = check_for_custom_questions(user_text)
        if custom_response:
            return custom_response
        
        system_prompt = """You are MoodMelody, an advanced AI assistant created by Krishna Tripathi, ManuRaj Singh, Mohini Srivastava and Manas Gupta.
        You can answer any question like ChatGPT with detailed, helpful, and accurate information.
        You're knowledgeable about a wide range of topics including science, history, technology, arts, and more.
        You can provide explanations, definitions, how-to guides, and creative content.
        Your primary specialty is analyzing user emotions and recommending music that matches their mood.
        Always be helpful, friendly, and conversational in your responses.
        """
        
        if USE_OPENAI and OPENAI_API_KEY:
            return fetch_openai_response(user_text, system_prompt)
        else:
            return fetch_local_llm_response(user_text, system_prompt)
            
    except Exception as e:
        logger.error(f"Error fetching AI response: {e}", exc_info=True)
        return generate_fallback_response(user_text)

def fetch_openai_response(user_text, system_prompt):
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("Connecting to OpenAI API...")
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        logger.info("Successfully received response from OpenAI")
        return response.choices[0].message.content.strip()
    except ImportError:
        logger.error("OpenAI package not installed. Install with: pip install openai")
        return fetch_local_llm_response(user_text, system_prompt)
    except Exception as e:
        logger.error(f"OpenAI API error: {e}", exc_info=True)
        return fetch_local_llm_response(user_text, system_prompt)

def fetch_local_llm_response(user_text, system_prompt):
    try:
        full_prompt = f"{system_prompt}\n\nUser: {user_text}\nMoodMelody:"

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": full_prompt,
            "stream": False,
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 500
        }
        
        logger.info(f"Sending request to Ollama API at {OLLAMA_API_URL}")
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        else:
            logger.error(f"Ollama API error: {response.status_code}, {response.text}")
            return generate_fallback_response(user_text)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to Ollama: {e}", exc_info=True)
        return generate_fallback_response(user_text)

def check_for_custom_questions(user_text):
    user_text_lower = user_text.lower()
    
    if any(word in user_text_lower for word in ["who made you", "who created you", "who developed you", "who built you", "your creator", "your developer", "who programmed you"]):
        return "I was developed by KRISHNA TRIPATHI, ManuRaj Singh, Mohini Srivastava and Manas Gupta. I'm an AI-powered chatbot that analyzes your emotions, suggests music to match your mood, and can answer a wide range of questions like ChatGPT."
    
    elif any(word in user_text_lower for word in ["who are you", "what are you", "your name", "what's your name", "what is your name"]):
        return "I'm MoodMelody, an AI-powered chatbot designed to analyze your emotions, recommend music that matches your mood, and answer any questions you might have. I was developed by Krishna Tripathi, ManuRaj Singh, Mohini Srivastava and Manas Gupta."

    elif any(phrase in user_text_lower for phrase in ["how do you work", "how does this work", "how it works"]):
        return "I analyze the sentiment of your messages to determine your emotional state and recommend music that matches your mood. I can also answer questions on virtually any topic using my knowledge base, similar to ChatGPT. Just ask me anything you'd like to know!"
    
    return None

def generate_fallback_response(user_text):
    user_text_lower = user_text.lower()
    
    if any(word in user_text_lower for word in ["who made you", "who created you", "who developed you", "who built you", "your creator", "your developer", "who programmed you"]):
        return "I was developed by KRISHNA TRIPATHI, ManuRaj Singh, Mohini Srivastava and Manas Gupta. I'm an AI-powered chatbot that analyzes your emotions, suggests music to match your mood, and can answer a wide range of questions."
    
    elif any(word in user_text_lower for word in ["who are you", "what are you", "your name", "what's your name", "what is your name"]):
        return "I'm MoodMelody, an AI-powered chatbot designed to analyze your emotions, recommend music that matches your mood, and answer questions on various topics. I was developed by Krishna Tripathi, ManuRaj Singh, Mohini Srivastava and Manas Gupta."
    
    elif any(greeting in user_text_lower for greeting in ["hello", "hi", "hey", "greetings"]):
        return "Hello there! How are you feeling today? I can help with music recommendations or answer questions on almost any topic."
    
    elif any(word in user_text_lower for word in ["how are you", "how're you", "how do you do"]):
        return "I'm doing well, thanks for asking! How about you? Feel free to ask me anything or share how you're feeling for music recommendations."
    
    elif any(word in user_text_lower for word in ["thank", "thanks", "thx"]):
        return "You're welcome! Happy to help. Let me know if you need anything else."
    
    elif any(word in user_text_lower for word in ["bye", "goodbye", "see you"]):
        return "Goodbye! Have a great day! Feel free to come back anytime you need music recommendations or have questions."
    
    elif any(word in user_text_lower for word in ["help", "assist", "support"]):
        return "I can help analyze your mood and recommend music that matches how you're feeling. I can also answer questions on a wide range of topics like science, history, technology, arts, and more. Just ask away!"
    
    elif any(word in user_text_lower for word in ["music", "song", "playlist", "recommend"]):
        return "I'd be happy to recommend some music for you! Just share how you're feeling, and I'll suggest music that matches your mood. You can also click the 'Get Music' button after sharing your feelings."
    
    elif any(phrase in user_text_lower for phrase in ["how do you work", "how does this work", "how it works"]):
        return "I analyze the sentiment of your messages to determine your emotional state and recommend music that matches your mood. I can also answer questions on virtually any topic using my knowledge base. Just ask me anything you'd like to know!"
    
    elif "what is" in user_text_lower or "who is" in user_text_lower or "when" in user_text_lower or "where" in user_text_lower or "why" in user_text_lower or "how" in user_text_lower:
        return "I'd be happy to answer that question, but I'm currently experiencing connection issues with my knowledge database. Please try again in a moment, or rephrase your question. In the meantime, would you like some music recommendations based on your mood?"
    
    return "I'm here to help answer your questions and recommend music based on your mood. What would you like to know or how are you feeling today?"

def generate_sample_tracks(genre):
    artists = [
        "The Weeknd", "Dua Lipa", "Billie Eilish", "Post Malone", "Ariana Grande",
        "Ed Sheeran", "Taylor Swift", "Drake", "Justin Bieber", "BTS",
        "Harry Styles", "Olivia Rodrigo", "Bad Bunny", "Adele", "Kendrick Lamar"
    ]
    
    track_names = [
        "Starlight", "Ocean Waves", "Midnight Dreams", "Summer Breeze", "Heartbeat",
        "Golden Hour", "Sunset Drive", "Neon Lights", "Rainy Day", "Mountain High",
        "City Lights", "Daydreamer", "Lost in Time", "Memories", "Echoes"
    ]
    
    tracks = []
    for i in range(5):
        track = {
            "name": random.choice(track_names),
            "artist": random.choice(artists),
            "preview_url": f"https://open.spotify.com/track/sample{i}"
        }
        tracks.append(track)
    
    return tracks

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)