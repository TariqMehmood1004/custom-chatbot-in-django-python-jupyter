
from django.shortcuts import render
from .forms import QuestionForm
import markdown
import os
import sqlite3
import pandas as pd
from datetime import datetime
import google.generativeai as genai

# Suppress GRPC debug logs
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GRPC_TRACE"] = ""

# Configure the Generative AI API key
api_key = "AIzaSyCle2-S8ezAAa1nHBBiO4gZ6XxsP-1AfIo"
genai.configure(api_key=api_key)

# Initialize the model
model = genai.GenerativeModel("gemini-1.5-flash")


class CustomChatbot:
    def __init__(self, excel_file, db_file):
        self.responses = {
            "Mentees": pd.read_excel(excel_file, sheet_name="Mentees").dropna(),
            "Mentors": pd.read_excel(excel_file, sheet_name="Mentors").dropna()
        }
        self.conn = sqlite3.connect(db_file)
        self.create_chat_table()

    def create_chat_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    user_query TEXT NOT NULL,
                    chatbot_response TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)

    def log_chat(self, role, query, response):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.conn:
            self.conn.execute("""
                INSERT INTO chat_logs (role, user_query, chatbot_response, timestamp)
                VALUES (?, ?, ?, ?)
            """, (role, query, response, timestamp))

    def get_response_from_excel(self, role, query):
        role_data = self.responses.get(role)
        if role_data is not None:
            for _, row in role_data.iterrows():
                if query.strip().lower() == row["Questions"].strip().lower():
                    return row["Answers"]
        return None

    def get_response_from_generativeai(self, query):
        try:
            response = model.generate_content(query)
            return response.text.strip()
        except Exception as e:
            return f"Error fetching response from Generative AI: {e}"

    def chat(self, role, query):
        if role not in ["Mentees", "Mentors"]:
            return "Invalid role. Please choose either 'Mentees' or 'Mentors'."

        response = self.get_response_from_excel(role, query)
        if not response:
            response = self.get_response_from_generativeai(query)

        self.log_chat(role, query, response)
        return response


def index(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data['role']
            question = form.cleaned_data['question']

            file_path = 'mentee_mentor_questions.xlsx'
            db_file = 'chat_logs.db'
            chatbot = CustomChatbot(file_path, db_file)
            response = chatbot.chat(role, question)

            # Convert the response to HTML using markdown
            response_html = markdown.markdown(response)

            return render(request, 'index.html', {'form': form, 'response': response_html})

    else:
        form = QuestionForm()

    return render(request, 'index.html', {'form': form})

