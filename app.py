from flask import Flask, render_template, request, redirect, url_for
import os
import cv2
import numpy as np

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
CHARACTERS_FOLDER = 'static/characters'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)
os.makedirs(CHARACTERS_FOLDER, exist_ok=True)

character_images = []
current_index = 0
character_annotations = {}

def process_image(image_path):
    global character_images
    global current_index
    
    image = cv2.imread(image_path)
    _, input_image = cv2.threshold(image, 115, 255, cv2.THRESH_BINARY)
    input_image = cv2.resize(input_image, (1300, 289))

    grayscale_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)

    blurred_image = cv2.medianBlur(grayscale_image, 3)

    binary_image = cv2.adaptiveThreshold(blurred_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    h, w = binary_image.shape[:2]
    mask = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(binary_image, mask, (0, 0), 0)

    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    input_image_copy = input_image.copy()
    padding = 15
    character_images = []

    for i, contour in enumerate(contours):
        x, y, w, h = cv2.boundingRect(contour)
        if w * h > 100:
            color = (0, 255, 0)
            cv2.rectangle(input_image_copy, (x - padding, y - padding), (x + w + padding, y + h + padding), color, 2)

            x_padded = max(x - padding, 0)
            y_padded = max(y - padding, 0)
            w_padded = min(x + w + padding, input_image.shape[1]) - x_padded
            h_padded = min(y + h + padding, input_image.shape[0]) - y_padded

            character_crop = input_image[y_padded:y_padded + h_padded, x_padded:x_padded + w_padded]

            # Convert character_crop to grayscale
            character_gray = cv2.cvtColor(character_crop, cv2.COLOR_BGR2GRAY)

            # Threshold to create a binary mask
            _, character_mask = cv2.threshold(character_gray, 50, 255, cv2.THRESH_BINARY)

            # Invert the mask (characters will be white, background will be black)
            character_mask_inv = cv2.bitwise_not(character_mask)

            # Apply the mask to remove the background
            character_without_background = cv2.bitwise_and(character_crop, character_crop, mask=character_mask)

            char_image_path = os.path.join(CHARACTERS_FOLDER, f"character_{i}.png")
            cv2.imwrite(char_image_path, character_without_background)
            print(f"Saved character image to: {char_image_path}")  # Debugging line
            character_images.append(f"character_{i}.png")

    current_index = 0
    return binary_image, input_image_copy, character_images


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global character_images
    global current_index

    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)
        
        if file:
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            
            binary_image, bounding_box_image, character_images = process_image(file_path)
            
            os.remove(file_path)
            
            # Initialize character annotations dictionary
            global character_annotations
            character_annotations = {img: '' for img in character_images}
            
            print(f"Character images: {character_images}")  # Debugging line
            
            return render_template('index.html', 
                                   binary_image=binary_image, 
                                   bounding_box_image=bounding_box_image, 
                                   character_image=character_images[current_index],
                                   total_images=len(character_images),
                                   index=current_index,
                                   show_input=True)
    
    return render_template('index.html', show_input=False)

@app.route('/submit', methods=['POST'])
def submit_character():
    global current_index
    global character_annotations
    global character_images

    character = request.form.get('character')
    character_annotations[character_images[current_index]] = character
    current_index += 1

    if current_index < len(character_images):
        return render_template('index.html',
                               binary_image=None,
                               bounding_box_image=None,
                               character_image=character_images[current_index],
                               total_images=len(character_images),
                               index=current_index,
                               show_input=True)
    else:
        # Save character annotations to a file or database
        save_annotations()

        return render_template('index.html',
                               message="All characters processed. Annotations saved.",
                               show_input=False,
                               all_submitted=True)

@app.route('/recognize', methods=['POST'])
def recognize_character():
    global character_annotations

    user_input = request.form.get('user_input', '').strip()
    
    recognized_images = []
    for char in user_input:
        if char == " ":
                recognized_images.append(" ")
                continue
        if char in character_annotations.values():
            for img, annotation in character_annotations.items():
                if annotation == char:
                    recognized_images.append(img)
                    break
        else:
            recognized_images.append('not_found_image.png')  # Placeholder for character not found
    
    return render_template('index.html',
                           recognized_images=recognized_images)

def save_annotations():
    global character_annotations
    # Example: Save annotations to a text file
    with open('annotations.txt', 'w') as f:
        for image, character in character_annotations.items():
            f.write(f"{image}: {character}\n")

if __name__ == '__main__':
    app.run(debug=True)
