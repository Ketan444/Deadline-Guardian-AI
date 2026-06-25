import streamlit as st
import requests


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
                "http://127.0.0.1:8000/chat",
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