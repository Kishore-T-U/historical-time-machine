# historical-time-machine
**The Historical Time Machine**

Youtube Video link: https://youtu.be/D9iE_Fa5oHc

The Historical Time Machine is an immersive, AI-powered “multi-reality” interface for **students and teachers, writers and researchers, and history/mythology/fiction enthusiasts** who want to move beyond passive reading into active, high-context dialogue. Traditional learning and research often rely on static textbooks and wiki pages, which makes it hard to ask follow-up questions, explore “why” behind conclusions, or stay engaged. Meanwhile, generic chatbots can be inconsistent: they may break character, blur contexts across topics, and present complex material (especially math/physics) in ways that aren’t easy to learn from.

To address this, The Historical Time Machine lets users **summon a persona**—a historical scientist, a mythological deity, or a fictional character—and converse inside that persona’s isolated “timeline.” Instead of using hardcoded character sheets, the system uses a **Dynamic Summoning System** (powered by GitHub Models and the gpt-4o API) that constructs a grounded context at runtime. The backend queries the **Wikipedia REST API** to fetch verified biographical summaries and portrait imagery, helping anchor each conversation in recognizable facts and visuals.

The experience is designed to be both immersive and useful:
- **Strict persona confinement:** the AI is prompted to stay within the character’s era and lore (e.g., a 17th‑century scientist resists modern framing; a deity speaks within their canon).
- **Educational math formatting:** for scientific and technical discussions (e.g., Newton), equations and explanations are rendered in clear, readable, “textbook-style” formatting to make abstract ideas easier to understand.
- **Isolated multiverse memory:** multiple parallel timelines can run without cross-contamination, so users can switch between personas while keeping each conversation consistent.
- **Research/learning preservation:** users can **download chat logs** as clean, formatted text files—useful for study notes, classroom artifacts, and writing/research workflows.

The demo showcases the full capability set: summoning and interacting with multiple personas (including historical, fictional, and mythological), a math concept explained by Newton with proper formatting, and exporting the conversation via the download utility.

Built with Python, Streamlit, GitHub Models (OpenAI gpt-4o), and the Wikipedia REST API. Developed by Harshavardhan M, M Tejash Reddy, and Kishore T U.
