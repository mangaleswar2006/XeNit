# XeNit
This is an AI integrated automation browser; it does work in a single command. This browser helps the users to make life and research easier.


## Project Moto
XeNit is an AI-integrated automation browser that executes complex workflows using a single command, making research and daily tasks effortless.


## Problem
The primary interface for the web—keyboard and mouse—excludes natural human interaction. Users cannot simply "talk" to the internet or delegate complex, multi-step tasks (e.g., "Find a lofi playlist and open WhatsApp"). Existing voice assistants are external overlays that lack deep context of the browser's DOM (Document Object Model), making them useless for web-specific tasks.


## Solution (XeNit AI)
XeNit AI implements a multimodal interaction layer directly over the web engine. With integrated Voice-to-Text and Text-to-Speech, users can converse with their browser. The underlying Agentic Architecture allows the AI to perceive the DOM, execute JavaScript events, and manipulate the browser state programmatically, effectively giving the AI "hands" to browse alongside the user. XeNit is a Python-based AI-powered browser that combines browser automation, ad-blocking, memory handling, and AI-driven command execution. Users can interact with the browser using intelligent commands while XeNit manages tabs, blocks ads, remembers context, and automates workflows in the background.
  

# XeNit AI Browser Project Report

This document provides a comprehensive and detailed breakdown of the XeNit AI Browser project. It covers the core problem, the architectural solution, technical implementation details, challenges faced, and the final capabilities.

---

## 1. Problem Statement
**The "Dumb" Browser Problem**  
Modern web browsers (Chrome, Edge, Firefox) have become stagnant. They act as passive rendering engines—displaying what is sent to them but understanding nothing. 
-   **User Overload**: Users drown in tab clutter ("Tab Fatigue").
-   **Context Switching**: Users constantly jump between the browser and other apps (Notes, Calendar, Chatbots).
-   **Repetitive Tasks**: Filling out forms, clicking through ads, and managing logins are manual, repetitive burdens.
-   **Privacy Gaps**: Tracking and intrusive ads are the norm, often requiring third-party extensions to block.

**The Solution: XeNit AI (The "Agentic" Browser)**  
XeNit AI redefines the browser as an **Active Agent**. It is not just a window to the web; it is an intelligent co-pilot that lives _inside_ the browser.
-   **Perception**: It "sees" the web page (URL, Title, Content).
-   **Action**: It can click buttons, type text, and navigate on your behalf.
-   **Memory**: It remembers your preferences and identity to autofill forms.
-   **Voice**: You can simply *speak* to it, "Go to YouTube and play lofi beats," and it executes the complex sequence of actions.

---

## 2. Architecture Diagram



<img width="1328" height="677" alt="Screenshot 2026-02-01 031954" src="https://github.com/user-attachments/assets/25a481f5-994c-40a4-9de4-c6bba619aa31" />









## 3. Tech Stack & Rationale

| Component | Technology | Reasoning |
| :--- | :--- | :--- |
| **Language** | **Python 3.10+** | Chosen for its vast ecosystem of AI/ML libraries and rapid development capabilities. |
| **GUI Framework** | **PyQt6** | Provides native OS integration and access to the powerful chromium-based QtWebEngine. |
| **Rendering Engine** | **QtWebEngine** | Efficient, standards-compliant web rendering (same engine as Chrome). |
| **LLM Inference** | **NVIDIA NIM** | Access to `Llama-3.1-405b-instruct`, a model with high reasoning capability for complex tasks. |
| **Voice STT** | **SpeechRecognition** | Robust offline/online speech-to-text conversion. |
| **Voice TTS** | **pyttsx3** | Low-latency local text-to-speech synthesis. |
| **Data Storage** | **JSON** | Zero-dependency, human-readable storage for user memory and preferences. |

---

## 4. Setup Instructions

To reproduce the development environment, follow these steps:

### Prerequisites
-   **OS**: Windows 10/11 (Preferred), macOS, or Linux.
-   **Python**: Version 3.10 or higher.
-   **Hardware**: Microphone and Speakers.

### Step-by-Step Installation
1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-repo/XeNit-AI.git
    cd "XeNit AI"
    ```

2.  **Create Virtual Environment** (Crucial for dependency isolation):
    ```bash
    python -m venv .venv
    ```

3.  **Activate Environment**:
    -   **Windows**: `.\.venv\Scripts\Activate.ps1`
    -   **Mac/Linux**: `source .venv/bin/activate`

4.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *(Dependencies include: `PyQt6`, `PyQt6-WebEngine`, `openai`, `SpeechRecognition`, `pyttsx3`, `pyaudio`)*

5.  **Configure API Keys**:
    -   Open `browser/ai_agent.py`.
    -   Set `self.api_key = "YOUR_NVIDIA_OR_OPENAI_KEY"`.

6.  **Run the Application**:
    ```bash
    python main.py
    ```

---

## 5. Detailed Implementation & Source Code

This section highlights the critical logic that makes the browser "Smart".

### A. The Agent Controller (`browser/window.py`)
This class bridges the gap between the LLM's text output and the Browser's execution.

```python
class AgentController:
    # ...
    def click_element(self, text):
        # Injects JavaScript to find and click an element by text
        js_code = f"""
        (function() {{
            const text = "{text}".toLowerCase();
            const elements = document.querySelectorAll('button, a, input[type="submit"]');
            for (let el of elements) {{
                if (el.innerText.toLowerCase().includes(text)) {{
                    el.click();
                    return;
                }}
            }}
        }})();
        """
        self.window.tabs.currentWidget().page().runJavaScript(js_code)
```

### B. Prompt Engineering Strategy (`browser/ai_agent.py`)
We intentionally "leak" system internals to the LLM via the System Prompt, teaching it a specific `[[ACTION]]` syntax.

**System Prompt Template:**
> "You are XeNit, a browser agent. 
> To act, output tags at the END of your response:
> - `[[OPEN: url]]` -> Navigates to a URL.
> - `[[CLICK: text]]` -> Clicks a button.
> - `[[AUTOFILL: json]]` -> Fills forms using User Profile data.
> 
> Context: User is on '{current_page_title}'.
> User Profile: {json_dump_of_user_data}"

### C. The "Dot Trick" AdBlocker (`browser/window.py`)
A clever, lightweight technique to bypass YouTube ads by forcing a hostname deviation.
```python
if "youtube.com" in host and not host.endswith("."):
    # Appending a dot often breaks ad-serving domain matching
    new_host = host.replace("youtube.com", "youtube.com.") 
    qurl.setHost(new_host)
```

---

## 6. User Flow Examples

### Scenario 1: Voice Navigation
1.  **User acts**: Clicks Mic and says "Play lofi hip hop on YouTube."
2.  **STT Layer**: Converts audio to text "Play lofi hip hop on YouTube".
3.  **LLM Layer**: Receives text, decides to search. Outputs: `Sure! [[MUSIC: lofi hip hop]]`.
4.  **Controller Layer**: 
    -   Parses `[[MUSIC]]`.
    -   Navigates to `youtube.com/results?search_query=lofi+hip+hop`.
    -   Injects JS to find the first video thumbnail and **simulates a click**.
5.  **Result**: Video starts playing automatically.

### Scenario 2: Smart Form Filling
1.  **User acts**: Opens a job application and says "Fill this for me."
2.  **LLM Layer**:
    -   Reads page context (knows it's a form).
    -   Reads User Profile from Memory (`{"Name": "Lucky", "Email": "..."}`).
    -   Outputs: `Filling details... [[AUTOFILL: {"Name": "Lucky", "Email": ...}]]`.
3.  **Controller Layer**: Injects JS to fuzzy-match input fields (finding "Full Name", "E-mail Address") and inserts the values.

---

## 7. Challenges & Future Improvements

### Challenges
-   **Context Limit**: The LLM cannot read the *entire* HTML of complex pages without exceeding token limits. We currently truncate text.
-   **DOM Complexity**: `[[CLICK: text]]` is fragile. Text on buttons often differs from the visible label due to icons or CSS (e.g., `aria-label`).
-   **Audio Config**: `PyAudio` is notoriously difficult to install on Windows due to binary wheel mismatches (solved via `pipwin`).

### Future Roadmap
-   [ ] **Vision Capabilities**: Send screenshots of the webpage to the LLM (using GPT-4o) for true "visual" understanding.
-   [ ] **Extension Support**: Add support for Chrome Extensions (`.crx` files).
-   [ ] **Cloud Sync**: Sync memory/history across devices using Firebase/Supabase.

---

## 8. Final Output

The **XeNit AI Browser** stands as a functional prototype of the future of browsing. 
-   It **Looks** different: Neon, dark, glassmorphism UI.
-   It **Feels** different: You talk to it, and it does the work.
-   It **Works** explicitly: It blocks ads and remembers you, respecting your time and attention.


## Build & Reproducibility Instructions

# XeNit AI Browser - Build & Reproducibility Instructions

## Requirements
- PyQt6
- PyQt6-WebEngine
- openai
- SpeechRecognition
- pyttsx3
- pyaudio
- pypiwin32

This document outlines the mandatory steps to reproduce the build and run the XeNit AI Browser environment.

## 1. System Requirements
- **OS:** Windows 10/11 (Primary Support), macOS, or Linux.
- **Python:** Python 3.10, 3.11, or 3.12.
- **Hardware:** Microphone and Speakers (for Voice features), Internet Connection.

## 2. Environment Setup (Clean Install)

It is highly recommended to use a fresh virtual environment to avoid conflicts.

### Step 2.1: Clone/Extract Project
Ensure you are in the root directory of the project:
```powershell
cd "path\to\XeNit AI"
```

### Step 2.2: Create Virtual Global Environment
```powershell
python -m venv .venv
```

### Step 2.3: Activate Environment
- **Windows (PowerShell):**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- **Windows (CMD):**
  ```cmd
  .venv\Scripts\activate.bat
  ```
- **Mac/Linux:**
  ```bash
  source .venv/bin/activate
  ```

## 3. Dependency Installation

Install the required Python packages using the generated requirements file.

### Option A: Using requirements.txt (Recommended)
```powershell
pip install -r requirements.txt
```

### Option B: Manual Installation (If option A fails)
```powershell
pip install PyQt6 PyQt6-WebEngine openai SpeechRecognition pyttsx3 pyaudio
```

**Troubleshooting Audio on Windows:**
If `pyaudio` fails to install with a "Wheel" error:
1.  `pip install pipwin`
2.  `pipwin install pyaudio`
3.  Or download the .whl manually from [Christoph Gohlke's libs](https://www.lfd.uci.edu/~gohlke/pythonlibs/).

## 4. Configuration (API Keys)
The AI features require an LLM provider.
1.  Open `browser/ai_agent.py`.
2.  Locate the OpenAI Client initialization.
3.  Ensure your **NVIDIA NIM** or **OpenAI** API key is set in the `api_key` field or as an environment variable `NVIDIA_API_KEY`.
    *   *Default configuration uses a placeholder or local variable which must be updated for the AI to reply.*

## 5. Execution
Run the main application entry point:
```powershell
python main.py
```

## 6. Verification Checklist
- [ ] Browser window opens with the "XeNit" Neon UI.
- [ ] Sidebar can be toggled via the Menu or specific buttons.
- [ ] Microphone icon appears in the AI Sidebar.
- [ ] Pages load correctly (e.g., YouTube, Google).
- [ ] AdBlocker prints "AdBlock Logic Fully Armed" in the console.

## 7. Folder Structure
```
XeNit AI/
├── browser/               # Core Source Code
│   ├── adblock.py         # AdBlock Engine
│   ├── ai_agent.py        # LLM Integration
│   ├── sidebar.py         # Chat & Voice UI
│   ├── window.py          # Main GUI & Browser Engine
│   └── voice.py           # Speech Processing
├── main.py                # Entry Point
├── requirements.txt       # Dependency List
├── xenit_memory.json      # User Persistent Data
└── README.md              # This file
```
