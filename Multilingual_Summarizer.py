import streamlit as st
import openai
import requests
import os
from SECRET_KEY import GROQ_API_KEY

# Set up Groq API credentials
GROQ_API_KEY = GROQ_API_KEY  # Replace with your actual Groq API Key
GROQ_API_URL = "https://api.groq.com/openai/v1"

# Fixed Model Selection
WHISPER_MODEL = "whisper-large-v3-turbo"
SUMMARIZATION_MODEL = "mixtral-8x7b-32768"

# Streamlit UI
st.title("🌍 Multilingual Podcast Transcriber & Summarizer with Token Count")
st.markdown("Upload an audio file to transcribe and summarize using Groq's AI models.")

# Sidebar for Token Count
st.sidebar.title("📊 Token Usage")

# Initialize token counters
transcription_tokens = 0
summary_tokens = 0

# File Upload
uploaded_file = st.file_uploader("Upload an audio file (MP3, WAV)", type=["mp3", "wav"])

if uploaded_file:
    st.audio(uploaded_file, format="audio/mp3")

    # Save file temporarily
    temp_audio_path = "temp_audio.mp3"
    with open(temp_audio_path, "wb") as f:
        f.write(uploaded_file.read())

    # Transcribe audio using Groq Whisper API
    with st.spinner("Transcribing..."):
        try:
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
            
            # Open file in a 'with' statement to ensure it's properly closed
            with open(temp_audio_path, "rb") as audio_file:
                files = {"file": audio_file}
                data = {"model": WHISPER_MODEL}

                response = requests.post(f"{GROQ_API_URL}/audio/transcriptions", headers=headers, files=files, data=data)
                response_json = response.json()

            if response.status_code == 200 and "text" in response_json:
                transcribed_text = response_json["text"]
                st.success("✅ Transcription Complete!")
                st.text_area("Transcribed Text:", transcribed_text, height=200)

                # Count tokens in the transcribed text (Assuming 1.5 tokens per word)
                transcription_tokens = int(len(transcribed_text.split()) * 1.5)
            else:
                st.error(f"Transcription Error: {response_json}")

        except Exception as e:
            st.error(f"Error during transcription: {e}")

    # Display Transcription Token Count in Sidebar
    st.sidebar.info(f"🎙 *Transcription Tokens*: {transcription_tokens}")

    # Summarize text using Groq Mixtral Model
    if st.button("Summarize Text"):
        with st.spinner("Generating summary..."):
            try:
                client = openai.OpenAI(
                    api_key=GROQ_API_KEY,
                    base_url=GROQ_API_URL
                )

                response = client.chat.completions.create(
                    model=SUMMARIZATION_MODEL,
                    messages=[
                        {"role": "system", "content": "Summarize the given text concisely."},
                        {"role": "user", "content": transcribed_text}
                    ],
                    temperature=0.7,
                    max_tokens=150
                )

                summary_text = response.choices[0].message.content
                st.success("✅ Summary Generated!")
                st.text_area("Summary:", summary_text, height=100)

                # Count tokens in summary (Assuming 1.5 tokens per word)
                summary_tokens = int(len(summary_text.split()) * 1.5)

            except Exception as e:
                st.error(f"Error during summarization: {e}")

    # Display Summary Token Count in Sidebar
    st.sidebar.info(f"📄 *Summary Tokens*: {summary_tokens}")

    # Display Total Token Count in Sidebar
    total_tokens = transcription_tokens + summary_tokens
    st.sidebar.success(f"🔢 *Total Tokens Used*: {total_tokens}")

    # Delete temp file only after everything is done
    try:
        os.remove(temp_audio_path)
    except Exception as e:
        st.warning(f"⚠ Could not delete temporary file: {e}")