import streamlit as st
import os
from openai import OpenAI

# Simple page layout
st.set_page_config(page_title="Data Science Jargon Buster", layout="centered")
st.title("🧙‍♂️ Data Science Jargon Buster")
st.write("Translate complex data science concepts into simple, plain English instantly.")

# User input text box
user_query = st.text_input("Enter a complex term (e.g., 'Overfitting', 'Neural Networks', 'Linear Regression'):")

# Trigger button
if st.button("Explain like I'm 5"):
    if user_query:
        with st.spinner("Thinking..."):
            try:
                # Initialize the client pointing to GitHub's free model marketplace
                # It automatically looks for an environment variable named GITHUB_TOKEN
                client = OpenAI(
                    base_url="https://models.inference.ai.azure.com",
                    api_key=os.environ.get("GITHUB_TOKEN")
                )
                
                # Create the prompt instructing the AI how to behave
                prompt = f"Explain the following data science concept to an absolute beginner using a simple analogy: {user_query}"
                
                # Generate text using a highly relevant model available in the ecosystem
                response = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model="gpt-4o-mini", # Free, fast, and highly capable
                    temperature=1.0,
                    max_tokens=1000,
                )
                
                # Display output
                st.success("Here is the simple breakdown:")
                st.write(response.choices[0].message.content)
                
            except Exception as e:
                st.error(f"Error: {e}")
                st.info("Tip: Make sure your GITHUB_TOKEN environment variable is set up in your terminal!")
    else:
        st.warning("Please type a term first!")