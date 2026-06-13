import streamlit as st
import os
import requests
from openai import OpenAI

# 1. Page Configuration & Custom Vintage Theme
st.set_page_config(page_title="Historical Time Machine", page_icon="⏳", layout="wide")

# Inject Custom CSS for an "Ancient/Vintage" look
st.markdown("""
<style>
    /* Vintage parchment background pattern */
    .stApp {
        background-color: #f4ecd8;
        background-image: url("https://www.transparenttextures.com/patterns/aged-paper.png");
        font-family: 'Georgia', serif !important;
        color: #2b1b17;
    }
    /* Make headers match the theme */
    h1, h2, h3 {
        font-family: 'Georgia', serif !important;
        color: #3e2723 !important;
    }
    /* Style the sidebar to look like a leather binding */
    [data-testid="stSidebar"] {
        background-color: #e6dfcc;
        border-right: 2px solid #8d6e63;
    }
</style>
""", unsafe_allow_html=True)

st.info("📱 **Mobile Users:** Avoid swiping down from the very top of your screen to prevent accidentally refreshing the page and resetting your timeline.")

st.title("⏳ Historical Time Machine")
st.write("Summon historical figures and explore different timelines!")

# 2. Wikipedia Image Fetcher
def get_wikipedia_image(person_name):
    try:
        search_name = person_name.replace(" ", "_")
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{search_name}"
        headers = {"User-Agent": "HistoricalTimeMachine/2.0 (Hackathon Project)"}
        response = requests.get(url, headers=headers).json()
        if "thumbnail" in response:
            return response["thumbnail"]["source"]
    except Exception:
        pass
    return "https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png"

# 3. Initialize Session State (Memory)
if "personas" not in st.session_state:
    # Notice we now store the 'base_name' so the AI knows who it is, even if the timeline has a custom topic!
    st.session_state.personas = {
        "Isaac Newton (Calculus)": {
            "base_name": "Isaac Newton",
            "dates": "1642–1727",
            "bio": "English mathematician, physicist, astronomer, and author.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/3/3b/Portrait_of_Sir_Isaac_Newton%2C_1689.jpg"
        },
        "Ada Lovelace (Engines)": {
            "base_name": "Ada Lovelace",
            "dates": "1815–1852",
            "bio": "English mathematician and writer, known for her work on the first mechanical computer.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/a/a4/Ada_Lovelace_portrait.jpg"
        }
    }

if "messages" not in st.session_state:
    st.session_state.messages = {name: [] for name in st.session_state.personas}

# 4. Sidebar UI
with st.sidebar:
    st.header("🕰️ Timeline Control")
    
    selected_character = st.selectbox(
        "Select an active timeline:", 
        options=list(st.session_state.personas.keys())
    )
    
    char_info = st.session_state.personas[selected_character]
    st.image(char_info["image"], use_container_width=True)
    st.subheader(char_info["base_name"])
    st.caption(char_info["dates"])
    st.write(char_info["bio"])
    
    # ---------------------------------------------------------
    # NEW FEATURE: Export Chat Log
    # ---------------------------------------------------------
    chat_history = st.session_state.messages[selected_character]
    if chat_history:
        # Format the chat into a readable text document
        export_text = f"--- Timeline: {selected_character} ---\n\n"
        for msg in chat_history:
            role = "You" if msg["role"] == "user" else char_info["base_name"]
            export_text += f"{role}: {msg['content']}\n\n"
            
        st.download_button(
            label="💾 Download Chat Log",
            data=export_text,
            file_name=f"{selected_character.replace(' ', '_')}_Log.txt",
            mime="text/plain",
            use_container_width=True
        )
    # ---------------------------------------------------------

    if selected_character not in ["Isaac Newton (Calculus)", "Ada Lovelace (Engines)"]:
        if st.button(f"🗑️ Delete Timeline", type="primary", use_container_width=True):
            del st.session_state.personas[selected_character]
            if selected_character in st.session_state.messages:
                del st.session_state.messages[selected_character]
            st.success("Timeline erased!")
            st.rerun()

    if st.button("🧹 Clear Chat", use_container_width=True):
        st.session_state.messages[selected_character] = []
        st.rerun()
        
    st.divider()
    
    # Summon New Character Form (With Parallel Timelines!)
    st.header("⚡ Summon Someone New")
    st.caption("Create a new instance of a character to discuss a new topic!")
    with st.form("new_persona_form"):
        new_name = st.text_input("Name (e.g., Nikola Tesla) *Required")
        new_topic = st.text_input("Topic/Session Name (e.g., Radio Waves) *Required")
        
        submitted = st.form_submit_button("Open New Timeline!")
        
        if submitted and new_name and new_topic:
            timeline_key = f"{new_name} ({new_topic})" # Creates a unique key like "Nikola Tesla (Radio Waves)"
            
            with st.spinner(f"Searching the timeline for {new_name}..."):
                final_image = get_wikipedia_image(new_name)
                
                # Auto-fill using AI
                try:
                    client = OpenAI(
                        base_url="https://models.inference.ai.azure.com",
                        api_key=os.environ.get("GITHUB_TOKEN")
                    )
                    prompt = f"Provide the birth and death years (format: YYYY-YYYY) and a 1-sentence biography for {new_name}. Format: \nDates: [Years]\nBio: [Biography]"
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.2, max_tokens=100
                    )
                    ai_data = response.choices[0].message.content
                    final_dates = ai_data.split("Dates:")[1].split("\n")[0].strip() if "Dates:" in ai_data else "Unknown"
                    final_bio = ai_data.split("Bio:")[1].strip() if "Bio:" in ai_data else "A figure from history."
                except Exception:
                    final_dates = "Unknown Dates"
                    final_bio = "A mysterious figure from history."
                
                st.session_state.personas[timeline_key] = {
                    "base_name": new_name, # Store the actual name for the AI prompt
                    "dates": final_dates,
                    "bio": final_bio,
                    "image": final_image
                }
                if timeline_key not in st.session_state.messages:
                    st.session_state.messages[timeline_key] = []
                    
                st.success(f"Timeline opened: {timeline_key}!")
                st.rerun()

# 5. Main Chat Interface
st.header(f"Chatting with {char_info['base_name']}")

# Display Chat History (With custom User Avatar 👤)
for msg in st.session_state.messages[selected_character]:
    # If user, use silhouette. If AI, use their Wikipedia photo.
    avatar_choice = "👤" if msg["role"] == "user" else char_info["image"]
    with st.chat_message(msg["role"], avatar=avatar_choice):
        st.markdown(msg["content"])

# User Input
if prompt := st.chat_input(f"Teach {char_info['base_name']} something new..."):
    
    st.session_state.messages[selected_character].append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=char_info["image"]):
        message_placeholder = st.empty()
        try:
            client = OpenAI(
                base_url="https://models.inference.ai.azure.com",
                api_key=os.environ.get("GITHUB_TOKEN")
            )
            
            death_year = "your time"
            if "–" in char_info['dates']:
                death_year = char_info['dates'].split('–')[-1].strip()
            elif "-" in char_info['dates']:
                death_year = char_info['dates'].split('-')[-1].strip()

            system_prompt = f"""
            You are strictly {char_info['base_name']}. 
            Your biography: {char_info['bio']}. 
            You lived during {char_info['dates']}. 
            
            CRITICAL INSTRUCTIONS:
            1. You have absolutely no knowledge of any events, people, discoveries, or technology that occurred after your death in {death_year}.
            2. If asked about modern topics, respond with confusion.
            3. You must act exactly as {char_info['base_name']} would. Do not break character.
            4. Use analogies only from your own time period.
            """
            
            messages_for_api = [{"role": "system", "content": system_prompt}]
            messages_for_api.extend(st.session_state.messages[selected_character][-5:])
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages_for_api,
                temperature=0.7,
                max_tokens=1000
            )
            
            full_response = response.choices[0].message.content
            message_placeholder.markdown(full_response)
            
            st.session_state.messages[selected_character].append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error("Timeline disruption! Make sure your GITHUB_TOKEN is set in Streamlit Secrets.")
