import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
from langdetect import detect

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Configure the Gemini API
genai.configure(api_key="AIzaSyBouvRSS9IeVAXrbtYJy69slHADhax3-VA")  # Replace with your actual API key

# Generation configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Initialize the conversation model
model = genai.GeminiModel(model_name="gemini-free",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

convo = model.start_chat(history=[])

# Function to get response from Google Gemini
def get_response(user_input):
    convo.send_message(user_input)
    gemini_reply = convo.last.text
    return gemini_reply

# Function to set the voice based on the detected language
def set_voice(language_code):
    voices = engine.getProperty('voices')
    if language_code == 'hi':
        for voice in voices:
            if 'hindi' in voice.languages:
                engine.setProperty('voice', voice.id)
                break
    elif language_code == 'ta':
        for voice in voices:
            if 'tamil' in voice.languages:
                engine.setProperty('voice', voice.id)
                break

# Main loop for listening and responding
exit_words = ["exit", "stop", "quit", "bye", "goodbye"]
listening = True

while listening:
    with sr.Microphone() as source:
        recognizer = sr.Recognizer()
        recognizer.adjust_for_ambient_noise(source)

        try:
            print("Listening...")
            audio = recognizer.listen(source, timeout=5.0)
            response = recognizer.recognize_google(audio)  # Auto-detect language
            
            print(f"User said: {response}")

            # Detect the language dynamically
            detected_language = detect(response)

            # Set TTS voice based on detected language
            set_voice(detected_language[:2])

            if any(exit_word in response.lower() for exit_word in exit_words):
                print("Exiting...")
                listening = False
                continue

            # Get response from Gemini
            response_from_gemini = get_response(response)

            # Speak the response
            engine.say(response_from_gemini)
            engine.runAndWait()

        except sr.UnknownValueError:
            print("Didn't recognize anything.")
        except Exception as e:
            print(f"An error occurred: {e}")
