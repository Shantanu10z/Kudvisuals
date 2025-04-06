import speech_recognition as sr

def list_microphones():
    print("🔍 Available Microphones:\n")
    for i, mic_name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"  [{i}] {mic_name}")

def test_microphone(device_index=None):
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone(device_index=device_index) as source:
            print("\n🎤 Speak something... (You have 5 seconds)")
            recognizer.adjust_for_ambient_noise(source)
            audio_data = recognizer.listen(source, timeout=5)

            print("🔎 Recognizing...")
            text = recognizer.recognize_google(audio_data)
            print("✅ You said:", text)

    except sr.UnknownValueError:
        print("❌ Could not understand audio")
    except sr.RequestError as e:
        print(f"❌ Could not request results; {e}")
    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    list_microphones()

    index = input("\n🎙️ Enter the mic index to test (e.g., 0, 1, 2): ")
    if index.isdigit():
        test_microphone(device_index=int(index))
    else:
        print("❌ Invalid input. Must be a number.")
