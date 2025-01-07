import os
import google.generativeai as genai

# Suppress GRPC debug logs
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GRPC_TRACE"] = ""

def main():
    try:
        # Configure the API key
        genai.configure(api_key="AIzaSyDxuUVik4Kud6NuFQFwsT9RyCOu-ZSj3YM")

        # Initialize the model
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Get user input and generate a response
        user_input = input("User: ")
        response = model.generate_content(user_input)
        print(f"Chatbot: {response.text}")
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    main()
