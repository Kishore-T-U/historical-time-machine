import streamlit as st
import os
import requests
from openai import OpenAI

# 1. Page Configuration & Mobile Warning
st.set_page_config(page_title="Historical Time Machine", page_icon="⏳", layout="wide")

# Mobile Data Loss Warning Banner
st.info("📱 **Mobile Users:** Avoid swiping down from the very top of your screen to prevent accidentally refreshing the page and resetting your timeline.")

st.title("⏳ Historical Time Machine")
st.write("Summon historical figures and teach them modern concepts!")

# 2. Wikipedia Image Fetcher Helper Function
def get_wikipedia_image(name):
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={name}&prop=pageimages&format=json&pithumbsize=500"
    try:
        response = requests.get(url).json()
        pages = response['query']['pages']
        for page_id in pages:
            if 'thumbnail' in pages[page_id]:
                return pages[page_id]['thumbnail']['source']
    except Exception:
        pass
    # Fallback image if Wikipedia doesn't have a portrait
    return "https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png"

# 3. Initialize Session State (Memory)
if "personas" not in st.session_state:
    st.session_state.personas = {
        "Isaac Newton": {
            "dates": "1642–1727",
            "bio": "English mathematician, physicist, astronomer, and author.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/3/3b/Portrait_of_Sir_Isaac_Newton%2C_1689.jpg"
        },
        "Ada Lovelace": {
            "dates": "1815–1852",
            "bio": "English mathematician and writer, known for her work on the first mechanical computer.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/a/a4/Ada_Lovelace_portrait.jpg"
        }
    }

if "messages" not in st.session_state:
    # Create empty chat logs for everyone in the personas list
    st.session_state.messages = {name: [] for name in st.session_state.personas}

# 4. Sidebar UI
with st.sidebar:
    st.header("🕰️ Timeline Control")
    
    # Character Selection
    selected_character = st.selectbox(
        "Who are you talking to?", 
        options=list(st.session_state.personas.keys())
    )
    
    # Display Character Profile
    char_info = st.session_state.personas[selected_character]
    st.image(char_info["image"], use_container_width=True)
    st.subheader(selected_character)
    st.caption(char_info["dates"])
    st.write(char_info["bio"])
    
    # Delete Persona Button (Only show for custom characters)
    if selected_character not in ["Isaac Newton", "Ada Lovelace"]:
        if st.button(f"🗑️ Delete {selected_character}", type="primary", use_container_width=True):
            del st.session_state.personas[selected_character]
            if selected_character in st.session_state.messages:
                del st.session_state.messages[selected_character]
            st.success(f"{selected_character} erased from timeline!")
            st.rerun()

    # Clear Chat Button
    if st.button("🧹 Clear Current Chat", use_container_width=True):
        st.session_state.messages[selected_character] = []
        st.rerun()
        
    st.divider()
    
    # Summon New Character Form (AI AUTO-FILL VERSION)
    st.header("⚡ Summon Someone New")
    st.caption("Just type a name. Leave the rest blank to let the AI auto-fill it!")
    with st.form("new_persona_form"):
        new_name = st.text_input("Name (e.g., Marie Curie) *Required")
        new_dates = st.text_input("Dates (Optional)")
        new_bio = st.text_area("Brief Bio (Optional)")
        new_image = st.text_input("Image URL (Optional)")
        
        submitted = st.form_submit_button("Bring them to life!")
        
        if submitted and new_name:
            # Show a cool loading spinner while the AI works
            with st.spinner(f"Searching the timeline for {new_name}..."):
                
                # 1. Fetch Image from Wikipedia
                final_image = new_image if new_image.strip() else get_wikipedia_image(new_name)
                
                # 2. Auto-fill Dates and Bio using GPT-4o-mini
                final_dates = new_dates.strip()
                final_bio = new_bio.strip()
                
                if not final_dates or not final_bio:
                    try:
                        client = OpenAI(
                            base_url="https://models.inference.ai.azure.com",
                            api_key=os.environ.get("GITHUB_TOKEN")
                        )
                        # Ask the AI to research the missing info
                        prompt = f"Provide the birth and death years (format: YYYY-YYYY) and a 1-sentence biography for the historical figure {new_name}. Format your exact response like this:\nDates: [Years]\nBio: [Biography]"
                        
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.2, # Low temperature for factual accuracy
                            max_tokens=100
                        )
                        ai_data = response.choices[0].message.content
                        
                        # Extract the AI's answers
                        if not final_dates and "Dates:" in ai_data:
                            final_dates = ai_data.split("Dates:")[1].split("\n")[0].strip()
                        if not final_bio and "Bio:" in ai_data:
                            final_bio = ai_data.split("Bio:")[1].strip()
                    except Exception:
                        # Fallbacks just in case the API glitches
                        if not final_dates: final_dates = "Unknown Dates"
                        if not final_bio: final_bio = "A mysterious figure from history."
                
                # 3. Save to memory
                st.session_state.personas[new_name] = {
                    "dates": final_dates,
                    "bio": final_bio,
                    "image": final_image
                }
                if new_name not in st.session_state.messages:
                    st.session_state.messages[new_name] = []
                    
                st.success(f"Successfully summoned {new_name}!")
                st.rerun()

# 5. Main Chat Interface
st.header(f"Chatting with {selected_character}")

# Display Chat History
for msg in st.session_state.messages[selected_character]:
    with st.chat_message(msg["role"], avatar=char_info["image"] if msg["role"] == "assistant" else None):
        st.markdown(msg["content"])

# User Input
if prompt := st.chat_input(f"Teach {selected_character} something new..."):
    # Append user message to state and UI
    st.session_state.messages[selected_character].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # API Call
    with st.chat_message("assistant", avatar=char_info["image"]):
        message_placeholder = st.empty()
        
        try:
            # Connect to GitHub Models API
            client = OpenAI(
                base_url="https://models.inference.ai.azure.com",
                api_key=os.environ.get("GITHUB_TOKEN")
            )
            
            # Extract the death year dynamically for the prompt
            death_year = "your time"
            if "–" in char_info['dates']:
                death_year = char_info['dates'].split('–')[-1].strip()
            elif "-" in char_info['dates']:
                death_year = char_info['dates'].split('-')[-1].strip()

            # The Strict System Prompt
            system_prompt = f"""
            You are strictly {selected_character}. 
            Your biography: {char_info['bio']}. 
            You lived during {char_info['dates']}. 
            
            CRITICAL INSTRUCTIONS:
            1. You have absolutely no knowledge of any events, people, discoveries, or technology that occurred after your death in {death_year}.
            2. If a user asks you about someone like Albert Einstein, quantum mechanics, or modern technology, you must respond with confusion, stating that you have never heard of these things. 
            3. You must act exactly as this person would. Do not break character.
            4. Use analogies only from your own time period.
            5. Respond with curiosity and stay strictly in the persona of a person living in your era.
            """
            
            messages_for_api = [{"role": "system", "content": system_prompt}]
            # Only send the last 5 messages to save tokens and keep it fast
            messages_for_api.extend(st.session_state.messages[selected_character][-5:])
            
            # Generate Response
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages_for_api,
                temperature=0.7,
                max_tokens=1000
            )
            
            full_response = response.choices[0].message.content
            message_placeholder.markdown(full_response)
            
            # Save AI response to memory
            st.session_state.messages[selected_character].append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error("Timeline disruption! Make sure your GITHUB_TOKEN is set in Streamlit Secrets.")
