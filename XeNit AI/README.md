# XeNit AI Browser

**XeNit AI** is a next-generation web browser designed for the modern era, blending a futuristic "Cyberpunk/Neon" aesthetic with advanced AI capabilities. Built with Python and PyQt6, XeNit integrates a powerful Voice-Activated AI Assistant (powered by NVIDIA NIM/OpenAI) directly into your browsing experience.

![XeNit AI Browser](https://via.placeholder.com/800x400?text=XeNit+AI+Browser+UI)

## 🚀 Key Features

### 🧠 Integrated AI Assistant
- **Voice-Activated**: Conversational AI that listens and speaks back.
- **Context Aware**: capable of understanding your current browsing context.
- **DeepMind/NVIDIA Powered**: Leverages state-of-the-art LLMs for accurate and helpful responses.

### 🛡️ Advanced Privacy & Security
- **AdBlocker**: Built-in, aggressive ad-blocking logic to keep your browsing clean and fast.
- **Secure Architecture**: User-Agent spoofing and strict security protocols to ensure compatibility with modern secure sites (Gmail, YouTube).

### 🎨 Futuristic UI/UX
- **Neon Design**: A visually stunning dark mode with neon accents and glassmorphism effects.
- **Smooth Animations**: Fluid transitions and interactive elements.
- **Customizable**: Adaptable interface to match your style.

## 🛠️ System Requirements

- **OS**: Windows 10/11 (Preferred), macOS, or Linux.
- **Python**: Python 3.10+.
- **Hardware**: Microphone and Speakers (required for full voice features).

## 📥 Installation

Follow these steps to set up the XeNit AI Browser development environment.

### 1. Clone the Repository
```powershell
cd "path\to\XeNit AI"
```

### 2. Create a Virtual Environment
It is highly recommended to use a virtual environment to manage dependencies.
```powershell
python -m venv .venv
```

### 3. Activate the Environment
- **Windows (PowerShell):**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- **Mac/Linux:**
  ```bash
  source .venv/bin/activate
  ```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```
*Note: If you encounter issues with `pyaudio` on Windows, you may need to install `pipwin` first and use it to install `pyaudio`.*

## ⚙️ Configuration

### API Keys
To enable the AI features, you must configure your API keys.
1. Open `browser/ai_agent.py`.
2. Locate the API Key configuration section.
3. specific your **NVIDIA NIM** or **OpenAI** API key. You can set this as an environment variable `NVIDIA_API_KEY` for better security.

### User Memory
The browser stores user preferences and history in `xenit_memory.json`.
- **Profile**: Stores user details (Name, Email, etc.) for form filling.
- **History**: Smart history tracking for better AI context.

## 📖 Usage Manual

### Navigation
- **Address Bar**: Type URL or search query. Press Enter.
- **Tabs**: Click `+` to add a new tab. click `x` on a tab to close it.
- **Back/Forward**: Standard navigation controls.

### AI Assistant
- **Open Sidebar**: Click the AI icon in the toolbar.
- **Voice Mode**: Click the mic icon to speak to the AI.

### Keyboard Shortcuts
- `Ctrl+T`: New Tab
- `Ctrl+W`: Close Tab
- `Ctrl+R`: Reload
- `F11`: Toggle Fullscreen

## 🔧 Troubleshooting

### Audio Issues
- **Microphone not detected**: Ensure your default input device is set correctly in Windows Sound settings.
- **"Wheel" error during install**: Try installing `pyaudio` using `pipwin install pyaudio`.

### Renderer Issues
- **Black Screen**: Ensure your graphics drivers are up to date. The browser uses OpenGL for rendering.

## 📂 Project Structure

```
XeNit AI/
├── browser/               # Core Application Code
│   ├── adblock.py         # AdBlock Logic
│   ├── ai_agent.py        # AI Integration
│   ├── sidebar.py         # AI Sidebar UI
│   ├── tabs.py            # Tab Management
│   ├── window.py          # Main Window & Browser Engine
│   └── ...
├── main.py                # Application Entry Point
├── requirements.txt       # Python Dependencies
├── xenit_memory.json      # Persistent User Data
└── README.md              # Project Documentation
```

---
**XeNit AI** - Redefining the way you browse.
