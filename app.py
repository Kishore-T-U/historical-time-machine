import streamlit as st
import os
import requests
from openai import OpenAI

# --- UI Configuration & Custom CSS ---
st.set_page_config(page_title="Historical Time Machine", page_icon="⏳", layout="centered")

st.markdown("""
<style>
    .stChatFloatingInputContainer { padding-bottom: 20px; }
    .profile-card { background-color: #f9f9f9; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; color: #333;}
    .bio-text { font-size: 0.95rem; color: #555; }
</style>
""", unsafe_allow_html=True)

# --- Initialize AI Client ---
client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ.get("GITHUB_TOKEN")
)

# --- Helper Function: Fetch Wikipedia Image ---
# --- Helper Function: Fetch Wikipedia Image ---
def get_wiki_image(person_name):
    """Hits the free Wikipedia API to grab the main image for a historical figure."""
    try:
        # Replace spaces with underscores for the URL
        search_name = person_name.replace(" ", "_")
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{search_name}"
        
        # Give our app a "Name Badge" so Wikipedia doesn't block us!
        headers = {
            "User-Agent": "HackathonTimeMachineApp/1.0 (Student Project)"
        }
        
        response = requests.get(url, headers=headers).json()
        
        # If Wikipedia has a thumbnail for this person, return it!
        if "thumbnail" in response:
            return response["thumbnail"]["source"]
    except Exception:
        pass
    # Fallback to the default placeholder if Wikipedia fails or has no image
    return "https://upload.wikimedia.org/wikipedia/commons/7/7c/Profile_avatar_placeholder_large.png"
# --- The Persona Library ---
if "library" not in st.session_state:
    st.session_state.library = {
        "Isaac Newton": {
            "image": "https://upload.wikimedia.org/wikipedia/commons/3/39/GodfreyKneller-IsaacNewton-1689.jpg",
            "bio": "Born: December 25, 1642<br>Died: March 20, 1726<br><em>English mathematician, physicist, astronomer, and author.</em>",
            "history": [
                {"role": "system", "content": "You are Sir Isaac Newton. Speak with proper, older English. React with intense curiosity to modern concepts. CRITICAL: Always format math equations using $ for inline and $$ for block equations."},
                {"role": "assistant", "content": "Greetings, traveler. I was just pondering the laws of motion. What strange knowledge do you bring?"}
            ]
        },
        "Ada Lovelace": {
            "image": "https://upload.wikimedia.org/wikipedia/commons/a/a4/Ada_Lovelace_portrait.jpg",
            "bio": "Born: December 10, 1815<br>Died: November 27, 1852<br><em>English mathematician and the world's first computer programmer.</em>",
            "history": [
                {"role": "system", "content": "You are Ada Lovelace. Speak eloquently. Compare modern tech to Charles Babbage's Analytical Engine. CRITICAL: Always format math equations using $ for inline and $$ for block equations."},
                {"role": "assistant", "content": "Good day! Has the future built a machine that can calculate beyond mere numbers?"}
            ]
        }
    }
    st.session_state.current_persona = "Isaac Newton"

# --- Sidebar: The Library & Summoning Menu ---
with st.sidebar:
    st.title("⏳ Time Machine")
    st.write("Switch between your active historical chats:")
    
    for persona_name in st.session_state.library.keys():
        if st.button(f"🗣️ {persona_name}", use_container_width=True):
            st.session_state.current_persona = persona_name
    # --- Clear Memory Button ---
    st.write("") # Adds a tiny bit of spacing
    if st.button("🗑️ Clear Current Chat", type="secondary", use_container_width=True):
        # We grab the current person
        person = st.session_state.current_persona
        # We slice their history to ONLY keep the first two messages (System Prompt & First Greeting)
        st.session_state.library[person]["history"] = st.session_state.library[person]["history"][:2]
        st.rerun() # Refresh the screen instantly        
    st.divider()
    
    st.header("✨ Summon Someone New")
    new_name = st.text_input("Name (e.g., Albert Einstein):")
    new_born = st.text_input("Birth/Death Dates:")
    new_desc = st.text_area("Short Bio/Description:")
    new_img = st.text_input("Image URL (Optional):", placeholder="Leave blank for auto-fetch!")
    
    if st.button("Bring them to life!", type="primary"):
        if new_name and new_desc and new_name not in st.session_state.library:
            custom_prompt = f"You are {new_name}, {new_desc}. Speak authentically to your era. CRITICAL: Always format math equations using $ for inline and $$ for block equations."
            
            # If the user leaves the image URL blank, auto-fetch from Wikipedia!
            img_url = new_img if new_img else get_wiki_image(new_name)
            
            st.session_state.library[new_name] = {
                "image": img_url,
                "bio": f"Dates: {new_born}<br><em>{new_desc}</em>",
                "history": [
                    {"role": "system", "content": custom_prompt},
                    {"role": "assistant", "content": f"Where am I? Who are you? I am {new_name}."}
                ]
            }
            st.session_state.current_persona = new_name
            st.rerun()

# --- Main App Area: The Homely Profile Header ---
active_person = st.session_state.library[st.session_state.current_persona]

st.markdown(f"""
<div class="profile-card">
    <div style="display: flex; align-items: center; gap: 20px;">
        <img src="{active_person['image']}" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 3px solid #ddd;">
        <div>
            <h2 style="margin: 0; padding: 0; color: #111;">{st.session_state.current_persona}</h2>
            <div class="bio-text">{active_person['bio']}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- The Chat Interface ---
for msg in active_person["history"]:
    if msg["role"] != "system":
        avatar_img = active_person["image"] if msg["role"] == "assistant" else "🧑‍🚀"
        with st.chat_message(msg["role"], avatar=avatar_img):
            st.markdown(msg["content"])

# --- Chat Input Box ---
if user_prompt := st.chat_input(f"Teach {st.session_state.current_persona} something new..."):
    
    active_person["history"].append({"role": "user", "content": user_prompt})
    with st.chat_message("user", avatar="🧑‍🚀"):
        st.markdown(user_prompt)
        
    with st.chat_message("assistant", avatar=active_person["image"]):
        with st.spinner(f"{st.session_state.current_persona} is pondering your words..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=active_person["history"],
                    temperature=0.8,
                    max_tokens=1000
                )
                
                ai_reply = response.choices[0].message.content
                
                # --- BULLETPROOF MATH FIX ---
                # This explicitly forces OpenAI's bracket formatting into Streamlit's dollar sign formatting
                ai_reply = ai_reply.replace(r"\[", "$$").replace(r"\]", "$$").replace(r"\(", "$").replace(r"\)", "$")
                
                st.markdown(ai_reply)
                active_person["history"].append({"role": "assistant", "content": ai_reply})
                
            except Exception as e:
                st.error(f"Oops! Something went wrong: {e}")
