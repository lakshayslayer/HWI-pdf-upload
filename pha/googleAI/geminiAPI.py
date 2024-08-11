import os
import time
import google.generativeai as genai
import pdfplumber

# Configure the Gemini API key securely
api_key = "AIzaSyBGWNH9mygdQepDV1YvPt94TiTTpJ5V5_I"
genai.configure(api_key=api_key)

def start_empty_chat():
    # Initialize a new chat session
    generation_config = {
        "temperature": 0,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 1000000,
        "response_mime_type": "application/json",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )
    
    chat_session = model.start_chat(history=[])  # Start an empty chat session
    return chat_session

def extract_text_from_pdf(pdf_path):
    """Extracts text from the given PDF file."""
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text()
    return full_text

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def wait_for_files_active(files):
    """Waits for the given files to be active."""
    print("Waiting for file processing...")
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    print("...all files ready")
    print()

def send_message(chat_session, message):
    """Sends a message in the chat session and returns the response."""
    response = chat_session.send_message(message)
    print("Response:", response.text)
    return response.text
