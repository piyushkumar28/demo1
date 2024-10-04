import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
from langdetect import detect

# Initializing pyttsx3
listening = True
sending_to_gemini = False
engine = pyttsx3.init()

# Set up the Google Gemini API
genai.configure(api_key="AIzaSyB5z_FtouLRiYEUTKJsKRSKAh6nt3bnJv4")

# Set up the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

convo = model.start_chat(history=[])

# Function to get response from Google Gemini
def get_response(user_input):
    convo.send_message(user_input)
    gemini_reply = convo.last.text
    print(gemini_reply)
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

# Function to detect language from input text
def detect_language(text):
    # Using langdetect library to detect the language
    lang = detect(text)
    if lang == 'hi':
        return 'hi-IN'  # Hindi
    elif lang == 'ta':
        return 'ta-IN'  # Tamil
    else:
        return 'en-US'  # Default to English if not recognized

# Main loop for listening and responding
exit_words = ["exit", "stop", "quit", "bye", "goodbye"]  # Add your exit words here
wake_word = "gemini"  # Set your wake word here

while listening:
    with sr.Microphone() as source:
        recognizer = sr.Recognizer()
        recognizer.adjust_for_ambient_noise(source)
        recognizer.dynamic_energy_threshold = 3000

        try:
            print("Listening...")
            audio = recognizer.listen(source, timeout=5.0)
            response = recognizer.recognize_google(audio, language='hi-IN')  # Start with Hindi by default
            print(response)

            if any(exit_word in response.lower() for exit_word in exit_words):
                sending_to_gemini = False
                print("Stopped sending responses to Gemini.")
                continue

            if wake_word in response.lower() and not sending_to_gemini:
                sending_to_gemini = True
                print("Resumed sending responses to Gemini.")

            if sending_to_gemini:
                # Detect the language dynamically from the user input
                detected_language = detect_language(response)
                set_voice(detected_language[:2])  # Set the TTS voice for the detected language

                # Update the speech recognition language for next input
                response = recognizer.recognize_google(audio, language=detected_language)
                response_from_gemini = get_response(response)

                # Speak the response in the detected language
                engine.setProperty('rate', 200)
                engine.setProperty('volume', volume)
                engine.say(response_from_gemini)
                engine.runAndWait()

        except sr.UnknownValueError:
            print("Didn't recognize anything.")
