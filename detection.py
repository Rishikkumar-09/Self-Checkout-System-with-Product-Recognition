import cv2
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from keras.models import load_model
from PIL import Image, ImageTk, ImageOps
import numpy as np
import pandas as pd
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import webbrowser

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


# Load product details from CSV
def load_product_details():
    try:
        df = pd.read_csv("product_details.csv")
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=['ClassName', 'ProductName', 'ID', 'Price'])


product_df = load_product_details()

# Initialize the main GUI
main_root = tk.Tk()
main_root.title("Product Detection")

# Create a frame to hold the webcam feed and product list
frame = tk.Frame(main_root)
frame.pack(side=tk.LEFT)

# Create a canvas for displaying the webcam feed
canvas = tk.Canvas(frame, width=640, height=480)
canvas.pack()

# Create a listbox for displaying the detected products
product_listbox = tk.Listbox(main_root, width=40, height=25)
product_listbox.pack(side=tk.RIGHT, padx=20, pady=10)

# Customer details frame
customer_frame = tk.Frame(main_root)
customer_frame.pack(side=tk.BOTTOM, pady=10)

tk.Label(customer_frame, text="Customer Name:").grid(row=0, column=0, padx=5)
tk.Label(customer_frame, text="Email:").grid(row=1, column=0, padx=5)
tk.Label(customer_frame, text="Mobile Number:").grid(row=2, column=0, padx=5)

customer_name_entry = tk.Entry(customer_frame, width=30)
customer_name_entry.grid(row=0, column=1, padx=5)
customer_email_entry = tk.Entry(customer_frame, width=30)
customer_email_entry.grid(row=1, column=1, padx=5)
customer_mobile_entry = tk.Entry(customer_frame, width=30)
customer_mobile_entry.grid(row=2, column=1, padx=5)

# Initialize list to store detected products
detected_products = []
cap = cv2.VideoCapture(1)  # Open the webcam

# Variable to control scanning
scanning_active = True


# Function to update webcam feed continuously
def update_feed():
    if not scanning_active:
        return  # Stop updating feed if scanning is inactive

    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img = ImageTk.PhotoImage(image=img)

        canvas.create_image(0, 0, anchor=tk.NW, image=img)
        canvas.image = img  # Keep reference to avoid garbage collection

    main_root.after(10, update_feed)  # Continuously update the feed


# Function to start billing and detect products
def start_billing():
    global detected_products

    if scanning_active:
        # Capture a single frame from the webcam
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

            # Skip processing if class is 'null'
            if class_name == 'null':
                return

            # Retrieve product details from the CSV based on detected class name
            product_details = product_df[product_df['ClassName'] == class_name]

            if not product_details.empty:
                product_details = product_details.iloc[0].to_dict()
                product_details['ClassName'] = class_name
            else:
                # Handle case where no details are found
                product_details = {
                    'ClassName': class_name,
                    'ProductName': 'Unknown',
                    'ID': 'N/A',
                    'Price': 'N/A'
                }

            # Check if the product is already in the detected list
            existing_product = next(
                (p for p in detected_products if p['ProductName'] == product_details['ProductName']), None)
            if existing_product:
                existing_product['Quantity'] += 1
            else:
                product_details['Quantity'] = 1
                detected_products.append(product_details)

            # Update the listbox with the new product
            product_listbox.delete(0, tk.END)  # Clear existing entries
            for product in detected_products:
                product_listbox.insert(tk.END,
                                       f"{product['ProductName']} - ₹{product['Price']} x {product['Quantity']}")

    main_root.after(5000, start_billing)  # Schedule the next detection after 5 seconds


# Function to generate UPI link
def generate_upi_link(amount):
    upi_id = "9876543210@axl"  # Replace with your UPI ID
    upi_link = f"upi://pay?pa={upi_id}&pn=SPARTAN%20SUPER%20MART&mc=1234&tid=001&tr=1234567890&tn=Payment%20for%20invoice&am={amount:.2f}&cu=INR&url="
    return upi_link


# Function to stop scanning and show billing summary in a new popup window
def show_billing_summary():
    global scanning_active
    scanning_active = False  # Stop scanning

    # Create a new window for the invoice summary
    invoice_window = tk.Toplevel(main_root)
    invoice_window.title("Invoice Summary")

    # Create a treeview widget to display products
    tree = ttk.Treeview(invoice_window, columns=("No.", "ProductName", "Price", "Quantity"), show="headings")
    tree.heading("No.", text="No.")
    tree.heading("ProductName", text="Product Name")
    tree.heading("Price", text="Price")
    tree.heading("Quantity", text="Quantity")
    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    total_amount = 0
    product_entries = {}
    for i, product in enumerate(detected_products):
        # Skip 'null' products
        if product['ProductName'] == 'Unknown':
            continue

        price = float(product['Price']) if product['Price'] != 'N/A' else 0
        total_amount += price * product['Quantity']

        if product['ProductName'] in product_entries:
            # Update existing entry
            existing_item = product_entries[product['ProductName']]
            tree.item(existing_item, values=(i + 1, product['ProductName'], f"${price:.2f}", product['Quantity']))
        else:
            # Add new entry
            item = tree.insert("", "end",
                               values=(i + 1, product['ProductName'], f"${price:.2f}", product['Quantity']))
            product_entries[product['ProductName']] = item

    # Display the total amount
    total_label = tk.Label(invoice_window, text=f"Total Amount: ${total_amount:.2f}", font=("Arial", 16))
    total_label.pack(side=tk.BOTTOM, pady=20)

    # Generate UPI link with the total amount
    upi_link = generate_upi_link(total_amount)

    # Add a button to open the UPI link
    upi_button = tk.Button(invoice_window, text="Pay via UPI", command=lambda: webbrowser.open(upi_link),
                           font=("Arial", 16))
    upi_button.pack(side=tk.BOTTOM, pady=10)

    # Add a button to send invoice via email
    email_entry = tk.Entry(invoice_window, width=30)
    email_entry.pack(side=tk.BOTTOM, pady=10)
    email_entry.insert(0, "")

    export_button = tk.Button(invoice_window, text="Send Invoice", command=lambda: generate_pdf(email_entry.get()),
                              font=("Arial", 16))
    export_button.pack(side=tk.BOTTOM, pady=10)


# Function to generate PDF invoice
# Function to generate PDF invoice
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    customer_name = customer_name_entry.get()
    customer_email = customer_email_entry.get()
    customer_mobile = customer_mobile_entry.get()

    # Company information
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'SPARTAN SUPER MART', ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, '123 Business Rd', ln=True, align='C')
    pdf.cell(0, 10, 'address', ln=True, align='C')
    pdf.cell(0, 10, 'Phone: 876543210', ln=True, align='C')
    pdf.cell(0, 10, 'Email: contact@spartan13@gmail.com', ln=True, align='C')
    pdf.ln(10)  # Line break

    # Customer information
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Customer Information:', ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Name: {customer_name}', ln=True)
    pdf.cell(0, 10, f'Email: {customer_email}', ln=True)
    pdf.cell(0, 10, f'Mobile: {customer_mobile}', ln=True)

    pdf.ln(10)  # Line break
    # Add table headers
    pdf.cell(40, 10, txt="Product Name", border=1, align='C')
    pdf.cell(40, 10, txt="Price", border=1, align='C')
    pdf.cell(40, 10, txt="Quantity", border=1, align='C')
    pdf.cell(40, 10, txt="Total", border=1, ln=True, align='C')

    total_amount = 0
    # List products in table format
    for product in detected_products:
        if product['ProductName'] == 'Unknown':
            continue
        price = float(product['Price']) if product['Price'] != 'N/A' else 0
        total_price = price * product['Quantity']
        total_amount += total_price

        pdf.cell(40, 10, txt=product['ProductName'], border=1, align='C')
        pdf.cell(40, 10, txt=f"${price:.2f}", border=1, align='C')
        pdf.cell(40, 10, txt=str(product['Quantity']), border=1, align='C')
        pdf.cell(40, 10, txt=f"${total_price:.2f}", border=1, ln=True, align='C')

    # Add total amount at the end
    pdf.cell(120, 10, txt="Total Amount", border=1, align='C')
    pdf.cell(40, 10, txt=f"${total_amount:.2f}", border=1, ln=True, align='C')

    # Save the PDF to a file
    pdf_file = "invoice.pdf"
    pdf.output(pdf_file)

    # Fetch email from customer entry
    customer_email = customer_email_entry.get()

    # Send email with PDF attachment
    send_email(customer_email, pdf_file, total_amount)


# Remove email entry field from the billing summary function
def show_billing_summary():
    global scanning_active
    scanning_active = False  # Stop scanning

    # Create a new window for the invoice summary
    invoice_window = tk.Toplevel(main_root)
    invoice_window.title("Invoice Summary")

    # Create a treeview widget to display products
    tree = ttk.Treeview(invoice_window, columns=("No.", "ProductName", "Price", "Quantity"), show="headings")
    tree.heading("No.", text="No.")
    tree.heading("ProductName", text="Product Name")
    tree.heading("Price", text="Price")
    tree.heading("Quantity", text="Quantity")
    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    total_amount = 0
    product_entries = {}
    for i, product in enumerate(detected_products):
        # Skip 'null' products
        if product['ProductName'] == 'Unknown':
            continue

        price = float(product['Price']) if product['Price'] != 'N/A' else 0
        total_amount += price * product['Quantity']

        if product['ProductName'] in product_entries:
            # Update existing entry
            existing_item = product_entries[product['ProductName']]
            tree.item(existing_item, values=(i + 1, product['ProductName'], f"${price:.2f}", product['Quantity']))
        else:
            # Add new entry
            item = tree.insert("", "end",
                               values=(i + 1, product['ProductName'], f"${price:.2f}", product['Quantity']))
            product_entries[product['ProductName']] = item

    # Display the total amount
    total_label = tk.Label(invoice_window, text=f"Total Amount: ${total_amount:.2f}", font=("Arial", 16))
    total_label.pack(side=tk.BOTTOM, pady=20)

    # Generate UPI link with the total amount
    upi_link = generate_upi_link(total_amount)

    # Add a button to open the UPI link
    upi_button = tk.Button(invoice_window, text="Pay via UPI", command=lambda: webbrowser.open(upi_link),
                           font=("Arial", 16))
    upi_button.pack(side=tk.BOTTOM, pady=10)

    # Add a button to send invoice via email (no need to enter email again)
    export_button = tk.Button(invoice_window, text="Send Invoice", command=generate_pdf, font=("Arial", 16))
    export_button.pack(side=tk.BOTTOM, pady=10)


# Function to send email with PDF attachment
def send_email(recipient_email, pdf_file, total_amount):
    sender_email = "spartansupermart@gmail.com"
    sender_password = "xxxx xxxx xxx xxxx"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "Your Invoice"

    body = "Please find attached your invoice and UPI payment link."
    msg.attach(MIMEText(body, 'plain'))

    with open(pdf_file, 'rb') as attachment:
        part = MIMEApplication(attachment.read(), Name=pdf_file)
        part['Content-Disposition'] = f'attachment; filename="{pdf_file}"'
        msg.attach(part)

    # Add UPI link to email body
    upi_link = generate_upi_link(total_amount)
    msg.attach(MIMEText(f"\n\n {upi_link} ", 'plain'))

    # Send email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

    messagebox.showinfo("Success", "Invoice sent to email successfully.")


# Start the webcam feed and billing process
update_feed()

# Button to start billing
start_button = tk.Button(main_root, text="Start Billing", command=start_billing)
start_button.pack(side=tk.BOTTOM, pady=10)

# Button to show billing summary
summary_button = tk.Button(main_root, text="Show Billing Summary", command=show_billing_summary)
summary_button.pack(side=tk.BOTTOM, pady=10)

main_root.mainloop()

# Release the webcam and close the program
cap.release()
cv2.destroyAllWindows()
