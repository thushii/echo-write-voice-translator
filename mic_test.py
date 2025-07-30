import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone() as source:
    print("Say something...")
    audio = r.listen(source)
    print("Got it! Now recognizing...")

try:
    print("You said:", r.recognize_google(audio))
except sr.UnknownValueError:
    print("Sorry, could not understand your voice.")
except sr.RequestError as e:
    print(f"Could not request results from Google; {e}")