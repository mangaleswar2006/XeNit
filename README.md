# XeNit
This is an AI integrated automation browser; it does work in a single command. This browser helps the users to make life and research easier.


## Project Moto
XeNit is an AI-integrated automation browser that executes complex workflows using a single command, making research and daily tasks effortless.


## Problem
The primary interface for the web—keyboard and mouse—excludes natural human interaction. Users cannot simply "talk" to the internet or delegate complex, multi-step tasks (e.g., "Find a lofi playlist and open WhatsApp"). Existing voice assistants are external overlays that lack deep context of the browser's DOM (Document Object Model), making them useless for web-specific tasks.


## Solution (XeNit AI)
XeNit AI implements a multimodal interaction layer directly over the web engine. With integrated Voice-to-Text and Text-to-Speech, users can converse with their browser. The underlying Agentic Architecture allows the AI to perceive the DOM, execute JavaScript events, and manipulate the browser state programmatically, effectively giving the AI "hands" to browse alongside the user. XeNit is a Python-based AI-powered browser that combines browser automation, ad-blocking, memory handling, and AI-driven command execution. Users can interact with the browser using intelligent commands while XeNit manages tabs, blocks ads, remembers context, and automates workflows in the background.
  

## Project Structure

XeNit AI/
│
├── browser/
│ ├── adblock.py # Ad request interception and blocking
│ ├── adblock_list.txt # Blocked domain list
│ ├── ai_agent.py # AI command processing logic
│ ├── data_manager.py # Data and state handling
│ ├── dialogs.py # Dialog and prompt UI handling
│ ├── engine.py # Core browser engine
│ ├── memory.py # Persistent memory management
│ ├── menu.py # Application menu logic
│ ├── pages.py # Page navigation handling
│ ├── sidebar.py # Sidebar UI
│ ├── styles.py # UI styling
│ ├── tabs.py # Tab management
│ ├── voice.py # Voice interaction support
│ ├── window.py # Main browser window
│ └── init.py
│
├── main.py # Application entry point
├── verify_install.py # Environment verification
├── requirements.txt # Dependencies
├── xenix_memory.json # Persistent browser memory
└── README.md


## Tech Stack
  The project is built using a modern Python ecosystem, leveraging the Chromium engine for web rendering and Qt for the high-performance UI.
  
  Core Language: Python 3.10+
  GUI Framework: PyQt6 (Python bindings for Qt 6)
  Browser Engine: QtWebEngine (Chromium-based rendering engine)
  Audio & Voice Processing:
          - SpeechRecognition (Unified wrapper for Speech APIs)
          - pyttsx3 (Offline Text-to-Speech synthesis)
          - PyAudio (Low-level microphone I/O)
  Data & Networking:
          - urllib (Network requests for blocklists)
          - json (Memory and persistent storage)


## Setup Instructions
  Prerequisites
  - Python 3.10 or higher installed.
  - A working microphone/speaker for voice features.
  
  **Installation Steps**

  Clone the Repository :-
  git clone <repository_url>
  cd XeNit_AI
  
  Create a Virtual Environment (Recommended) :-
  python -m venv .venv
  # Windows:
  .venv\Scripts\activate
  # Mac/Linux:
  source .venv/bin/activate
  
  Install Dependencies :-
  pip install PyQt6 PyQt6-WebEngine SpeechRecognition pyttsx3 pyaudio openai
  Note: If pyaudio fails on Windows, you may need to install pipwin then pipwin install pyaudio.
  
  Run the Application :-
  python main.py


## AI Tools Used
  XeNit AI integrates multiple AI modalities to create a cohesive agentic experience:
  
  Large Language Model (The "Brain"):-
  Model: meta/llama-3.1-405b-instruct
  Provider: NVIDIA NIM (NVIDIA Inference Microservices) via OpenAI-compatible API.
  Role: Reasoning, natural language understanding, decision making, HTML parsing, and generating browser control commands.
  
  Speech-to-Text (The "Ears"):-
  Tool: Google Speech Recognition API (via SpeechRecognition library).
  Role: Converting user voice commands into text for the LLM to process.
  
  Text-to-Speech (The "Voice"):-
  Tool: pyttsx3 (utilizing Microsoft SAPI5 on Windows).
  Role: Vocalizing the AI's responses back to the user for a hands-free experience.
  
  Contextual Agent (The "Hands"):-
  Technology: Custom Python-JavaScript Bridge.
  Role: Injects dynamic JavaScript into the DOM to "see" page content, click buttons, fill forms, and bypass anti-bots (like Captcha tick-boxes) based on the LLM's instructions.


## Prompt Strategy Summary
  Our AI Agent utilizes a "Context-Aware Action-Oriented" prompting strategy. We do not simply ask the LLM to "chat"; we engineer the prompt to be a control interface.
  
  - Role Definition: The System Prompt explicitly defines the AI as XeNit AI, a browser controller, not a general assistant.
  - Dynamic Context Injection: Before every user query, the Python backend scrapes the current browser state (Current URL, Page Title, and Truncated Page Text) and injects it into the prompt. This gives the AI "eyes" to see the page.
  - Structured Command Output: We enforce a strict "Action Grammar". The AI is instructed to output commands in a specific format (e.g., [[OPEN: google.com]], [[CLICK: Submit]], [[AUTOFILL: {...}]]).
  - Benefit: This separates the "Thought" (natural language) from the "Action" (code execution), preventing parsing errors.
  - Memory Retrieval: The MemoryManager retrieves relevant facts and user profile data (e.g., Name, Email) and injects them into the prompt, enabling the AI to fill forms without asking redundant questions.


## Final Output / Deliverable
  The final product is a fully functional, standalone web browser named "XeNit AI".

**Key Features:**

  - Futuristic UI: Neon-themed aesthetic with floating toolbars and smooth animations.
  - Zero-Ad Experience: Built-in aggressive AdBlock that mitigates 75,000+ trackers and YouTube ads.
  
  **Multimodal AI Agent: A sidebar assistant that can:**
  - See: Read and summarize the current webpage.
  - Do: Fill forms, click buttons, and navigate tabs autonomously.
  - Speak: Listen to voice commands and talk back to the user.
  - Performance: Optimized with hardware acceleration for smooth 60fps scrolling and rendering
  - AI-powered command agent
  - Built-in ad blocker with large domain list
  - Tab and page management
  - Persistent memory using JSON
  - Modular browser architecture
  - Voice and dialog interaction support
  - Automation-first browser control
