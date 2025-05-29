# MoodMelody - AI-Powered Music Recommendation Chatbot

MoodMelody is an intelligent chatbot that analyzes your emotions through conversation and recommends music that matches your mood. Using sentiment analysis and natural language processing, it creates a personalized music experience.

## Features

- **Emotion Analysis**: Analyzes text to determine your emotional state
- **Personalized Music Recommendations**: Suggests Spotify playlists based on detected emotions
- **Interactive Chat Interface**: User-friendly chat interface with real-time responses
- **Dark/Light Mode**: Toggle between dark and light themes
- **Responsive Design**: Works on desktop and mobile devices
- **Mood History**: Tracks your mood changes over time
- **Playlist Sharing**: Easily share playlists on social media

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript, jQuery
- **Backend**: Flask (Python)
- **NLP**: TextBlob for sentiment analysis
- **Music API**: Spotify Web API
- **LLM Integration**: Ollama API for conversational responses

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Krishna-Tripathi78/MoodMelody
   cd MoodMelody
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables (if needed):
   ```
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

1. Type how you're feeling in the chat input
2. MoodMelody will analyze your emotions and respond
3. Click "Get Music" to receive playlist recommendations
4. Open the playlist in Spotify to start listening
5. Share your playlist with friends if you enjoy it

## Dependencies

- Flask==2.2.3
- textblob==0.17.1
- requests==2.28.2
- gunicorn==20.1.0
- python-dotenv==1.0.0
- nltk==3.8.1

## Author

- [Krishna-Tripathi78](https://github.com/Krishna-Tripathi78)
- [Mohinisri123] (https://github.com/mohinisri23)


## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Spotify for providing the music API
- TextBlob for sentiment analysis capabilities
- Font Awesome for the icons used in the UI"# MoodMelody" 
