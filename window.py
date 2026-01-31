from PyQt6.QtWidgets import (QMainWindow, QToolBar, QLineEdit, QVBoxLayout, 
                             QWidget, QHBoxLayout, QLabel, QMenu, QSizePolicy, QPushButton,
                             QSplitter, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QSize, QUrl
from PyQt6.QtGui import QIcon, QAction, QColor
import urllib.parse

from browser.tabs import TabManager
from browser.menu import CustomMenu
from browser.data_manager import DataManager
from browser.sidebar import Sidebar
from browser.dialogs import (HistoryDialog, BookmarksDialog, DownloadsDialog, 
                             SettingsDialog, HelpDialog, SignInDialog)
from browser.memory import MemoryManager
from browser.ai_agent import AIAgent
from browser.voice import VoiceManager

from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # PERFORMANCE: Enable Smooth Scrolling & GPU Acceleration
        settings = QWebEngineProfile.defaultProfile().settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        
        self.setWindowTitle("XeNit Browser")
        self.resize(1200, 800)
        
        self.data_manager = DataManager()
        self.voice_manager = VoiceManager()
        
        # Initialize AI Agent System
        self.memory_manager = MemoryManager()
        self.agent = AIAgent(self.memory_manager)
        
        # setup Controller for Agent Actions
        class AgentController:
            def __init__(self, window):
                self.window = window
            
            def open_url(self, url):
                # Ensure URL has scheme
                if "://" not in url:
                    url = "https://" + url
                return self.window.add_new_tab(QUrl(url), "Loading...")
                
            def play_music(self, query):
                # Search on YouTube
                search_url = f"https://www.youtube.com/results?search_query={query}"
                browser = self.open_url(search_url)
                
                def auto_play():
                    # Robust JS: Polls for the video title link for up to 10 seconds
                    js_code = """
                    (function() {
                        let attempts = 0;
                        const maxAttempts = 40; // 20 seconds (40 * 500ms)
                        
                        const interval = setInterval(function() {
                            attempts++;
                            // Selector for the first video title in search results
                            // Try multiple valid selectors
                            let video = document.querySelector('ytd-video-renderer #video-title') || 
                                        document.querySelector('a#video-title') ||
                                        document.querySelector('ytd-video-renderer a#thumbnail');
                            
                            if (video) {
                                console.log("XeNit AI: Found video, clicking...");
                                video.click();
                                // Fallback: If click is intercepted, force navigation
                                // Use a small timeout to let the click try first
                                setTimeout(() => {
                                    if(document.location.href.includes('results')) {
                                        window.location.href = video.href;
                                    }
                                }, 500);
                                clearInterval(interval);
                            } else if (attempts >= maxAttempts) {
                                console.log("XeNit AI: Could not find video to auto-play.");
                                clearInterval(interval);
                            }
                        }, 500); 
                    })();
                    """
                    browser.page().runJavaScript(js_code)
                    # Disconnect to avoid re-running if user navigates elsewhere in this tab
                    try:
                        browser.loadFinished.disconnect(auto_play)
                    except:
                        pass
                
                browser.loadFinished.connect(auto_play)
                
            def open_whatsapp(self, param=None):
                url = "https://web.whatsapp.com"
                phone = None
                message = param
                
                # Check if param contains number and message separated by |
                if param and "|" in param:
                    parts = param.split("|", 1)
                    phone = parts[0].strip()
                    message = parts[1].strip()
                
                if message:
                    encoded_msg = urllib.parse.quote(message)
                    if phone:
                         # Direct Message Link
                         url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_msg}"
                    else:
                         # Select Contact Link
                         url = f"https://web.whatsapp.com/send?text={encoded_msg}"
                         
                browser = self.open_url(url)
                
                # Auto-Click Send Button
                def auto_send():
                    js_code = """
                    (function() {
                        let attempts = 0;
                        const maxAttempts = 60; // 30 seconds
                        
                        const interval = setInterval(function() {
                            attempts++;
                            
                            // 1. Try finding the Send Button
                            const sendBtnInfo = document.querySelector('span[data-icon="send"]');
                            const sendBtnAria = document.querySelector('button[aria-label="Send"]');
                            const mainBtn = (sendBtnInfo ? sendBtnInfo.closest('button') : null) || sendBtnAria;
                            
                            if (mainBtn) {
                                console.log("XeNit AI: Found Send button, clicking...");
                                mainBtn.click();
                                clearInterval(interval);
                                return;
                            }
                            
                            // 2. Fallback: Press 'Enter' if text box is focused (WhatsApp usually focuses it)
                            // We wait a bit (e.g. 10 attempts / 5s) before trying this to let the UI load
                            if (attempts > 10 && attempts % 5 === 0) {
                                const active = document.activeElement;
                                if (active && active.innerText.length > 0) {
                                    console.log("XeNit AI: Simulating Enter Key...");
                                    const event = new KeyboardEvent('keydown', {
                                        key: 'Enter',
                                        code: 'Enter',
                                        which: 13,
                                        keyCode: 13,
                                        bubbles: true
                                    });
                                    active.dispatchEvent(event);
                                    // We don't clear interval yet, in case it didn't work
                                }
                            }

                            if (attempts >= maxAttempts) {
                                console.log("XeNit AI: Could not find Send button.");
                                clearInterval(interval);
                            }
                        }, 500);
                    })();
                    """
                    browser.page().runJavaScript(js_code)
                    try:
                        browser.loadFinished.disconnect(auto_send)
                    except:
                        pass
                
                if message and phone:
                     # Only auto-send if we have a target
                     browser.loadFinished.connect(auto_send)
                
            def auto_fill(self, json_str):
                # We expect a JSON string like {"Name": "Lucky"}
                # To be safe against sloppy LLM output, we pass it directly to JS to parse if possible,
                # or we try to clean it here.
                # Let's wrap it in a JS function that handles the parsing.
                
                js_code = f"""
                (function() {{
                    try {{
                        const data = {json_str}; 
                        console.log("XeNit AutoFill Data:", data);
                        
                        for (const [key, value] of Object.entries(data)) {{
                            // Break key into searchable terms (e.g. "First Name" -> ["first", "name"])
                            const searchTerms = key.toLowerCase().split(/\s+|_|-/).filter(t => t.length > 0);
                            
                            let inputs = Array.from(document.querySelectorAll('input:not([type="hidden"]), textarea, select'));
                            let bestMatch = null;
                            let maxScore = 0;
                            
                            for (let input of inputs) {{
                                let score = 0;
                                // Combine all potential identifiers
                                const content = (input.placeholder || input.name || input.id || "").toLowerCase();
                                const labelText = input.labels?.[0]?.innerText.toLowerCase() || "";
                                const ariaLabel = (input.getAttribute('aria-label') || "").toLowerCase();
                                const totalText = content + " " + labelText + " " + ariaLabel;
                                
                                // Scoring: Match count of terms
                                for(let term of searchTerms) {{
                                    if(totalText.includes(term)) score++;
                                }}
                                
                                // Bonus for exact match or starting with main term
                                if(totalText.includes(key.toLowerCase())) score += 2;
                                if(searchTerms.length > 0 && totalText.includes(searchTerms[0])) score += 0.5;

                                // Penalties for mismatch types? (e.g. email filling a phone field)
                                // Basic type checking
                                if (key.toLowerCase().includes("email") && input.type === "email") score += 2;
                                if (key.toLowerCase().includes("phone") && (input.type === "tel" || input.name.includes("phone"))) score += 2;
                                
                                if (score > maxScore) {{
                                    maxScore = score;
                                    bestMatch = input;
                                }}
                            }}
                            
                            if (bestMatch && maxScore > 0) {{
                                bestMatch.scrollIntoView({{behavior: "smooth", block: "center"}});
                                bestMatch.focus();
                                bestMatch.value = value;
                                bestMatch.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                bestMatch.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                bestMatch.blur();
                                console.log("XeNit Filled: " + key + " -> " + (bestMatch.name || bestMatch.id));
                            }} else {{
                                console.log("XeNit: Could not match field for " + key);
                            }}
                        }}
                    }} catch (e) {{
                        console.error("AutoFill Error:", e);
                    }}
                }})();
                """
                self.window.tabs.currentWidget().page().runJavaScript(js_code)

            def click_element(self, text):
                # Clicks a button or link containing the text
                js_code = f"""
                (function() {{
                    const text = "{text}".toLowerCase();
                    const elements = document.querySelectorAll('button, a, input[type="submit"], span');
                    
                    for (let el of elements) {{
                        if (el.innerText.toLowerCase().includes(text) || (el.value && el.value.toLowerCase().includes(text))) {{
                            console.log("XeNit Clicking:", el);
                            el.click();
                            return;
                        }}
                    }}
                    console.log("XeNit: No element found for " + text);
                }})();
                """
                self.window.tabs.currentWidget().page().runJavaScript(js_code)
                
            def close_specific_tabs(self, indices_str):
                # indices_str might be "[1, 3, 5]" string or list
                try:
                    import json
                    if isinstance(indices_str, str):
                        indices = json.loads(indices_str)
                    else:
                        indices = indices_str
                    
                    # Sort descending to avoid index shift issues
                    indices.sort(reverse=True)
                    for i in indices:
                         # Safety check: Don't close current tab if possible?
                         # Actually Agent can close content in background.
                         if i < self.window.tabs.count():
                             # Retrieve widget to explicitly delete it (release memory)
                             widget = self.window.tabs.widget(i)
                             self.window.tabs.removeTab(i)
                             if widget:
                                 widget.deleteLater()
                                 
                    print(f"XeNit Agent: Closed {len(indices)} tabs.")
                except Exception as e:
                    print(f"XeNit: Error closing tabs {e}")
                
        self.agent.set_controller(AgentController(self))
        
        # Central Widget & Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Toolbar
        self.create_toolbar()
        
        # Splitter for Sidebar + Tabs
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter)
        
        # Sidebar (Initially Hidden)
        self.sidebar = Sidebar(self.data_manager, self, self.agent, self.voice_manager)
        self.sidebar.hide()
        self.splitter.addWidget(self.sidebar)
        
        # Tabs
        self.tabs = TabManager(self)
        self.splitter.addWidget(self.tabs)
        
        # Tab Health Monitor
        self.cleanup_proposal = None
        self.last_cleanup_prompt = 0
        from PyQt6.QtCore import QTimer
        self.tab_health_timer = QTimer()
        self.tab_health_timer.timeout.connect(self.monitor_tabs)
        self.tab_health_timer.start(10000) # Check every 10s
        
        # Set Splitter Factors to favor Web Content
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setCollapsible(0, False) # Can't fully collapse sidebar via dragging, button does it

        # Load initial tab
        self.add_new_tab(QUrl("xenit://newtab"), "New Tab")
        
        # Apply Styles for URL Bar uniqueness, reusing pill aesthetic
        self.url_bar.setStyleSheet("""
            QLineEdit {
                background-color: #18181b;
                border: 1px solid #27272a;
                border-radius: 18px; /* Pill */
                padding: 10px 20px;
                color: #FAFAFA;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #00F0FF;
                background-color: #09090b;
            }
        """)

    def monitor_tabs(self):
        import time
        if time.time() - self.last_cleanup_prompt < 300: # Don't bug more than once every 5 mins
            return
            
        count = self.tabs.count()
        if count < 4: return # Lower threshold for easier testing

        # Simple Clustering
        groups = {}
        for i in range(count):
            title = self.tabs.tabText(i)
            # Use main words > 3 chars
            words = [w.lower() for w in title.split() if len(w) > 3]
            for w in words:
                if w not in groups: groups[w] = []
                groups[w].append(i)
        
        # Check for heavy clusters
        for topic, indices in groups.items():
            if len(indices) >= 4: # Overload Threshold
                # Found overload
                titles = [self.tabs.tabText(i) for i in indices]
                self.cleanup_proposal = {"topic": topic, "indices": indices, "titles": titles}
                self.last_cleanup_prompt = time.time()
                
                msg = f"I noticed you have {len(indices)} tabs about '{topic}'. Want me to summarize them and close the extras? (Reply 'Yes' or 'Do it')"
                
                # Auto-open sidebar if hidden so user sees the help
                if not self.sidebar.isVisible():
                    self.sidebar.show()
                # Ensure AI tab is shown
                self.sidebar.show_ai_tab()
                
                self.sidebar.add_ai_message(msg)
                break

    def create_toolbar(self):
        # Container for the floating effect
        self.toolbar_container = QWidget()
        self.toolbar_container.setFixedHeight(60) # Fixed height for consistency
        self.toolbar_container.setStyleSheet("""
            QWidget {
                background-color: #18181b; 
                border: 1px solid #27272a; 
                border-radius: 16px;
            }
        """)
        
        # Shadow for Floating Effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 180)) # Darker shadow
        self.toolbar_container.setGraphicsEffect(shadow)

        self.tb_layout = QHBoxLayout(self.toolbar_container)
        self.tb_layout.setContentsMargins(15, 5, 15, 5) # Tighter vertical margins
        self.tb_layout.setSpacing(10)
        
        # Common Button Style with Neon Glow on Hover
        btn_style = """
            QPushButton { 
                background: transparent; 
                border-radius: 10px; 
                font-size: 16px; 
                color: #A1A1AA; 
                border: none;
            }
            QPushButton:hover { 
                background: rgba(0, 240, 255, 0.08); 
                color: #00F0FF; 
            }
            QPushButton:pressed {
                background: rgba(0, 240, 255, 0.15);
            }
        """

        # Navigation
        self.back_btn = QPushButton("←")
        self.fwd_btn = QPushButton("→")
        self.reload_btn = QPushButton("↻")
        
        for btn in [self.back_btn, self.fwd_btn, self.reload_btn]:
            btn.setFixedSize(36, 36)
            btn.setStyleSheet(btn_style)
        
        self.back_btn.clicked.connect(lambda: self.tabs.currentWidget().back())
        self.fwd_btn.clicked.connect(lambda: self.tabs.currentWidget().forward())
        self.reload_btn.clicked.connect(lambda: self.tabs.currentWidget().reload())

        # Removed Library/Sidebar button as requested
        # self.tb_layout.addWidget(self.lib_btn) 
        
        self.tb_layout.addWidget(self.back_btn)
        self.tb_layout.addWidget(self.fwd_btn)
        self.tb_layout.addWidget(self.reload_btn)
        
        # URL Bar (Pill Shape)
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter address")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        # Style set in init for specificity, but layout added here
        self.tb_layout.addWidget(self.url_bar)
        
        # Custom AI Button
        self.ai_btn = QPushButton("✨") # Sparkle icon for AI
        self.ai_btn.setFixedSize(36, 36)
        # Make AI button stand out
        self.ai_btn.setStyleSheet("""
            QPushButton { 
                background: rgba(0, 240, 255, 0.1); 
                border-radius: 10px; 
                font-size: 18px; 
                color: #00F0FF; 
                border: 1px solid rgba(0, 240, 255, 0.3);
            }
            QPushButton:hover { 
                background: rgba(0, 240, 255, 0.2); 
                color: #FFFFFF; 
                border: 1px solid #00F0FF;
            }
            QPushButton:pressed {
                background: rgba(0, 240, 255, 0.3);
            }
        """)
        self.ai_btn.clicked.connect(self.open_ai_agent)
        self.tb_layout.addWidget(self.ai_btn)

        # Menu Button (Right)
        self.menu_btn = QPushButton("☰")
        self.menu_btn.setFixedSize(36, 36)
        self.menu_btn.setStyleSheet(btn_style)
        self.menu_btn.clicked.connect(self.show_menu)
        self.tb_layout.addWidget(self.menu_btn)
        
        self.main_layout.addWidget(self.toolbar_container)

    def open_ai_agent(self):
        if not self.sidebar.isVisible():
            self.sidebar.show()
        self.sidebar.show_ai_tab()

    def toggle_sidebar(self):
        if self.sidebar.isVisible():
            self.sidebar.hide()
        else:
            self.sidebar.show()

    def add_new_tab(self, qurl=None, label="New Tab"):
        # Apply Dot Trick globally to ALL new tabs (AI, Links, User)
        if qurl and isinstance(qurl, QUrl):
             host = qurl.host().lower()
             if "youtube.com" in host and not host.endswith("."):
                 new_host = host.replace("youtube.com", "youtube.com.")
                 qurl.setHost(new_host)
                 print(f"XeNit AdBlock: Applied Dot Trick (Global) -> {qurl.toString()}")
        
        return self.tabs.add_new_tab(qurl, label)

    def go_home(self):
        self.tabs.currentWidget().setUrl(QUrl("xenit://newtab"))

    def navigate_to_url(self):
        text = self.url_bar.text()
        if not text:
            return
            
        url = QUrl(text)
        if url.scheme() == "":
            if "." in text:
                url.setScheme("http")
            else:
                # Search
                url = QUrl(f"https://www.google.com/search?q={text}")
        
        # YouTube "Dot Trick" for Ad Blocking
        host = url.host().lower()
        if "youtube.com" in host and not host.endswith("."):
            new_host = host.replace("youtube.com", "youtube.com.")
            url.setHost(new_host)
            print(f"XeNit AdBlock: Applied Dot Trick (Nav) -> {url.toString()}")
        
        self.tabs.currentWidget().setUrl(url)

    def update_url_bar(self, qurl, browser=None):
        if not hasattr(self, 'tabs') or browser != self.tabs.currentWidget():
            return

        if qurl.scheme() == "xenit":
            self.url_bar.setText("")
            self.url_bar.setPlaceholderText("Search the future...")
        else:
            self.url_bar.setText(qurl.toString())
            self.url_bar.setCursorPosition(0)

        # History Tracking
        if qurl.scheme() in ["http", "https"]:
            self.data_manager.add_history_item(browser.title(), qurl.toString())

    def show_menu(self):
        menu = CustomMenu(self)
        
        # Connect actions
        menu.actions()[0].triggered.connect(self.show_sign_in) # Sign In is first action
        
        menu.new_tab_action.triggered.connect(lambda: self.add_new_tab())
        menu.new_window_action.triggered.connect(self.open_new_window)
        
        menu.history_action.triggered.connect(self.open_history)
        menu.bookmarks_action.triggered.connect(self.open_bookmarks)
        menu.downloads_action.triggered.connect(self.open_downloads)
        
        menu.settings_action.triggered.connect(self.open_settings)
        menu.help_action.triggered.connect(self.open_help)
        menu.exit_action.triggered.connect(self.close)
        
        # Show relative to button
        menu.exec(self.menu_btn.mapToGlobal(self.menu_btn.rect().bottomLeft()))

    def open_new_window(self):
        # Create a new instance of BrowserWindow
        new_win = BrowserWindow()
        new_win.show()
        # Keep reference in a list on the main app if needed, 
        # normally purely local variable in Qt slots might get GC'd unless parented or explicitly referenced.
        # But for Top Level widgets .show() usually keeps them alive until closed if they have no parent.
        # To be safe, let's assume the main loop handles it, or we can add to a global list if tricky.
        pass

    def open_history(self):
        dlg = HistoryDialog(self)
        dlg.exec()

    def open_bookmarks(self):
        dlg = BookmarksDialog(self)
        dlg.exec()
        
    def open_downloads(self):
        dlg = DownloadsDialog(self)
        dlg.exec()

    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()
        
    def open_help(self):
        dlg = HelpDialog(self)
        dlg.exec()

    def show_sign_in(self):
        dlg = SignInDialog(self)
        dlg.exec()
