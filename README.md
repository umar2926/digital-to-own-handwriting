# digital-to-own-handwriting
This repository contains a Flask web app for recognizing handwritten characters. Users can upload images with handwritten text, which are processed with OpenCV to extract and save individual characters without backgrounds. The app allows manual annotation of characters and uses this data to recognize handwritten text from user input.

# Features
Image Upload: Users can upload images containing handwritten text.
Character Extraction: The application processes the uploaded image to extract individual characters.
Character Annotation: Users can manually annotate extracted characters.
Character Recognition: The app can recognize and display characters based on user input.
Background Removal: Extracted characters are saved with their backgrounds removed for clearer recognition.

# Installation
Clone the repository:
git clone https://github.com/umar2926/digital-to-own-handwriting.git

cd handwritten-character-recognition

Install dependencies:

pip install -r requirements.txt

Run the application:

python app.py

# Usage
Navigate to http://127.0.0.1:5000/ in your web browser.
Upload an image containing handwritten text.
Annotate the extracted characters.
Enter text in the recognition form to see the recognized characters.

# Folder Structure
app.py: Main application file.
templates/: HTML templates for rendering web pages.
static/characters/: Directory for saving extracted character images.
uploads/: Directory for temporarily storing uploaded images.
