import uvicorn
from fastapi import FastAPI, UploadFile, File
import os
import mimetypes
from googleAI.geminiAPI import upload_to_gemini, wait_for_files_active, start_chat_with_files, send_message
import json
app = FastAPI()

# Health check endpoint
@app.get("/health")
def health_check():
    return {"Hello": "Hi dev, server is up and running!!!"}

# Greeting endpoint
@app.get("/hello/{name}")
def greet_name(name: str):
    return {"Hello": f"Hi {name}, server is up and running!!!"}

# Upload image and process with Gemini API


@app.post("/upload-image/")
async def upload_image(image: UploadFile = File(...)):
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

    # Start a chat session with the uploaded file
    chat_session = start_chat_with_files([uploaded_file])

    # Send a message to the chat session
    response_text = send_message(chat_session, "Using the attached WHO guidelines and the nutritional details in the attached image, determine if the food item is healthy for children. Provide a detailed explanation based on the guidelines,focusing on aspects like sugar content, sodium, fiber, fat, and overall nutritional value.Conclude with a clear recommendation. Include a summary of any allergy concerns.")

    return {"filename": image.filename, "gemini_response": json.loads(response_text)}


# Run the server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
