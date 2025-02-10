# 🛒 AI-Powered Self-Checkout System

## 📌 Introduction
This **AI-powered self-checkout system** eliminates the need for barcode scanning by using **computer vision** and **machine learning** to recognize products through a live webcam feed. The system automatically retrieves product details from a **CSV-based database**, displays the total bill, and generates an invoice. It is built using **Python, OpenCV, TensorFlow, and Tkinter** for an intuitive user experience.

---

## 🎯 Purpose & Use Cases
This system is ideal for:
- 🛍 **Retail Stores** - Automates checkout, reducing the need for human cashiers.
- 🏪 **Supermarkets** - Enhances efficiency by recognizing multiple items without scanning barcodes.
- 🤖 **Smart Kiosks** - Enables self-service billing at vending machines and smart retail kiosks.
- 🚀 **Futuristic Shopping** - Supports AI-driven checkout experiences with real-time product recognition.

---

## 🛠️ Features
### ✅ Real-Time Product Recognition
- Uses **machine learning models** to detect and classify products in a **live webcam feed**.
- Recognizes multiple products in a single frame.
- Filters out incorrect detections to prevent billing errors.

### ✅ Automatic Billing System
- Retrieves product details (name, price, quantity) from a **CSV database**.
- Calculates total cost dynamically as items are recognized.
- Displays an **interactive UI** for reviewing items before payment.

### ✅ User-Friendly GUI
- Built with **Tkinter**, providing an intuitive interface.
- Displays a **list of scanned products** and the total bill in real time.
- **Start/Stop scanning** options for controlled product detection.

### ✅ Invoice Generation
- Generates a **detailed bill summary** with all scanned items.
- Supports **exporting invoices** to **CSV or PDF** format.
- Option to print or email receipts for a contactless checkout experience.

### ✅ Auto Scan Every 5 Seconds
- Continuously scans for new products every **5 seconds**, making checkout seamless.

### ✅ Error Handling & Logging
- Logs unrecognized or misclassified items for **future model improvements**.
- Notifies users when an item is not found in the database.

---

## 📂 Project Structure
```
📁 AI-Self-Checkout
│── 📄 main.py              # Runs the GUI and product recognition
│── 📄 product_recognition.py # Machine learning model for detection
│── 📄 database.csv          # CSV file storing product details
│── 📄 invoice_generator.py  # Generates invoices
│── 📁 assets               # Stores images and model data
│── 📄 requirements.txt      # List of dependencies
│── 📄 README.md             # Project documentation
```

---

## 🖥️ Installation & Setup
### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/AI-Self-Checkout.git
cd AI-Self-Checkout
```

### 2️⃣ Install Dependencies
Ensure you have **Python 3.9+** installed. Then, run:
```bash
pip install -r requirements.txt
```

### 3️⃣ Run the Application
#### ➤ Start the Checkout System
```bash
python main.py
```
![WhatsApp Image 2025-02-10 at 7 12 39 PM](https://github.com/user-attachments/assets/5e6fd50a-022a-4cad-89e0-963d67852ca2)
![WhatsApp Image 2025-02-10 at 7 10 06 PM](https://github.com/user-attachments/assets/4d7829c9-7b68-4c53-87d3-5add4d889510)

---

## ⚙️ How It Works
1. Click the **Start Billing** button to activate the webcam.
2. The system scans products every **5 seconds**.
3. **Product recognition model** classifies detected items.
4. Details (name, price, quantity) are **fetched from the CSV database**.
5. The **GUI updates** with a list of scanned items and the total bill.
6. Clicking **Next** finalizes the bill and moves to the invoice screen.
7. Users can **review** the scanned items before completing the transaction.
8. A **final invoice** is generated and saved/exported.

---

## 🚀 Future Enhancements
- 🤖 **Deep Learning Integration** - Enhance accuracy using **YOLOv8** or **CNN models**.
- 💳 **Online Payment Support** - Integrate **UPI, PayPal, and Credit Cards**.
- 📦 **Inventory Management** - Track stock levels and update in real time.
- 🛠 **Admin Dashboard** - Web-based panel for managing product data and sales analytics.
- 📱 **Mobile App** - QR-based self-checkout via mobile scanning.
- 🌐 **Cloud Storage** - Sync transactions to a **cloud database**.
- 🗣 **Voice Assistance** - Hands-free checkout via voice commands.
- 🔔 **Smart Alerts** - Notify customers about discounts and out-of-stock items.

---

## 🤝 Contributing
Feel free to contribute by opening an **issue** or **pull request** on GitHub!

---

## 📜 License
This project is **open-source** and licensed under the MIT License.

---

## 🌟 Show Your Support
If you find this project useful, consider giving it a ⭐ on GitHub!

---

💡 **Developed with passion to revolutionize retail shopping and enhance the checkout experience!** 🚀


