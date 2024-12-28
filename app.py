from deep_translator import GoogleTranslator
import deep_translator
import streamlit as st
from streamlit import session_state
import json
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from st_audiorec import st_audiorec
import speech_recognition as sr
from pydub import AudioSegment
import io

session_state = st.session_state
if "user_index" not in st.session_state:
    st.session_state["user_index"] = 0


load_dotenv()

def agriculture_specialist(question):
    try:
        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        prompt = f"""
            Welcome to the AI Agriculture Specialist! 🌱 I'm here to provide expert advice and guidance on all things related to agriculture. Whether you're a seasoned farmer or just starting out, I'm here to help you navigate the complexities of agricultural practices.

            Question: {question}
            """

        messages = [{"role": "system", "content": prompt}]
        response = client.chat.completions.create(
            messages=messages,
            # model="gpt-3.5-turbo",
            model="gpt-3.5-turbo-0125",
        )

        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
    
# def tamil_response(sentence):
#     try:
#         client = OpenAI(
#             api_key=os.environ.get("OPENAI_API_KEY"),
#         )
#         prompt = f"""
#             You are a helpful AI assistant that can translate English to Tamil. You are asked to translate the following English sentence to Tamil: {sentence}
#             Give the Tamil translation of the sentence in roman script.
            
#             For example, if the English sentence is "Hello, how are you?", the Tamil translation in roman script would be "Vanakkam, eppadi irukkinga?"
#             """

#         messages = [{"role": "system", "content": prompt}]
#         response = client.chat.completions.create(
#             messages=messages,
#             # model="gpt-3.5-turbo",
#             model="gpt-3.5-turbo-0125",
#         )

#         return response.choices[0].message.content
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return None

def tamil_response(sentence):
    try:
        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        prompt = f"""
            You are a helpful AI assistant capable of translating English to Tamil using the Roman script. Your task is to translate the provided English sentence to Tamil using the Roman script. Make sure to provide translations using English letters that correspond to Tamil sounds.

            Example:
            English: "Hello, how are you?"
            Tamil (Roman script): "Vanakkam, eppadi irukkinga?"
            English : How Many Types of Urea are There?
            Tamil (Roman script) : "Prilled and granules iruku. Athu Ammonia and carbon dioxide pola reaction ah produce pannum"
            Translate the following English sentence to Tamil using Roman script:
            {sentence}
            
            For instance, if the English sentence is "What is your name?", the Tamil translation in Roman script would be "Un peyar enna?"
            """

        messages = [{"role": "system", "content": prompt}]
        response = client.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo-0125",  # You might need to adjust the model based on availability
        )

        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def signup(json_file_path="data.json"):
    st.title("Signup Page")
    with st.form("signup_form"):
        st.write("Fill in the details below to create an account:")
        name = st.text_input("Name:")
        email = st.text_input("Email:")
        age = st.number_input("Age:", min_value=0, max_value=120)
        sex = st.radio("Sex:", ("Male", "Female", "Other"))
        password = st.text_input("Password:", type="password")
        confirm_password = st.text_input("Confirm Password:", type="password")

        if st.form_submit_button("Signup"):
            if password == confirm_password:
                user = create_account(
                    name,
                    email,
                    age,
                    sex,
                    password,
                    json_file_path,
                )
                session_state["logged_in"] = True
                session_state["user_info"] = user
            else:
                st.error("Passwords do not match. Please try again.")


def check_login(username, password, json_file_path="data.json"):
    try:
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)

        for user in data["users"]:
            if user["email"] == username and user["password"] == password:
                session_state["logged_in"] = True
                session_state["user_info"] = user
                st.success("Login successful!")
                return user
        return None
    except Exception as e:
        st.error(f"Error checking login: {e}")
        return None


def initialize_database(json_file_path="data.json"):
    try:
        if not os.path.exists(json_file_path):
            data = {"users": []}
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file)
    except Exception as e:
        print(f"Error initializing database: {e}")


def create_account(
    name,
    email,
    age,
    sex,
    password,
    json_file_path="data.json",
):
    try:
        # Check if the JSON file exists or is empty
        if not os.path.exists(json_file_path) or os.stat(json_file_path).st_size == 0:
            data = {"users": []}
        else:
            with open(json_file_path, "r") as json_file:
                data = json.load(json_file)

        # Append new user data to the JSON structure
        user_info = {
            "name": name,
            "email": email,
            "age": age,
            "sex": sex,
            "password": password,
            "report": None,
            "questions": None,
        }
        data["users"].append(user_info)

        # Save the updated data to JSON
        with open(json_file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

        st.success("Account created successfully! You can now login.")
        return user_info
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON: {e}")
        return None
    except Exception as e:
        st.error(f"Error creating account: {e}")
        return None


def login(json_file_path="data.json"):
    st.title("Login Page")
    username = st.text_input("Email:")
    password = st.text_input("Password:", type="password")

    login_button = st.button("Login")

    if login_button:
        user = check_login(username, password, json_file_path)
        if user is not None:
            session_state["logged_in"] = True
            session_state["user_info"] = user
        else:
            st.error("Invalid credentials. Please try again.")


def get_user_info(email, json_file_path="data.json"):
    try:
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)
            for user in data["users"]:
                if user["email"] == email:
                    return user
        return None
    except Exception as e:
        st.error(f"Error getting user information: {e}")
        return None

def get_audio_data(wav_audio_data):
    audio_segment = AudioSegment.from_wav(io.BytesIO(wav_audio_data))
    mp3_data = io.BytesIO()
    audio_segment.export(mp3_data, format="mp3")
    return mp3_data.getvalue()


def render_dashboard(user_info, json_file_path="data.json"):
    try:
        # add profile picture
        st.title(f"Welcome to the Dashboard, {user_info['name']}!")
        st.subheader("User Information:")
        st.write(f"Name: {user_info['name']}")
        st.write(f"Sex: {user_info['sex']}")
        st.write(f"Age: {user_info['age']}")
    except Exception as e:
        st.error(f"Error rendering dashboard: {e}")


def main(json_file_path="data.json"):

    st.sidebar.title("Smart Business Assistant")
    page = st.sidebar.radio(
        "Go to",
        (
            "Signup/Login",
            "Dashboard",
            "Get Agriculture Information",
        ),
        key="pages",
    )

    if page == "Signup/Login":
        st.title("Signup/Login Page")
        login_or_signup = st.radio(
            "Select an option", ("Login", "Signup"), key="login_signup"
        )
        if login_or_signup == "Login":
            login(json_file_path)
        else:
            signup(json_file_path)

    elif page == "Dashboard":
        if session_state.get("logged_in"):
            render_dashboard(session_state["user_info"])
        else:
            st.warning("Please login/signup to view the dashboard.")
            
    elif page == "Get Agriculture Information":
        if session_state.get("logged_in"):
            user_info = session_state["user_info"]
            st.title("Get Agriculture Information")
            recognizer = sr.Recognizer()
            microphone = sr.Microphone()
            if st.button("Ask a question"):
                with microphone as source:
                    st.info("Listening...")
                    recognizer.adjust_for_ambient_noise(source)
                    audio = recognizer.listen(source)   
                    voice_command_tamil = recognizer.recognize_google(audio, language="ta-IN")
                    english_command = GoogleTranslator(source='auto', target='en').translate(voice_command_tamil)
                    st.write(f"Question: {english_command}")
                    response = agriculture_specialist(english_command)
                    tamil_response_text = tamil_response(response)
                    st.write(f"Response: {tamil_response_text}")
            
        else:
            st.warning("Please login/signup to chat.")

if __name__ == "__main__":
    initialize_database()
    main()
