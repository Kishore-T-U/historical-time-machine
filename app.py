import streamlit as st
import os
import requests
import json  # ADDED: For saving data
from openai import OpenAI

# --- NEW: Permanent Save Functions ---
SAVE_FILE = "time_machine_history.json"

def load_history():
    """Loads the chat history from a local file if it exists."""
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return {} 

def save_history(history_dict):
    """Saves the current chat history to a local file."""
    with open(SAVE_FILE, "w") as f:
        json.dump(history_dict, f, indent=4)
# -------------------------------------

# 1. Page Configuration & Custom Vintage Theme
st.set_page_config(page_title="Historical Time Machine", page_icon="⏳", layout="wide")

# Inject Custom CSS for an "Ancient/Vintage" look
st.markdown("""
<style>
    /* 1. Base Vintage Background */
    .stApp {
        background-color: #f4ecd8;
        background-image: url("https://www.transparenttextures.com/patterns/aged-paper.png");
        font-family: 'Georgia', serif !important;
    }

    /* 2. FORCE Base Text to be Dark Ink */
    .stApp p, .stApp span, .stApp label, .stApp li {
        color: #2b1b17 !important; 
    }
    
    h1, h2, h3 {
        font-family: 'Georgia', serif !important;
        color: #3e2723 !important;
    }

    /* 3. FIX THE DROPDOWN BOXES */
    div[data-baseweb="select"] > div {
        background-color: #f4ecd8 !important;
        border: 1px solid #8d6e63 !important;
        color: #2b1b17 !important;
    }
    div[data-baseweb="popover"] div {
        background-color: #f4ecd8 !important;
        color: #2b1b17 !important;
    }

    /* 4. Vintage Stationary Chat Look */
    [data-testid="stChatMessage"] {
        background-color: #ede6d3 !important; 
        border: 1px solid #cbbba0 !important; 
        border-radius: 10px !important;       
        margin-bottom: 15px !important;       
        padding: 15px !important;
        box-shadow: 2px 2px 5px rgba(43, 27, 23, 0.08) !important; 
    }

    /* 5. Style the Sidebar */
    [data-testid="stSidebar"] {
        background-color: #e6dfcc;
        border-right: 2px solid #8d6e63;
    }

    /* 6. Fix Chat Input */
    [data-testid="stChatInput"] {
        background-color: #e6dfcc !important;
        border: 1px solid #8d6e63 !important;
    }

    /* 7. FIX: Header & Bottom Chat Background Blocks */
    [data-testid="stHeader"] {
        background-color: transparent !important; 
    }
    [data-testid="stBottom"] > div {
        background-color: transparent !important; 
    }
    [data-testid="collapsedControl"] svg, [data-testid="collapsedControl"] {
        color: #2b1b17 !important; 
        fill: #2b1b17 !important;
    }

    /* 8. FIX: Button Colors */
    .stButton > button[kind="primary"] p {
        color: #f4ecd8 !important; 
    }
    .stButton > button[kind="secondary"] {
        background-color: #e6dfcc !important;
        border: 1px solid #8d6e63 !important;
    }
    .stButton > button[kind="secondary"] p {
        color: #2b1b17 !important; 
    }
</style>
""", unsafe_allow_html=True)

st.info("📱 **Mobile Users:** Avoid swiping down from the very top of your screen to prevent accidentally refreshing the page and resetting your timeline.")

st.title("⏳ Historical Time Machine")
st.write("Summon historical figures and explore different timelines!")

# 2. Wikipedia Image Fetcher
def get_wikipedia_image(person_name):
    # A dictionary of your "Golden Path" characters
    golden_characters = {
        "Sherlock Holmes": "https://upload.wikimedia.org/wikipedia/commons/b/b5/Sherlock_Holmes_portrait.jpg",
        "Sun Wukong": "https://upload.wikimedia.org/wikipedia/commons/e/e0/Sun_Wukong.jpg",
        "Isaac Newton": "https://upload.wikimedia.org/wikipedia/commons/3/3b/Portrait_of_Sir_Isaac_Newton%2C_1689.jpg"
    }
    
    # Check if the character is in your curated list
    if person_name in golden_characters:
        return golden_characters[person_name]
    
    # Otherwise, run your normal logic...
    try:
        # ... (rest of the Wikipedia search code)
        # 1. Attempt to get from Wikipedia
        search_name = person_name.replace(" ", "_")
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{search_name}"
        headers = {"User-Agent": "HistoricalTimeMachine/2.0 (Hackathon)"}
        response = requests.get(url, headers=headers).json()
        
        if "thumbnail" in response and "source" in response["thumbnail"]:
            return response["thumbnail"]["source"]
        
        # 2. FALLBACK for fictional characters
        # If Wikipedia fails, use a generic "Legendary/Storybook" avatar
        # You can change this URL to any icon you prefer
        return "https://cdn-icons-png.flaticon.com/512/2809/2809636.png"
        
    except Exception:
        return "https://cdn-icons-png.flaticon.com/512/2809/2809636.png"
        
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
    st.session_state.messages = load_history()

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
        new_topic = st.text_input("Topic/Session Name *Required")
        # Add this line back in!
        custom_image = st.text_input("Image URL (Optional - paste here to override auto-search)")
        
        submitted = st.form_submit_button("Open New Timeline!")
        
        # We only require the name now to trigger the logic
        if submitted and new_name:
            # If user left the topic blank, default to "General Exploration"
            topic_label = new_topic.strip() if new_topic.strip() else "General Exploration"
            timeline_key = f"{new_name} ({topic_label})"
            
            with st.spinner(f"Searching the timeline for {new_name}..."):
                # Use custom image if provided, otherwise auto-search
                final_image = custom_image.strip() if custom_image.strip() else get_wikipedia_image(new_name)
            
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
            
            st.session_state.messages[active_timeline].append({"role": "assistant", "content": full_response})
            save_history(st.session_state.messages)
        except Exception as e:
            st.error("Timeline disruption! Make sure your GITHUB_TOKEN is set in Streamlit Secrets.")
