import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone() as source:
    print("Say something...")
    audio = r.listen(source)
    print("Recognizing...")

try:
    print("You said:", r.recognize_google(audio))
except sr.RequestError as e:
    print(f"API request error: {e}")
except sr.UnknownValueError:
    print("Sorry, couldn't understand audio.")
