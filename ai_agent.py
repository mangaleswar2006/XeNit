import datetime
import re
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class AIAgent:
    def __init__(self, memory_manager):
        self.memory = memory_manager
        self.controller = None # Browser controller interface
        
        # NVIDIA API Setup
        # Ideally, this key should be in an environment variable or secure config.
        self.api_key = "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"
        self.base_url = "https://integrate.api.nvidia.com/v1"
        
        if OpenAI:
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key
            )
        else:
            self.client = None
            print("XeNit AI: OpenAI library not installed. Running in mock mode.")

    def set_controller(self, controller):
        """
        Sets the controller object (BrowserWindow wrapper) to perform actions.
        Expected methods: open_url(url), play_music(query), open_whatsapp()
        """
        self.controller = controller

    def chat(self, user_message, context=None):
        """
        Process a user message with the given context (current page info).
        Returns a string response.
        """
        # 0. Check for local memory updates (fast path)
        if "i like" in user_message.lower():
            fact = user_message.lower().replace("i like", "").strip()
            self.memory.add_user_fact(f"Likes {fact}")
            return f"(I've remembered that you like {fact})"

        if "what did i" in user_message.lower() or "remember" in user_message.lower():
            facts = self.memory.get_relevant_facts()
            if facts:
                return "Here's what I remember about you:\n- " + "\n- ".join(facts)
            else:
                return "I don't have many facts stored about you yet."

        # 0.5 Check for Cleanup Confirmation (Tab Management)
        # Relaxed matching for "yes", "sure", "do it", "ok"
        confirms = ["yes", "sure", "do it", "ok", "clean", "close", "yep", "allow"]
        is_confirmed = any(c in user_message.lower() for c in confirms)
        
        if context and context.get("cleanup_proposal") and is_confirmed:
             proposal = context["cleanup_proposal"]
             indices = proposal["indices"] # List of tab indices
             topic = proposal["topic"]
             titles = proposal.get("titles", [])
             
             # Strategy: Keep first 2, Close rest (2..N)
             close_indices = indices[2:] 
             
             if not close_indices:
                 return f"I analyzed your tabs about '{topic}' but there aren't enough to safely close. I'll keep them open."
             
             import json
             # Generate a mini-summary of what is kept
             kept_titles = titles[:2]
             summary_text = f"Keeping focused on:\n1. {kept_titles[0]}\n2. {kept_titles[1] if len(kept_titles)>1 else ''}..."
             
             response = f"Cleaning up tabs for '{topic}'. {summary_text}\nClosing {len(close_indices)} background tabs. [[CLOSE_TABS: {json.dumps(close_indices)}]]"
             self._process_actions(response)
             return response

        # 1. Prepare Context & Instructions for LLM
        system_prompt = """You are XeNit AI, an advanced browser agent. 
You can control the browser to help the user.
To perform actions, output specific tags at the END of your response:
- To open a website: [[OPEN: url]]
- To play music: [[MUSIC: song name]]
- To open WhatsApp: [[WHATSAPP: <phone_number>|<text>]]
- To search: [[SEARCH: query]]
- To fill forms: [[AUTOFILL: {"Label": "Value", ...}]] (Use JSON format. CRITICAL: Use "User Profile Data" below. DO NOT ASK USER FOR INFO YOU ALREADY HAVE.)
- To click something: [[CLICK: text]] (Click a button/link)
- To save user details: [[SAVE_PROFILE: {"Key": "Value", ...}]]
- To close specific tabs: [[CLOSE_TABS: [id1, id2...]]]

Example: "I'll apply using your profile. [[AUTOFILL: {"Name": "Lucky", "Email": "lucky@example.com"}]] [[CLICK: Submit]]"
Be concise."""
        
        # Add Memory to Context
        user_facts = self.memory.get_relevant_facts()
        if user_facts:
            system_prompt += f"\n\nUser Notes/Facts:\n" + "\n".join(user_facts)

        # Add User Profile Data
        user_profile = self.memory.get_profile()
        if user_profile:
            import json
            system_prompt += f"\n\nUser Profile Data (Use this for forms):\n{json.dumps(user_profile, indent=2)}"
            
        # Add Page Context
        page_context_str = ""
        if context:
            page_context_str = f"\nCurrent Page Title: {context.get('title', 'Unknown')}\nCurrent URL: {context.get('url', 'Unknown')}\n"
            if context.get('text'):
                # Truncate text to avoid token limits (NVIDIA Nim limits vary, safely assuming ~4k chars for now)
                truncated_text = context['text'][:8000] 
                page_context_str += f"Page Content (Truncated): {truncated_text}\n"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{page_context_str}\n\nUser Query: {user_message}"}
        ]
        
        print("DEBUG - SYSTEM PROMPT INJECTED:")
        print(system_prompt)
        print("DEBUG - FULL MESSAGES:")
        print(messages)

        # 2. Call API
        response = ""
        if self.client:
            try:
                completion = self.client.chat.completions.create(
                    model="meta/llama-3.1-405b-instruct", # Using a high-quality model available on NVIDIA NIM
                    messages=messages,
                    temperature=0.2,
                    top_p=0.7,
                    max_tokens=1024,
                    stream=False
                )
                response = completion.choices[0].message.content
            except Exception as e:
                return f"⚠️ AI Error: {str(e)}"
        else:
             return "⚠️ OpenAI library missing. Please install it to use the AI features."

        # 3. Process Actions
        self._process_actions(response)
        
        return response

    def _process_actions(self, response_text):
        """
        Parses response for [[ACTION: param]] tags and executes them.
        """
        if not self.controller:
            return

        # Regex for tags like [[OPEN: google.com]]
        # We look for [[KEY: VALUE]]
        pattern = r"\[\[([A-Z]+):(.*?)\]\]" 
        matches = re.findall(pattern, response_text)
        
        for action, param in matches:
            param = param.strip()
            print(f"XeNit Agent Action: {action} -> {param}")
            
            if action == "OPEN":
                self.controller.open_url(param)
            elif action == "MUSIC":
                self.controller.play_music(param)
            elif action == "WHATSAPP":
                self.controller.open_whatsapp(param)
            elif action == "SEARCH":
                self.controller.open_url(f"google.com/search?q={param}")
            elif action == "AUTOFILL":
                self.controller.auto_fill(param)
            elif action == "CLICK":
                self.controller.click_element(param)
            elif action == "CLOSE_TABS":
                self.controller.close_specific_tabs(param)
            elif action == "SAVE_PROFILE":
                try:
                    import json
                    data = json.loads(param)
                    self.memory.update_profile(data)
                    print("XeNit Agent: Profile Updated")
                except Exception as e:
                    print(f"XeNit Agent: Failed to save profile - {e}")


    def analyze_page(self, html_content, url):
        """
        Proactive analysis of a page when loaded.
        """
        pass

    def check_safety(self, context):
        if not context: return "No page loaded."
        url = context.get('url', '')
        if "http:" in url and "https" not in url:
            return "⚠️ **Warning**: This site is using HTTP. Your connection is not secure."
        return "✅ This site looks standard. Connection is secure (HTTPS)."
