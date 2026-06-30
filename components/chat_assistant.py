import os
import streamlit as st
import requests


def _get_api_url():
    try:
        if "API_URL" in st.secrets:
            return st.secrets["API_URL"]
    except Exception:
        pass
    return os.environ.get("API_URL", "http://127.0.0.1:8000")


API_URL = _get_api_url()


def guardian_chat():

    st.sidebar.header("🤖 Guardian AI")

    question = st.sidebar.text_input(
        "Ask Guardian AI"
    )

    if st.sidebar.button("Ask Guardian"):

        if not question:
            st.sidebar.warning(
                "Enter a question first."
            )
            return

        try:

            response = requests.post(
                f"{API_URL}/chat",
                json={
                    "question": question
                }
            )

            result = response.json()

            st.sidebar.success(
                result["answer"]
            )

        except Exception as e:

            st.sidebar.error(
                str(e)
            )