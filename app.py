import streamlit as st
import requests
import json

# Cloudflare Account Information
ACCOUNT_ID = "15c09f0f298a7e26646b104e34dc0a24"
AUTH_TOKEN = "p1R0Bg3D3wdVSdHzBGmSWv7jjT_MZCnNI_QuZaLu"
CHAT_MODEL = "@cf/qwen/qwen1.5-14b-chat-awq"
IMAGE_MODEL = "@cf/stabilityai/stable-diffusion-xl-base-1.0"

# Session data for chat history
session_state = st.session_state
if "messages" not in session_state:
    session_state["messages"] = [{"role": "system", "content": "You are a helpful assistant."}]
MAX_HISTORY_LENGTH = 6

def update_session(message):
    session_state["messages"].append({"role": "user", "content": message})
    if len(session_state["messages"]) > MAX_HISTORY_LENGTH:
        session_state["messages"].pop(1)  # Keep only the latest messages

def gpt_response(prompt):
    update_session(prompt)
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "max_tokens": 1024,
        "messages": session_state["messages"]
    }
    response = requests.post(
        f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/{CHAT_MODEL}",
        headers=headers,
        json=data
    )
    result = response.json()
    answer = result.get("result", {}).get("response")
    if answer:
        session_state["messages"].append({"role": "assistant", "content": answer})
        return answer
    return "No response from GPT model"

def generate_image(prompt, nsfw=False):
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {"prompt": prompt}
    if nsfw:
        data["nsfw"] = True
    response = requests.post(
        f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/{IMAGE_MODEL}",
        headers=headers,
        json=data
    )
    return response.content if response.status_code == 200 else "Image generation failed"

# Streamlit Interface
st.title("AI Assistant - GPT and Image Generation")

# Select command type (Chat or Image Generation)
command_type = st.selectbox("Select Command", ["Chat", "Image Generation"])

if command_type == "Chat":
    # Chat mode
    prompt = st.text_area("Enter your message", height=150)
    if st.button("Get Response"):
        if prompt:
            response = gpt_response(prompt)
            st.write(response)
        else:
            st.write("Please enter a message.")

elif command_type == "Image Generation":
    # Image generation mode
    image_prompt = st.text_input("Enter image description")
    nsfw_option = st.checkbox("Enable NSFW content")
    if st.button("Generate Image"):
        if image_prompt:
            image_content = generate_image(image_prompt, nsfw=nsfw_option)
            if isinstance(image_content, bytes):
                st.image(image_content, caption="Generated Image")
            else:
                st.write(image_content)
        else:
            st.write("Please enter a description for the image.")
            
