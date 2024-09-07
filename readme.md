Personalized Health App
    This FastAPI application is designed to assess the healthiness of food items based on their nutritional information. Users can upload images of food labels, and the app uses WHO guidelines to evaluate whether the food is healthy.

Features
    1. Health Check Endpoint: GET /health
        Returns a confirmation message indicating that the server is running.
    2. Image Upload and Health Assessment: POST /upload-image/
        a. Allows users to upload images of food labels.
        b. Saves the uploaded image to the server.
        c. Uploads the image to the Google Gemini API.
        d. Processes the image to extract nutritional information.
        e. Uses WHO guidelines to determine if the food is healthy, focusing on aspects such as     sugar content, sodium, fiber, fat, and overall nutritional value.
        f. Returns a detailed health assessment based on the image and guidelines.