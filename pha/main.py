import uvicorn
from fastapi import FastAPI, UploadFile, File
import os
import mimetypes
from googleAI.geminiAPI import upload_to_gemini, wait_for_files_active, start_empty_chat, send_message, extract_text_from_pdf

app = FastAPI()

# Global chat session
chat_session = None

def initialize_chat_session():
    global chat_session
    chat_session = start_empty_chat()
    if chat_session is None:
        print("Failed to start chat session.")
        return
    
    # Path to the default PDF file
    default_pdf_path = r"C:\Users\tusha\OneDrive\Desktop\HWI_5\pha\data\EMROPUB_2019_en_23536.pdf"
    
    # Extract the text from the PDF file
    pdf_text = extract_text_from_pdf(default_pdf_path)
    
    # Send the extracted text as a message to the chat session
    send_message(chat_session, pdf_text)

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
    response_text = send_message(chat_session, "extract the nutrients details from the image.is it healthy for children according to WHO guidelines?")

    # Print response for debugging
    print(f"Response from Gemini API: {response_text}")

    return {"filename": image.filename, "gemini_response": response_text}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
