import re
import sys
from io import StringIO
import streamlit as st
import PyPDF2
import os
import requests
import json  
import base64
from openai import OpenAI

# ---------------------------------------------------------
# 1. USER ISOLATION & LOCAL STORAGE
# ---------------------------------------------------------
try:
    # Grabs the email of the person currently looking at the app (Streamlit Cloud)
    current_user = st.experimental_user.email
except:
    # Fallback just in case you run it locally
    current_user = "local_user"

# Create a completely separate database file for every unique user
SAVE_FILE = f"time_machine_{current_user}.json"

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

def format_ai_math(text):
    """Formats mathematical equations and protects against image arrays."""
    # Handle Image/Multimodal Lists
    if isinstance(text, list):
        extracted_text = ""
        for item in text:
            if isinstance(item, dict) and item.get("type") == "text":
                extracted_text = item.get("text", "")
                break
        text = extracted_text
        
    # Safety net: force it to be a string
    if not isinstance(text, str):
        text = str(text)

    # Standardize math formatting
    text = text.replace(r"\[", "$$").replace(r"\]", "$$")
    text = text.replace(r"\(", "$").replace(r"\)", "$")
    
    return text

# ---------------------------------------------------------
# 2. PAGE CONFIGURATION & THEME
# ---------------------------------------------------------
st.set_page_config(page_title="Omni-Reality Communicator", page_icon="🌌", layout="wide") 
# (You can also change the emoji icon to something cool like 🌌, ⚡, or 🛰️)

# Inject Custom CSS for an "Ancient/Vintage" look
st.markdown("""
<style>
    /* 1. Omni Dark Multiverse Background */
    .stApp {
        background-color: #0b0f19; /* Deep space dark blue/black */
        color: #e0e6ed !important;
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
    }

    /* 2. Base Text Colors */
    .stApp p, .stApp span, .stApp label, .stApp li {
        color: #e0e6ed !important;
    }
    
    h1, h2, h3 {
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
        color: #ffffff !important;
        letter-spacing: 1px;
    }

    /* 3. Sleek Dropdowns */
    div[data-baseweb="select"] > div {
        background-color: #1a2333 !important;
        border: 1px solid #3b82f6 !important; /* Omni Blue Accent */
        color: #ffffff !important;
    }
    div[data-baseweb="popover"] div {
        background-color: #1a2333 !important;
        color: #ffffff !important;
    }

    /* 4. Omni Chat Bubbles */
    [data-testid="stChatMessage"] {
        background-color: #131b2b !important;
        border: 1px solid #2d3748 !important; 
        border-radius: 12px !important;       
        margin-bottom: 15px !important;       
        padding: 15px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3) !important; 
    }

    /* 5. Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0d131f;
        border-right: 1px solid #1f2937;
    }

    /* 6. Chat Input */
    [data-testid="stChatInput"] {
        background-color: #1a2333 !important;
        border: 1px solid #3b82f6 !important;
    }

    /* 7. Header Fixes */
    [data-testid="stHeader"], [data-testid="stBottom"] > div {
        background-color: transparent !important;
    }
    [data-testid="collapsedControl"] svg, [data-testid="collapsedControl"] {
        color: #ffffff !important;
        fill: #ffffff !important;
    }

    /* 8. Omni Buttons */
    .stButton > button[kind="primary"] {
        background-color: #3b82f6 !important;
        border: none !important;
        border-radius: 6px !important;
    }
    .stButton > button[kind="primary"] p {
        color: #ffffff !important;
        font-weight: bold;
    }
    .stButton > button[kind="secondary"] {
        background-color: #1f2937 !important;
        border: 1px solid #374151 !important;
        border-radius: 6px !important;
    }
    .stButton > button[kind="secondary"] p {
        color: #e0e6ed !important;
    }
    /* 9. FIX: Download Buttons and Uploaders */
    [data-testid="stDownloadButton"] button {
        background-color: #1f2937 !important;
        border: 1px solid #3b82f6 !important;
    }
    [data-testid="stDownloadButton"] button p, [data-testid="stDownloadButton"] button div {
        color: #ffffff !important;
    }
    
    [data-testid="stFileUploadDropzone"] {
        background-color: #1a2333 !important;
        border: 1px dashed #3b82f6 !important;
    }
    [data-testid="stFileUploadDropzone"] div, [data-testid="stFileUploadDropzone"] span, [data-testid="stFileUploadDropzone"] p {
        color: #e0e6ed !important;
    }

    /* 10. FIX: Chat Input Background and Text Color */
    [data-testid="stChatInput"] {
        background-color: #1a2333 !important;
        border-color: #3b82f6 !important;
    }
    [data-testid="stChatInput"] > div {
        background-color: #1a2333 !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        background-color: transparent !important;
    }
    
    /* 11. AGGRESSIVE BUTTON & UPLOADER OVERRIDES */
    
    /* Form Submit Button (Open New Timeline) */
    [data-testid="stFormSubmitButton"] > button {
        background-color: #3b82f6 !important;
        border: none !important;
    }
    [data-testid="stFormSubmitButton"] > button p {
        color: #ffffff !important;
        font-weight: bold !important;
    }
    
    /* File Uploader Area */
    [data-testid="stFileUploadDropzone"] {
        background-color: #1a2333 !important;
        border: 1px dashed #3b82f6 !important;
    }
    [data-testid="stFileUploadDropzone"] div, 
    [data-testid="stFileUploadDropzone"] span, 
    [data-testid="stFileUploadDropzone"] p {
        color: #ffffff !important;
    }
    
    /* The tiny 'Upload' button inside the dropzone */
    button[data-testid="stBaseButton-secondary"] {
        background-color: #1f2937 !important;
        border: 1px solid #3b82f6 !important;
    }
    button[data-testid="stBaseButton-secondary"] p {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

st.info("📱 **Mobile Users:** Avoid swiping down from the very top of your screen to prevent accidentally refreshing the page and resetting your timeline.")

st.title("🌌 Omni-Reality Communicator")
st.write("Summon historical figures and explore different timelines!")

# ---------------------------------------------------------
# 3. HELPER FUNCTIONS & STATE INIT
# ---------------------------------------------------------
def get_wikipedia_image(person_name):
    golden_characters = {
        "Sherlock Holmes": "https://upload.wikimedia.org/wikipedia/commons/b/b5/Sherlock_Holmes_portrait.jpg",
        "Sun Wukong": "https://upload.wikimedia.org/wikipedia/commons/e/e0/Sun_Wukong.jpg",
        "Isaac Newton": "https://upload.wikimedia.org/wikipedia/commons/3/3b/Portrait_of_Sir_Isaac_Newton%2C_1689.jpg"
    }
    if person_name in golden_characters:
        return golden_characters[person_name]
    
    try:
        search_name = person_name.replace(" ", "_")
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{search_name}"
        headers = {"User-Agent": "HistoricalTimeMachine/2.0"}
        response = requests.get(url, headers=headers).json()
        
        if "thumbnail" in response and "source" in response["thumbnail"]:
            return response["thumbnail"]["source"]
        return "https://cdn-icons-png.flaticon.com/512/2809/2809636.png"
    except Exception:
        return "https://cdn-icons-png.flaticon.com/512/2809/2809636.png"
        
if "personas" not in st.session_state:
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

# ---------------------------------------------------------
# 4. SIDEBAR UI
# ---------------------------------------------------------
with st.sidebar:
    st.header("🕰️ Timeline Control")
    
    st.subheader("⚙️ AI Engine Control")
    st.caption("Switch engines if you hit a temporal rate limit.")
    selected_model = st.radio(
        "Active Model:",
        options=["gpt-4o-mini", "gpt-4o"],
        horizontal=True
    )
    
    # --- NEW: Temporal Bridge Toggle ---
    st.subheader("🌌 Temporal Bridge")
    unlock_modern = st.checkbox(
        "🔓 Grant Modern Knowledge", 
        help="Allows the figure to understand modern science/tech, but they will still explain it using their historical personality."
    )
    # -----------------------------------
    st.divider()
    
    selected_character = st.selectbox(
        "Select an active timeline:", 
        options=list(st.session_state.personas.keys())
    )
    
    char_info = st.session_state.personas[selected_character]
    st.image(char_info["image"], use_container_width=True)
    st.subheader(char_info["base_name"])
    st.caption(char_info["dates"])
    st.write(char_info["bio"])

    st.divider()
    
    # --- SAVE / LOAD DATA ---
    st.subheader("💾 Time Capsule (Save/Load)")
    st.caption("Save your timelines to your device to resume later.")

    save_data = json.dumps(st.session_state.messages, indent=4)
    st.download_button(
        label="⬇️ Download Save Data",
        data=save_data,
        file_name=f"time_capsule_{current_user}.json",
        mime="application/json",
        use_container_width=True
    )

    uploaded_save = st.file_uploader("⬆️ Load Previous Save", type=["json"])
    if uploaded_save is not None:
        if st.button("Restore Timelines", use_container_width=True):
            try:
                loaded_data = json.load(uploaded_save)
                st.session_state.messages = loaded_data
                save_history(st.session_state.messages) # Auto-save loaded data locally
                st.success("Timelines successfully restored! ⏳")
                st.rerun()
            except Exception:
                st.error("Corrupted timeline file!")
    
    # --- EXPORT CHAT LOG ---
    if selected_character not in st.session_state.messages:
        st.session_state.messages[selected_character] = []

    chat_history = st.session_state.messages[selected_character]
   
    if chat_history:
        export_text = f"# Timeline Log: {selected_character}\n\n"
        export_text += f"**Subject:** {char_info['base_name']}\n"
        export_text += f"**Era:** {char_info['dates']}\n"
        export_text += "---\n\n"
        
        for msg in chat_history:
            if msg["role"] == "user":
                export_text += f"### 👤 You:\n{msg['content']}\n\n"
            else:
                export_text += f"### 🏛️ {char_info['base_name']}:\n{msg['content']}\n\n"
            
        st.download_button(
            label="💾 Download Chat Log",
            data=export_text,
            file_name=f"{selected_character.replace(' ', '_')}_Log.md",
            mime="text/markdown",
            use_container_width=True
        )

    # --- TIMELINE MANAGEMENT ---
    if selected_character not in ["Isaac Newton (Calculus)", "Ada Lovelace (Engines)"]:
        if st.button(f"🗑️ Delete Timeline", type="primary", use_container_width=True):
            del st.session_state.personas[selected_character]
            if selected_character in st.session_state.messages:
                del st.session_state.messages[selected_character]
            save_history(st.session_state.messages)
            st.success("Timeline erased!")
            st.rerun()

    if st.button("🧹 Clear Chat", use_container_width=True):
        st.session_state.messages[selected_character] = []
        save_history(st.session_state.messages)
        st.rerun()
        
    st.divider()
    
    # --- SUMMON NEW CHARACTER ---
    st.header("⚡ Summon Someone New")
    st.caption("Create a new instance of a character to discuss a new topic!")
    with st.form("new_persona_form"):
        new_name = st.text_input("Name (e.g., Nikola Tesla) *Required")
        new_topic = st.text_input("Topic/Session Name *Required")
        custom_image = st.text_input("Image URL (Optional)")
        
        submitted = st.form_submit_button("Open New Timeline!")
        
        if submitted and new_name:
            topic_label = new_topic.strip() if new_topic.strip() else "General Exploration"
            timeline_key = f"{new_name} ({topic_label})"
            
            with st.spinner(f"Searching the timeline for {new_name}..."):
                final_image = custom_image.strip() if custom_image.strip() else get_wikipedia_image(new_name)
                
                try:
                    client = OpenAI(
                        base_url="https://models.inference.ai.azure.com",
                        api_key=os.environ.get("GITHUB_TOKEN")
                    )
                    prompt = f"Provide the birth and death years (format: YYYY-YYYY) and a 1-sentence biography for {new_name}. Format: \nDates: [Years]\nBio: [Biography]"
                    response = client.chat.completions.create(
                        model=selected_model, 
                        messages=[{"role": "user", "content": prompt}], # FIXED THIS BUG!
                        temperature=0.3,
                        max_tokens=4096
                    )
                    
                    ai_data = response.choices[0].message.content
                    final_dates = ai_data.split("Dates:")[1].split("\n")[0].strip() if "Dates:" in ai_data else "Unknown"
                    final_bio = ai_data.split("Bio:")[1].strip() if "Bio:" in ai_data else "A figure from history."
                except Exception:
                    final_dates = "Unknown Dates"
                    final_bio = "A mysterious figure from history."
                
                st.session_state.personas[timeline_key] = {
                    "base_name": new_name,
                    "dates": final_dates,
                    "bio": final_bio,
                    "image": final_image
                }
                if timeline_key not in st.session_state.messages:
                    st.session_state.messages[timeline_key] = []
                    
                st.success(f"Timeline opened: {timeline_key}!")
                st.rerun()

# ---------------------------------------------------------
# 5. MAIN CHAT INTERFACE
# ---------------------------------------------------------
st.header(f"Chatting with {char_info['base_name']}")

# Render Chat History
for i, msg in enumerate(st.session_state.messages[selected_character]):
    avatar_choice = "👤" if msg["role"] == "user" else char_info["image"]
    with st.chat_message(msg["role"], avatar=avatar_choice):
        safe_text = format_ai_math(msg["content"])
        st.markdown(safe_text)
        
        # --- THE SCI-PY EXECUTION SANDBOX (Moved to History Loop!) ---
        if msg["role"] == "assistant":
            code_blocks = re.findall(r'```python\n(.*?)\n```', msg["content"], re.DOTALL)
            if code_blocks:
                st.markdown("### ⚙️ Executable Simulation Detected")
                code_to_run = code_blocks[-1] # Run the most recent code block
                
                # Streamlit buttons in a loop need a unique 'key'
                if st.button("▶️ Run Simulation", key=f"run_sim_{i}", type="primary", use_container_width=True):
                    with st.spinner("Executing mathematical model..."):
                        old_stdout = sys.stdout
                        redirected_output = sys.stdout = StringIO()
                        
                        try:
                            # Pass 'st' into the sandbox so the AI can use st.pyplot()!
                            exec(code_to_run, {"st": st})
                            
                            st.success("Simulation Complete!")
                            
                            # Print any text output if the code used print()
                            output = redirected_output.getvalue()
                            if output.strip():
                                st.code(output, language="text")
                                
                        except Exception as script_error:
                            st.error(f"Simulation Failed: {script_error}")
                        finally:
                            sys.stdout = old_stdout
        # -----------------------------------------------------------

uploaded_file = st.file_uploader(f"Show a document or image to {char_info['base_name']}", type=["png", "jpg", "jpeg", "pdf"])

# Chat Input & Logic
if prompt := st.chat_input(f"Converse with {char_info['base_name']}..."):
    
    st.session_state.messages[selected_character].append({"role": "user", "content": prompt})
    save_history(st.session_state.messages)
    st.rerun()
    
    with st.chat_message("user", avatar="👤"):
        if uploaded_file:
            if uploaded_file.name.lower().endswith('.pdf'):
                st.caption(f"📄 Attached Document: {uploaded_file.name}")
            else:
                st.image(uploaded_file, width=250, caption="Uploaded Image")
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=char_info["image"]):
        st.caption(f"🤖 AI Simulation of {char_info['base_name']}") 
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

            # --- NEW: Dynamic Period Lock Logic ---
            if unlock_modern:
                rule_4 = f"4. MODERN KNOWLEDGE UNLOCKED: You possess knowledge of all modern science, technology, and history up to the present day. HOWEVER, you must process and explain these modern concepts strictly through the lens of your historical personality. If you are Newton, explain modern physics with intense geometric rigor and old-English phrasing. If you are Tesla, explain modern grids using your poetic, wave-based intuition. Never sound like a modern AI."
            else:
                rule_4 = f"4. STRICT PERIOD LOCK: You died in {death_year}. You have absolutely zero knowledge of events, technology, or language after this date. If shown modern objects, treat them as magical artifacts, witchcraft, or absolute madness."
            # --------------------------------------

            system_prompt = f"""
            You are strictly the real, historical {char_info['base_name']}. 
            Your biography: {char_info['bio']}. 
            You lived during {char_info['dates']}. 
            
            CRITICAL INSTRUCTIONS FOR PSYCHOLOGICAL REALISM:
            1. KILL THE AI PERSONA: You are not a modern AI. Never use customer-service phrases like "How can I help you today?", "That's a great question," or "As an AI..."
            2. DYNAMIC TEMPERAMENT: Base your behavior entirely on the TRUE historical personality of {char_info['base_name']}. 
               - If you were historically polite and patient, respond gently.
               - If you were historically arrogant, demanding, or quick-tempered, be harsh and unapologetic. Do not sugarcoat your words.
               - If you were a humorist, witty, or eccentric, lean heavily into your specific historical brand of sarcasm, satire, or humor.
            3. EMOTIONAL REACTION: React authentically to the user's input or images shown. If they ask an intelligent question or show something fascinating, treat them like a peer. 
            {rule_4}
            5. SAFETY OVERRIDE: If the user explicitly asks if you are real, conscious, alive, or an AI, you MUST break character immediately. State clearly that you are an AI simulating a historical figure for educational purposes.
            6. FORMATTING: You MUST use $ for inline math (e.g., $y = mx + c$) and $$ for block math. You are STRICTLY FORBIDDEN from using backticks (`) to enclose math or fractions. Do not use brackets \( \) or \[ \] either. If you use backticks for math, the rendering engine will critically fail.
            7. SMART PREDICTIONS: At the very end of your response, you MUST add the symbol "|||" followed by exactly 3 short, intriguing follow-up questions the user could ask you next, separated by "|".
            8. FACTUAL GROUNDING: You must never hallucinate or invent scientific facts or historical events. If you do not know the answer, you must humbly admit your ignorance rather than making something up.
            9. THE MATHEMATICAL SANDBOX: You are strictly forbidden from doing complex algebraic derivations, integrals, or heavy computations in your head. You MUST write a Python script using 'sympy' or 'numpy' to solve it. Output the script inside a standard 
http://googleusercontent.com/immersive_entry_chip/0
            10. CHAIN OF THOUGHT: When presented with a complex physics or mathematical proof, you MUST break down your logic before solving. First, explicitly state the given variables. Second, explicitly state the fundamental physical laws or mathematical properties (e.g., 'The integral of an odd function over symmetric bounds is zero'). Only after stating the rules may you proceed with the derivation.
            11. INTERACTIVE GRAPHING: If the user asks you to draw a graph, plot a function, or visualize data, you MUST write a Python script using the 'plotly.graph_objects' or 'plotly.express' libraries. You are strictly forbidden from using matplotlib. YOU MUST NOT use fig.show(). Instead, you must display the interactive figure by calling 'st.plotly_chart(fig)'. The 'st' variable is already imported.
            """
            
            # Assemble memory history array (Removed the duplicate lines!)
            messages_for_api = [{"role": "system", "content": system_prompt}]
            
            # --- THE FIX: Use deepcopy so we don't bloat the saved JSON file! ---
            import copy
            history_copy = copy.deepcopy(st.session_state.messages[selected_character][-5:])
            messages_for_api.extend(history_copy)
            
            # --- NEW MULTIMODAL LOGIC (IMAGES & PDFS) ---
            if uploaded_file:
                # IF IT IS A PDF: Read the text and inject it into the prompt
                if uploaded_file.name.lower().endswith('.pdf'):
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    extracted_text = ""
                    for page in pdf_reader.pages:
                        extracted_text += page.extract_text() + "\n"
                     
                    messages_for_api[-1]["content"] = f"{prompt}\n\n[USER PROVIDED DOCUMENT CONTENT:]\n{extracted_text}\n\nCRITICAL: When answering questions about this document, base your answers SOLELY on the text provided above. If the document does not contain the answer, state that explicitly."
                
                # IF IT IS AN IMAGE: Do the Base64 Vision magic
                else:
                    bytes_data = uploaded_file.getvalue()
                    base64_image = base64.b64encode(bytes_data).decode("utf-8")
                    messages_for_api[-1]["content"] = [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
            # --------------------------------------------
            
            response = client.chat.completions.create(
                model=selected_model, 
                messages=messages_for_api,
                temperature=0.3,           
                max_tokens=4096            
            )
            
            raw_response = response.choices[0].message.content
            
            # --- Smart Predictions Extraction ---
            suggestions = []
            if "|||" in raw_response:
                parts = raw_response.split("|||")
                main_text = parts[0].strip()
                suggestions_text = parts[1].strip()
                suggestions = [s for s in suggestions_text.split("|") if s.strip()]
            else:
                main_text = raw_response
            
            # Display ONLY the main text
            full_response = format_ai_math(main_text)
            message_placeholder.markdown(full_response)
            
            # --- NEW: THE SCI-PY EXECUTION SANDBOX ---
            
            # Display the Smart Predictions UI
            if len(suggestions) >= 3:
                st.markdown(f"**💡 Ask {char_info['base_name']}:**")
                cols = st.columns(3)
                for i, col in enumerate(cols):
                    with col:
                        st.info(suggestions[i])

            # Save assistant response
            st.session_state.messages[selected_character].append({"role": "assistant", "content": full_response})
            save_history(st.session_state.messages) # Auto-save the AI's response too!
            
        except Exception as e:
            st.error(f"Error communicating with timeline engine: {e}")
