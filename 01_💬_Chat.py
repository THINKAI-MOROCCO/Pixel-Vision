import os
import csv
import datetime
import ollama
import streamlit as st
from openai import OpenAI
from utilities.icon import page_icon

# Function to save messages in a CSV file
def save_messages(messages, folder="archive"):
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(folder, f"messages_{timestamp}.csv")
    
    with open(filename, "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Time", "Role", "Content"])
        for message in messages:
            writer.writerow([message["time"], message["role"], message["content"]])

st.set_page_config(
    page_title="Chat playground",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)


def extract_model_names(models_info: list) -> tuple:
    """
    Extracts the model names from the models information.

    :param models_info: A dictionary containing the models' information.

    Return:
        A tuple containing the model names.
    """

    return tuple(model["name"] for model in models_info["models"])

import requests
import json

def translate_text(text, source_lang, target_lang):
    url = 'https://winstxnhdw-nllb-api.hf.space/api/v2/translate'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization':'Bearer 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'
    }
    payload = {
        'text': text,
        'source': source_lang,
        'target': target_lang
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Oops! An unexpected error occurred:", err)
    
    return None

def main():
    """
    The main function that runs the application.
    """

    st.image("utilities/logo.png", width=100)  # Adjust the path and width as needed
    st.subheader("Test and improve your medical information with our chatbot", divider="red", anchor=False)

    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",  # required, but unused
    )

    models_info = ollama.list()
    available_models = extract_model_names(models_info)

    if available_models:
        #selected_model = st.selectbox(   "Pick a model available locally on your system ↓", available_models)
        
        selected_model = "rohithbojja/llava-med-v1.6:latest"

    else:
        st.warning("You have not pulled any model from Ollama yet!", icon="⚠️")
        if st.button("Go to settings to download a model"):
            st.page_switch("pages/03_⚙️_Settings.py")

    message_container = st.container(height=500, border=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        avatar = "🤖" if message["role"] == "assistant" else "😎"
        with message_container.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if prompt := st.chat_input("Enter a prompt here..."):
        try:
            st.session_state.messages.append(
                {"time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 "role": "user",
                 "content": prompt})

            message_container.chat_message("user", avatar="😎").markdown(prompt)

            with message_container.chat_message("assistant", avatar="🤖"):
                with st.spinner("model working..."):
                    stream = client.chat.completions.create(
                        model=selected_model,
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                        stream=True,
                    )
                # stream response
                response = st.write_stream(stream)
            st.session_state.messages.append(
                {"time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 "role": "assistant",
                 "content": response})

        except Exception as e:
            st.error(e, icon="⛔️")

    # Button to archive messages
    if st.button("Archive Messages"):
        save_messages(st.session_state.messages)

if __name__ == "__main__":
    main()
