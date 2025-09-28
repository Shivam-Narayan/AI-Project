# import openai
# import streamlit as st
# import pdfplumber
# from pymongo import MongoClient, errors
# import datetime
# import urllib.parse
# from dotenv import load_dotenv
# import os
# import streamlit as st
# from googletrans import Translator


# # st.image("../templates/Ascendum_image.png", width=200)

# # Load the .env file from the specified path
# env_path = os.path.join("..", "templates", ".env")
# load_dotenv(dotenv_path=env_path)

# # Set up your OpenAI API key
# open_api_key = os.getenv("OPENAI_API_KEY")
# openai.api_key = open_api_key

# # Function to read and extract text from a PDF file
# def extract_text_from_pdf(pdf_file):
#     text = ""
#     with pdfplumber.open(pdf_file) as pdf:
#         for page in pdf.pages:
#             text += page.extract_text()
#     return text

# # Function to generate a response from OpenAI's GPT model
# def generate_response(prompt, context):
#     response = openai.ChatCompletion.create(
#         model="gpt-4",
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant. Provide complete and well-structured responses."},
#             {"role": "user", "content": f"{context}\n\n{prompt}"},
#         ],
#         max_tokens=500,
#         temperature=0.7,
#     )
#     return response['choices'][0]['message']['content'].strip()

# # Function to connect to MongoDB Atlas
# def connect_to_mongodb():
#     try:
#         # Use urllib to encode special characters in the username and password
#         username = urllib.parse.quote_plus("harshithc20")  # Check your actual username
#         password = urllib.parse.quote_plus("mongodb123")   # Check your actual password
#         cluster_url = f"mongodb+srv://{username}:{password}@cluster0.rten3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

#         # Connect to MongoDB
#         client = MongoClient(cluster_url)
#         db = client["RagLLM_database"]  # Replace with your actual database name
#         collection = db["response"]  # Replace with your actual collection name

#         # Test the connection
#         client.admin.command('ping')
#         print("Connected to MongoDB successfully!")
#         return collection
#     except errors.PyMongoError as e:
#         st.error(f"MongoDB connection error: {str(e)}")
#         return None

# # Function to store response in MongoDB
# def store_response_in_mongodb(collection, user_question, gpt_response):
#     try:
#         response_data = {
#             "user_question": user_question,
#             "response_from_LLM": gpt_response,
#             "timestamp": datetime.datetime.utcnow()  # Store the current time in UTC
#         }
#         collection.insert_one(response_data)  # Insert the data into MongoDB
#     except errors.PyMongoError as e:
#         st.error(f"Failed to store response in MongoDB: {str(e)}")

# # Function to retrieve latest responses from MongoDB
# def get_latest_responses(collection, limit=3):
#     try:
#         responses = list(collection.find().sort("timestamp", -1).limit(limit))
#         return responses
#     except errors.PyMongoError as e:
#         st.error(f"Failed to retrieve responses from MongoDB: {str(e)}")
#         return []

# # Streamlit application
# def main_function1():
#     st.title("Ascendum Chatbot Application")

#     # Connect to MongoDB
#     collection = connect_to_mongodb()

#     if collection is not None:
#         # Retrieve the latest 3 responses
#         limit = 6
#         latest_responses = get_latest_responses(collection, limit)

#         if latest_responses:
#             # Only show selectbox if there are responses
#             select_response_options = [f"Latest Response History {i+1}" for i in range(len(latest_responses))]

#             st.sidebar.header("Chat History")
#             selected_response_label = st.sidebar.selectbox("Select History", options=select_response_options)

#             # Get the index of the selected response
#             selected_index = select_response_options.index(selected_response_label)

#             # Fetch the corresponding response from MongoDB
#             selected_chat = latest_responses[selected_index]

#             # Display the selected response's details in the sidebar
#             st.sidebar.write(f"**Question:** {selected_chat.get('user_question', 'No question available')}")
#             st.sidebar.write(f"**Response:** {selected_chat.get('response_from_LLM', 'No response available')}")
#         else:
#             st.sidebar.write("No responses available in history.")

#         # Upload PDF file
#         uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
#         if uploaded_file is not None:
#             # Extract text from the PDF
#             pdf_text = extract_text_from_pdf(uploaded_file)
#             st.write("PDF content loaded successfully!")

#             # Input text from the user
#             user_input = st.text_input("Enter Your Question", "")

#             response = ""
#             # Generate response on button click
#             if st.button("Get Answer"):
#                 if user_input:
#                     response = generate_response(user_input, pdf_text)
#                     st.write(response)

#                     store_response_in_mongodb(collection, user_input, response)
#                     # language_translation(response)   
#                 else:
#                     st.warning("Please enter a question!")
#     else:
#         st.write("No History")


# if __name__ == "__main__":
#     main_function1()









# Added Language Translation


import openai
import streamlit as st
import pdfplumber
from pymongo import MongoClient, errors
import datetime
import urllib.parse
from dotenv import load_dotenv
import os
from googletrans import Translator

# Load the .env file from the specified path
env_path = os.path.join("..", "templates", ".env")
load_dotenv(dotenv_path=env_path)

# Set up your OpenAI API key
open_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = open_api_key

# Function to read and extract text from a PDF file
def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Function to generate a response from OpenAI's GPT model
def generate_response(prompt, context):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Provide complete and well-structured responses."},
            {"role": "user", "content": f"{context}\n\n{prompt}"},
        ],
        max_tokens=500,
        temperature=0.7,
    )
    return response['choices'][0]['message']['content'].strip()

# Function to connect to MongoDB Atlas
def connect_to_mongodb():
    try:
        username = urllib.parse.quote_plus("harshithc20")
        password = urllib.parse.quote_plus("mongodb123")
        cluster_url = f"mongodb+srv://{username}:{password}@cluster0.rten3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

        client = MongoClient(cluster_url)
        db = client["RagLLM_database"]
        collection = db["response"]

        client.admin.command('ping')
        print("Connected to MongoDB successfully!")
        return collection
    except errors.PyMongoError as e:
        st.error(f"MongoDB connection error: {str(e)}")
        return None

# Function to store response in MongoDB
def store_response_in_mongodb(collection, user_question, gpt_response):
    try:
        response_data = {
            "user_question": user_question,
            "response_from_LLM": gpt_response,
            "timestamp": datetime.datetime.utcnow()
        }
        collection.insert_one(response_data)
    except errors.PyMongoError as e:
        st.error(f"Failed to store response in MongoDB: {str(e)}")

# Function to retrieve latest responses from MongoDB
def get_latest_responses(collection, limit=3):
    try:
        responses = list(collection.find().sort("timestamp", -1).limit(limit))
        return responses
    except errors.PyMongoError as e:
        st.error(f"Failed to retrieve responses from MongoDB: {str(e)}")
        return []

# Streamlit application
def main_function1():
    st.title("Ascendum Chatbot Application")

    collection = connect_to_mongodb()

    if collection is not None:
        limit = 6
        latest_responses = get_latest_responses(collection, limit)

        if latest_responses:
            select_response_options = [f"Latest Response History {i+1}" for i in range(len(latest_responses))]

            st.sidebar.header("Chat History")
            selected_response_label = st.sidebar.selectbox("Select History", options=select_response_options)
            selected_index = select_response_options.index(selected_response_label)
            selected_chat = latest_responses[selected_index]
            st.sidebar.write(f"**Question:** {selected_chat.get('user_question', 'No question available')}")
            st.sidebar.write(f"**Response:** {selected_chat.get('response_from_LLM', 'No response available')}")
        else:
            st.sidebar.write("No responses available in history.")

        uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
        if uploaded_file is not None:
            pdf_text = extract_text_from_pdf(uploaded_file)
            st.write("PDF content loaded successfully!")

            user_input = st.text_input("Enter Your Question", "")
            response = ""
            if st.button("Get Answer"):
                if user_input:
                    response = generate_response(user_input, pdf_text)
                    st.session_state["response"] = response  # Store response in session state
                    st.write("Original Response:", response)
                    store_response_in_mongodb(collection, user_input, response)
                else:
                    st.warning("Please enter a question!")
            
            language_options = {
                'Hindi': 'hi',
                'Kannada': 'kn',
                'Malayalam': 'ml',
                'Tamil': 'ta',
                'Telugu': 'te',
                'Bengali': 'bn',
                'English': 'en'
            }

            if "selected_language" not in st.session_state:
                st.session_state["selected_language"] = 'en'

            to_lang = st.selectbox("Translate to", list(language_options.keys()), 
                                   index=list(language_options.values()).index(st.session_state["selected_language"]))
            
            st.session_state["selected_language"] = language_options[to_lang]

            if "response" in st.session_state:
                translator = Translator()
                original_response = st.session_state["response"]
                translated_text = ""
                if st.button("Translate"):
                    translated = translator.translate(original_response, 
                                                      src='en', 
                                                      dest=st.session_state["selected_language"])
                    translated_text = translated.text

                # Display Original and Translated text side by side
                col1, col2 = st.columns(2)

                with col1:
                    st.write("### Original Response")
                    st.write(original_response)

                with col2:
                    st.write("### Translated Response")
                    if translated_text:
                        st.write(translated_text)
                    else:
                        st.write("Click 'Translate' to see the translated text.")
    else:
        st.write("No History")


if __name__ == "__main__":
    main_function1()
