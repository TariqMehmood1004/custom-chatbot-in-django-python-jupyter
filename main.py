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
        # Load Excel responses
        self.responses = {
            "Mentees": pd.read_excel(excel_file, sheet_name="Mentees").dropna(),
            "Mentors": pd.read_excel(excel_file, sheet_name="Mentors").dropna()
        }
        # Set up database
        self.conn = sqlite3.connect(db_file)
        self.create_chat_table()

    def create_chat_table(self):
        """
        Create a table to store chats if it doesn't exist.
        """
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
        """
        Store chat interactions in the database.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.conn:
            self.conn.execute("""
                INSERT INTO chat_logs (role, user_query, chatbot_response, timestamp)
                VALUES (?, ?, ?, ?)
            """, (role, query, response, timestamp))

    def get_response_from_excel(self, role, query):
        """
        Fetch response from Excel sheet.
        """
        role_data = self.responses.get(role)
        if role_data is not None:
            for _, row in role_data.iterrows():
                if query.strip().lower() == row["Questions"].strip().lower():
                    return row["Answers"]
        return None

    def get_response_from_generativeai(self, query):
        """
        Fetch response from Google's Generative AI model.
        """
        try:
            # Get user input and generate a response
            response = model.generate_content(query)
            return response.text.strip()
        except Exception as e:
            return f"Error fetching response from Generative AI: {e}"

    def chat(self, role, query):
        """
        Process the chat based on the role and query.
        """
        if role not in ["Mentees", "Mentors"]:
            return "Invalid role. Please choose either 'Mentees' or 'Mentors'."

        # Try to get response from Excel
        response = self.get_response_from_excel(role, query)

        # If no response found in Excel, use Generative AI
        if not response:
            response = self.get_response_from_generativeai(query)

        # Log the interaction
        self.log_chat(role, query, response)
        return response


if __name__ == '__main__':
    # Load Excel file
    file_path = 'mentee_mentor_questions.xlsx'  # Replace with your file path
    db_file = 'chat_logs.db'
    chatbot = CustomChatbot(file_path, db_file)

    while True:
        print("Choose a role: Mentees or Mentors")
        role = input("Enter your choice: ").strip().capitalize()

        if role not in ["Mentees", "Mentors"]:
            print("Invalid choice. Try again.")
            continue

        print(f"\nQuestions for {role}:")
        for question in chatbot.responses[role]["Questions"]:
            print(f"- {question}")

        query = input("\nEnter your question: ").strip()
        response = chatbot.chat(role, query)
        print(f"\nResponse: {response}")

        exit_prompt = input("\nDo you want to exit? (yes[y/Y]/no[n/N]): ").strip().lower()
        if exit_prompt == "yes" or exit_prompt == "y" or exit_prompt == "Y":
            break
