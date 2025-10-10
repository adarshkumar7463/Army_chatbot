🪖 Army Chatbot

Army Chatbot is a secure, offline AI-powered chatbot designed specifically for the Army Signal Group. It provides a unified platform to query and manage army records stored in a MySQL database. Built using Python, Django, Haystack, Whoosh, and PyTesseract, the chatbot integrates OCR capabilities to process scanned documents and generate actionable insights.

🚀 Features

Offline & Secure: Works fully offline to ensure maximum data privacy for sensitive army records.

OCR-Enabled: Extracts text from scanned documents and images using PyTesseract.

Multi-Language Queries: Supports English and Hinglish for natural, easy-to-understand questions.

Report Generation: Generates PDF, Word, and Excel reports from queried data.

Efficient Search: Powered by Haystack and Whoosh for fast, full-text search across large datasets.

User-Friendly Interface: Django-based backend for managing queries, database interactions, and secure access.

🛠️ Tech Stack

Programming Language: Python

Web Framework: Django

Search Engine: Haystack + Whoosh

OCR Engine: PyTesseract

Database: MySQL

Document Generation: PDF, Word, Excel libraries (e.g., reportlab, python-docx, openpyxl)

📦 Installation
Prerequisites

Python 3.8+

MySQL server

Required Python packages (listed in requirements.txt)

Steps

Clone the repository:

git clone https://github.com/yourusername/army_chatbot.git
cd army_chatbot


Install dependencies:

pip install -r requirements.txt


Configure MySQL database and update settings.py with your credentials.

Run Django server:

python manage.py runserver


Access the chatbot via browser (localhost) or run the .exe version for offline use.

🧰 Usage

Ask questions in English or Hinglish related to army records.

View real-time responses powered by full-text search.

Generate reports in PDF, Word, or Excel for documentation or record-keeping.

Upload scanned documents/images to enable OCR extraction and integrate them into queries.

📂 Project Links

GitHub Repository: https://github.com/yourusername/army_chatbot


🔧 Future Enhancements

Integrate network monitoring and analytics features

Enable advanced AI-based query understanding

👨‍💻 Author

Adarsh Kumar
📧 kradarsh52@gmail.com
🔗 GitHub Profile
