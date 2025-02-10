import cv2
import tkinter as tk
from keras.models import load_model
from PIL import Image, ImageTk, ImageOps
import numpy as np
import pandas as pd
import time

# Load the model
try:
    model = load_model("keras_model.h5", compile=False)
except Exception as e:
    print(f"Error loading model: {e}")
    exit()

# Load the labels
try:
    class_names = open("labels.txt", "r").readlines()
except FileNotFoundError:
    print("Error: labels.txt file not found.")
    exit()

# Create the array of the right shape to feed into the Keras model
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

# Initialize the GUI
register_root = tk.Tk()
register_root.title("Product Registration")

# Entry fields for product details
tk.Label(register_root, text="Class Name:").pack(pady=5)
class_name_entry = tk.Entry(register_root)
class_name_entry.pack(pady=5)

tk.Label(register_root, text="Product Name:").pack(pady=5)
product_name_entry = tk.Entry(register_root)
product_name_entry.pack(pady=5)

tk.Label(register_root, text="Product ID:").pack(pady=5)
product_id_entry = tk.Entry(register_root)
product_id_entry.pack(pady=5)

tk.Label(register_root, text="Price:").pack(pady=5)
price_entry = tk.Entry(register_root)
price_entry.pack(pady=5)

# List to store product details
product_list = []


def register_product():
    class_name = class_name_entry.get()
    product_name = product_name_entry.get()
    product_id = product_id_entry.get()
    price = price_entry.get()

    if class_name and product_name and product_id and price:
        product_list.append({
            'ClassName': class_name,
            'ProductName': product_name,
            'ID': product_id,
            'Price': price
        })

        # Save to CSV
        df = pd.DataFrame(product_list)
        df.to_csv("product_details.csv", index=False)

        # Clear entries
        class_name_entry.delete(0, tk.END)
        product_name_entry.delete(0, tk.END)
        product_id_entry.delete(0, tk.END)
        price_entry.delete(0, tk.END)
        print("Product details saved to CSV.")


def detect_class():
    # Capture a single frame from the webcam
    cap = cv2.VideoCapture(1)
    ret, frame = cap.read()
    if ret:
        # Convert the captured frame to PIL format
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Resize the image to 224x224 and process it
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

        # Turn the image into a numpy array
        image_array = np.asarray(image)

        # Normalize the image
        normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

        # Load the image into the array
        data[0] = normalized_image_array

        # Predict the model
        prediction = model.predict(data)
        index = np.argmax(prediction)
        class_name = class_names[index].strip()

        # Set class name in the entry field
        class_name_entry.delete(0, tk.END)
        class_name_entry.insert(0, class_name)

    cap.release()


# Register button
register_button = tk.Button(register_root, text="Register Product", command=register_product, font=("Arial", 16))
register_button.pack(pady=20)

# Detect button
detect_button = tk.Button(register_root, text="Detect Class", command=detect_class, font=("Arial", 16))
detect_button.pack(pady=20)

# Start the GUI main loop
register_root.mainloop()
