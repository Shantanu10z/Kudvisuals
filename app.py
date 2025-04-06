import os
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import torch
import threading
import speech_recognition as sr
from tqdm import tqdm
from diffusers import StableDiffusionPipeline

pipe = None
image_counter = 1  # track generated images

def load_model():
    global pipe
    status_label.configure(text="🔄 Loading SD v1.5 model...")
    app.update()
    try:
        model_path = "./stable-diffusion"
        if os.path.exists(model_path):
            pipe = StableDiffusionPipeline.from_pretrained(
                model_path,
                torch_dtype=torch.float32,
                safety_checker=None
            )
            print("✅ Loaded model from local folder.")
        else:
            pipe = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=torch.float32,
                safety_checker=None
            )
            print("📥 Loaded model from Hugging Face cache.")

        pipe.set_progress_bar_config(disable=False)
        pipe.to("cpu")
        status_label.configure(text="✅ Model ready!")
    except Exception as e:
        print("❌ Model loading error:", e)
        status_label.configure(text="❌ Failed to load model")

def get_next_filename():
    base = "generatedimg"
    ext = ".png"
    i = 1
    while os.path.exists(f"{base}_{i}{ext}"):
        i += 1
    return f"{base}_{i}{ext}"

def threaded_generate():
    global pipe
    prompt = prompt_entry.get().strip()
    if not prompt:
        status_label.configure(text="⚠️ Enter a prompt.")
        return
    if pipe is None:
        status_label.configure(text="⚠️ Model not loaded yet.")
        return

    status_label.configure(text="🎨 Generating image...")
    app.update()

    try:
        steps = 20
        bar = tqdm(total=steps, desc="Generating", ncols=70)

        def callback(step, timestep, total):
            bar.update(1)

        image = pipe(prompt, num_inference_steps=steps, callback=callback, callback_steps=1).images[0]
        bar.close()

        filename = get_next_filename()
        image.save(filename)
        img = Image.open(filename).resize((400, 400))
        img_tk = ImageTk.PhotoImage(img)
        image_label.configure(image=img_tk, width=400, height=400)
        image_label.image = img_tk
        status_label.configure(text=f"✅ Image saved as '{filename}'")
        print(f"✅ Image saved as '{filename}'")

    except Exception as e:
        status_label.configure(text=f"❌ Generation failed: {e}")
        print("❌ Generation failed:", e)

def generate_image():
    threading.Thread(target=threaded_generate).start()

def voice_to_text():
    status_label.configure(text="🎤 Listening...")
    app.update()
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone(device_index=2) as source:
            recognizer.adjust_for_ambient_noise(source)
            audio_data = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio_data)
            prompt_entry.delete(0, tk.END)
            prompt_entry.insert(0, text)
            status_label.configure(text="✅ Voice captured.")
    except sr.WaitTimeoutError:
        status_label.configure(text="❌ Timeout: No voice detected.")
    except sr.UnknownValueError:
        status_label.configure(text="❌ Could not understand audio.")
    except sr.RequestError as e:
        status_label.configure(text=f"❌ API Error: {e}")
    except Exception as e:
        status_label.configure(text=f"❌ Mic error: {e}")

# GUI Setup
ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.title("KukuAudVisuals")
app.geometry("600x700")

ctk.CTkLabel(app, text="Prompt:", font=("Arial", 16)).pack(pady=(20, 0))
prompt_entry = ctk.CTkEntry(app, width=520, height=40, font=("Arial", 14))
prompt_entry.pack(pady=10)

status_label = ctk.CTkLabel(app, text="", font=("Arial", 12))
status_label.pack(pady=5)

image_label = ctk.CTkLabel(app, text="")
image_label.pack(pady=10)

ctk.CTkButton(app, text="🎙️ Record Voice", command=voice_to_text).pack(pady=5)
ctk.CTkButton(app, text="🖼️ Generate Image", command=generate_image).pack(pady=5)

app.after(200, load_model)
app.mainloop()
