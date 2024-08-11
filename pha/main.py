import uvicorn
from fastapi import FastAPI, UploadFile, File
import os
import mimetypes
from googleAI.geminiAPI import upload_to_gemini, wait_for_files_active, start_empty_chat, send_message
import json

app = FastAPI()

# Global chat session
chat_session = None

def initialize_chat_session():
    global chat_session
    chat_session = start_empty_chat()
    if chat_session is None:
        print("Failed to start chat session.")
        return
    # Upload default PDF as knowledge base
    default_pdf_path = r"C:\Users\tusha\OneDrive\Desktop\HWI_5\pha\data\EMROPUB_2019_en_23536.pdf"
    mime_type, _ = mimetypes.guess_type(default_pdf_path)
    uploaded_file = upload_to_gemini(default_pdf_path, mime_type=mime_type or "application/octet-stream")
    wait_for_files_active([uploaded_file])
    # Add the default PDF file to the chat session
    send_message(chat_session, "Add this PDF as knowledge base.")

@app.on_event("startup")
async def startup_event():
    initialize_chat_session()

@app.get("/health")
def health_check():
    return {"Hello": "Hi dev, server is up and running!!!"}

@app.get("/hello/{name}")
def greet_name(name: str):
    return {"Hello": f"Hi {name}, server is up and running!!!"}

@app.post("/upload-image/")
async def upload_image(image: UploadFile = File(...)):
    if chat_session is None:
        return {"error": "Chat session is not initialized."}

    save_dir = "data"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    file_location = os.path.join(save_dir, image.filename)

    # Save the uploaded file to the "data" directory
    with open(file_location, "wb") as f:
        contents = await image.read()
        f.write(contents)

    # Determine the MIME type of the file
    mime_type, _ = mimetypes.guess_type(file_location)

    # Upload the image to Gemini API with the correct MIME type
    uploaded_file = upload_to_gemini(file_location, mime_type=mime_type or "application/octet-stream")

    # Wait for the file to be ready
    wait_for_files_active([uploaded_file])

    # Send the uploaded image to the chat session and ask a query
    response_text = send_message(chat_session, "Analyze this file for its nutritional content.")

    # Print response for debugging
    print(f"Response from Gemini API: {response_text}")

    return {"filename": image.filename, "gemini_response": response_text}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
