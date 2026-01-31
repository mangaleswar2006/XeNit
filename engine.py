from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings, QWebEngineScript
from PyQt6.QtCore import QUrl
from browser.adblock import AdBlockInterceptor

class WebView(QWebEngineView):
    def __init__(self, tab_index, parent=None):
        super().__init__(parent)
        self.tab_index = tab_index
        self.parent_window = parent # Reference to BrowserWindow or TabManager
        self.last_extracted_text = ""
        
        self.loadFinished.connect(self.extract_page_text)
        
        # Setup Profile and Settings
        self.profile = QWebEngineProfile.defaultProfile()
        # Use a specific, common Chrome version to pass security checks
        self.profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.130 Safari/537.36")
        
        # Enforce Dark Mode on Web Content if supported
        # Note: This is an internal Chromium setting, might not work on all PyQt versions perfectly
        # but we can inject CSS as a fallback or use ForceDarkMode preference if available in newer Qt
        
        self.settings = self.page().settings()
        self.settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        self.settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        self.settings.setAttribute(QWebEngineSettings.WebAttribute.ScreenCaptureEnabled, True)
        self.settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
        self.settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        # Performance: Disable Auditing (prevents some tracking calls)
        self.settings.setAttribute(QWebEngineSettings.WebAttribute.HyperlinkAuditingEnabled, False)
        # Enable DnsPrefetch
        self.settings.setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, True)
        # Allow Autoplay without User Gesture
        self.settings.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
        
        # GPU Acceleration Flags
        # We can't set command line args here easily per-view, 
        # but we ensure the profile uses system http cache
        self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        
        # AdBlock
        self.interceptor = AdBlockInterceptor(self)
        self.profile.setUrlRequestInterceptor(self.interceptor)
        
        # 1. EARLY SHIELD (DocumentCreation)
        # Prevents popups and injects CSS rules before page renders fully
        # ALSO: Spoofs navigator behavior to look like a real browser (not automation)
        
        # CSS Code for Cosmetic Filtering
        css_code = """
        /* Generic Ad Hiding Rules */
        div[id^="google_ads_"], div[id*="google_ads_"],
        iframe[id^="google_ads_"], iframe[id*="google_ads_"],
        iframe[src*="doubleclick.net"], iframe[src*="googlesyndication.com"],
        .adsbygoogle, .google-auto-placed, .ad-banner, .banner-ad,
        .ad_unit, .ad-slot, .ad-wrapper, .ad-container,
        .text-ad, .sponsor-ad, .sponsored-link,
        a[href*="/ad/"], a[href*="doubleclick"],
        div[data-ad-unit], div[data-google-query-id] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            width: 0 !important;
            pointer-events: none !important;
        }
        """
        
        early_shield_js = f"""
        (function() {{
            try {{
                // 0. JSON INTERCEPTION (The "Forceful" Fix)
                // YouTube delivers ad configurations in JSON blobs. We strip them out before the player sees them.
                const originalParse = JSON.parse;
                JSON.parse = function(text, reviver) {{
                    const data = originalParse(text, reviver);
                    if (data && typeof data === 'object') {{
                        // YouTube Ad Keys
                        if (data.adPlacements) {{
                            delete data.adPlacements;
                            console.log('XeNit AdBlock: Stripped adPlacements');
                        }}
                        if (data.playerAds) {{
                            delete data.playerAds;
                            console.log('XeNit AdBlock: Stripped playerAds');
                        }}
                    }}
                    return data;
                }};
                
                // 1. Strict Popup Blocker (Immediate)
                window.open = function(url, target, features) {{
                    console.log('XeNit AdBlock: Blocked Popup to ' + url);
                    return null;
                }};
                
                // 2. STEALTH MODE: Anti-Detection Evasions
                
                // A. Hide Webdriver (The biggest flag)
                Object.defineProperty(navigator, 'webdriver', {{
                    get: () => undefined
                }});
                
                // B. Mock window.chrome (Required for Google Login)
                if (!window.chrome) {{
                    window.chrome = {{
                        runtime: {{}},
                        loadTimes: function() {{}},
                        csi: function() {{}},
                        app: {{}}
                    }};
                }}
                
                // C. Mock Plugins (Empty plugins array triggers bots)
                if (navigator.plugins.length === 0) {{
                    Object.defineProperty(navigator, 'plugins', {{
                        get: () => [1, 2, 3, 4, 5] // Dummy length to fool checks
                    }});
                }}
                
                // D. Mock Languages
                Object.defineProperty(navigator, 'languages', {{
                    get: () => ['en-US', 'en']
                }});
                
                // E. Mock Permissions (Passes notification checks)
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                    Promise.resolve({{ state: Notification.permission }}) :
                    originalQuery(parameters)
                );
                
                console.log('XeNit Stealth Mode: Active');
                
            }} catch (e) {{
                console.log('XeNit Stealth Error: ' + e);
            }}
        }})();
        """
        
        script_early = QWebEngineScript()
        script_early.setName("XeNitShieldStart")
        script_early.setSourceCode(early_shield_js)
        script_early.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
        script_early.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        self.profile.scripts().insert(script_early)
        
        # 2. LATE SHIELD (DocumentReady)
        # Injects CSS and cleans up elements
        late_shield_js = f"""
        (function() {{
            // 1. Cosmetic CSS Injection
            const style = document.createElement('style');
            style.type = 'text/css';
            style.textContent = `{css_code}`; 
            (document.head || document.documentElement).appendChild(style);
            
            // 2. AGGRESSIVE YOUTUBE CLEANER
            function cleanYouTube() {{
                const player = document.querySelector('#movie_player');
                const video = document.querySelector('video');
                
                // A. Skip Buttons (Click immediately)
                const skipBtn = document.querySelector('.ytp-ad-skip-button, .ytp-ad-skip-button-modern, .videoAdUiSkipButton');
                if (skipBtn) {{
                    skipBtn.click();
                    console.log('XeNit AdBlock: Skipped Ad (Click)');
                }}
                
                // B. Overlay Ads (Remove)
                const overlays = document.querySelectorAll('.ytp-ad-overlay-container, .ytp-ad-image-overlay, .ytp-ad-module');
                overlays.forEach(overlay => {{
                    overlay.style.display = 'none';
                    // Don't remove module, it might hold the skip button logic
                    if (!overlay.classList.contains('ytp-ad-module')) overlay.remove();
                }});
                
                // Force Autoplay Next (User Request "Activate Autopay")
                const autoNav = document.querySelector('.ytp-autonav-toggle-button[aria-checked="false"]');
                if (autoNav) {{
                    autoNav.click();
                    console.log('XeNit: Enabled Autoplay Next');
                }}
                
                // Auto-Close Consent Popups (if any)
                const consent = document.querySelector('button[aria-label^="Accept"]');
                if (consent) consent.click();

                // 3. CAPTCHA AUTO-SOLVER (Simple Checkboxes)
                function cleanCaptcha() {{
                    // Cloudflare Turnstile / Challenge
                    const cfBox = document.querySelector('#challenge-stage input[type="checkbox"]');
                    if (cfBox && !cfBox.checked) {{
                        cfBox.click();
                        console.log("XeNit: Clicked Cloudflare Checkbox");
                    }}
                    
                    // Generic "I am human" buttons (careful selector)
                    const challenge = document.querySelector('#turnstile-wrapper iframe') || document.querySelector('.cf-turnstile iframe');
                    if (challenge) {{
                        // We can't click INSIDE an iframe easily without logic in that frame.
                    }}
                }}
                cleanCaptcha();

                // C. Video Ads (Speed Up & Mute & Seek)
                // Check multiple indicators
                const adShowing = document.querySelector('.ad-showing, .job-ad-showing');
                const isInterrupting = player && player.classList.contains('ad-interrupting');
                
                if (video && (adShowing || isInterrupting)) {{
                    video.muted = true;
                    video.playbackRate = 16.0; // Fast forward
                    // Force seek to end
                    if (!isNaN(video.duration)) {{
                         video.currentTime = video.duration;
                    }}
                    console.log('XeNit AdBlock: Fast-Forwarding/Seeking Ad');
                    
                    // Force click skip if available inside the ad container
                    const innerSkip = document.querySelector('.ytp-ad-skip-button-slot');
                    if (innerSkip) innerSkip.click();
                }} else if (video && video.paused && !adShowing && !isInterrupting) {{
                    // Force play main video if it's paused at the start (and not an ad)
                    // We check if it's the main video by ensuring no ad UI is present
                    if (video.currentTime < 2) {{
                         video.play();
                         console.log('XeNit: Force Playing Video');
                    }}
                }}
                
                // D. Static Ad Containers
                const adSelectors = [
                    'ytd-promoted-sparkles-web-renderer', 'ytd-display-ad-renderer', 
                    'ytd-statement-banner-renderer', 'ytd-in-feed-ad-layout-renderer',
                    '#masthead-ad', 'ytd-banner-promo-renderer', '#player-ads',
                    '.ytd-merch-shelf-renderer', 'ytd-ad-slot-renderer',
                    'ytd-player-legacy-desktop-watch-ads-renderer',
                    'ytd-rich-item-renderer.ytd-ad-slot-renderer'
                ];
                adSelectors.forEach(sel => {{
                    document.querySelectorAll(sel).forEach(el => {{
                        el.style.display = 'none';
                        el.remove();
                    }});
                }});
            }}
            
            // Run loop (Balanced: 300ms)
            setInterval(cleanYouTube, 300); 
            
            // Also use MutationObserver for immediate reaction
            const observer = new MutationObserver(cleanYouTube);
            observer.observe(document.body, {{ childList: true, subtree: true }});
            
            console.log('XeNit AdBlock: Aggressive Sweeper Active');
        }})();
        """
        
        script_late = QWebEngineScript()
        script_late.setName("XeNitShieldEnd")
        script_late.setSourceCode(late_shield_js)
        script_late.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
        script_late.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        self.profile.scripts().insert(script_late)

    def createWindow(self, type):
        # BLOCK OFFENSIVE POPUPS
        # Fix: WebPopup might not exist in all Qt bindings, rely on WebDialog
        if type == QWebEnginePage.WebWindowType.WebDialog:
            print("XeNit AdBlock: Blocked Popup Window")
            return None
            
        # Handle "Open in New Tab" requests from web pages (likely legitimate links)
        if self.window():
            # traverse up to find BrowserWindow
            main_window = self.window()
            if hasattr(main_window, 'add_new_tab'):
                new_view = main_window.add_new_tab(QUrl("about:blank"), "New Tab")
                return new_view
        return super().createWindow(type)

    def extract_page_text(self):
        # Run JS to get body text
        self.page().runJavaScript("document.body.innerText", self._store_text_callback)

    def _store_text_callback(self, result):
        if isinstance(result, str):
            self.last_extracted_text = result
