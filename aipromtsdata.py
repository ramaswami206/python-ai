#!/usr/bin/env python3
"""
Enhanced Futuristic AI Tools Checker with Auto-Prompt Injection
Automatically passes prompts to AI websites using JavaScript injection
"""

import os
import time
import webbrowser
import threading
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import quote
import tempfile
import sys
from functools import partial

class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler with additional routes"""
    
    def __init__(self, *args, checker_instance=None, **kwargs):
        self.checker = checker_instance
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.checker.get_html().encode('utf-8'))
        elif self.path == '/open-all':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.checker.open_all_tools()
            self.wfile.write(json.dumps({'status': 'success'}).encode('utf-8'))
        elif self.path == '/get-injection-bookmarklet':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            bookmarklet = self.checker.generate_universal_bookmarklet()
            self.wfile.write(json.dumps({'bookmarklet': bookmarklet}).encode('utf-8'))
        else:
            super().do_GET()
    
    def log_message(self, format, *args):
        """Suppress log messages"""
        pass

class EnhancedAIChecker:
    def __init__(self):
        self.ai_tools = {
            'ChatGPT': {
                'url': 'https://chat.openai.com',
                'selector': 'textarea[placeholder*="Message"]',
                'submit_selector': 'button[data-testid="send-button"]',
                'wait_time': 3
            },
            'Claude': {
                'url': 'https://claude.ai',
                'selector': 'div[contenteditable="true"]',
                'submit_selector': 'button[aria-label="Send Message"]',
                'wait_time': 3
            },
            'Gemini': {
                'url': 'https://gemini.google.com',
                'selector': 'rich-textarea[placeholder*="Enter a prompt here"]',
                'submit_selector': 'button[aria-label="Send message"]',
                'wait_time': 4
            },
            'Copilot': {
                'url': 'https://copilot.microsoft.com',
                'selector': 'textarea[placeholder*="Ask me anything"]',
                'submit_selector': 'button[aria-label="Submit"]',
                'wait_time': 3
            },
            'Perplexity': {
                'url': 'https://perplexity.ai',
                'selector': 'textarea[placeholder*="Ask anything"]',
                'submit_selector': 'button[aria-label="Submit"]',
                'wait_time': 3
            },
            'Character.AI': {
                'url': 'https://character.ai',
                'selector': 'textarea[placeholder*="Type a message"]',
                'submit_selector': 'button[type="submit"]',
                'wait_time': 4
            },
            'Poe': {
                'url': 'https://poe.com',
                'selector': 'textarea[placeholder*="Talk to"]',
                'submit_selector': 'button[class*="send"]',
                'wait_time': 3
            },
            'Hugging Face': {
                'url': 'https://huggingface.co/chat',
                'selector': 'textarea[placeholder*="Type a message"]',
                'submit_selector': 'button[type="submit"]',
                'wait_time': 3
            },
            'Cohere': {
                'url': 'https://coral.cohere.com',
                'selector': 'textarea[placeholder*="Enter your prompt"]',
                'submit_selector': 'button[type="submit"]',
                'wait_time': 3
            },
            'You.com': {
                'url': 'https://you.com',
                'selector': 'textarea[placeholder*="Ask anything"]',
                'submit_selector': 'button[aria-label="Send"]',
                'wait_time': 3
            }
        }
        
        self.prompt = ""
        self.server_port = 8080
        self.opened_tabs = []
        self.server = None
        self.server_thread = None
        
    def read_prompt(self):
        """Read prompt from abc.txt file"""
        try:
            with open('abc.txt', 'r', encoding='utf-8') as file:
                self.prompt = file.read().strip()
                print(f"✅ Prompt loaded: {self.prompt[:50]}...")
                return True
        except FileNotFoundError:
            print("❌ abc.txt not found, creating sample...")
            self.create_sample_prompt()
            return self.read_prompt()
        except Exception as e:
            print(f"❌ Error reading abc.txt: {e}")
            return False
    
    def create_sample_prompt(self):
        """Create sample abc.txt"""
        sample = """Write a Python script to upload APK files to AWS S3 bucket with proper error handling and progress tracking. Include features like:
1. File validation
2. Progress bars
3. Retry logic
4. Logging
5. Error handling"""
        
        with open('abc.txt', 'w', encoding='utf-8') as file:
            file.write(sample)
        print("✅ Created sample abc.txt")
    
    def escape_string_for_js(self, text):
        """Properly escape string for JavaScript"""
        return (text.replace('\\', '\\\\')
                   .replace('"', '\\"')
                   .replace("'", "\\'")
                   .replace('\n', '\\n')
                   .replace('\r', '\\r')
                   .replace('\t', '\\t'))
    
    def generate_injection_script(self, ai_name, config):
        """Generate JavaScript injection script for specific AI"""
        escaped_prompt = self.escape_string_for_js(self.prompt)
        safe_name = ai_name.replace('.', '_').replace(' ', '_')
        
        script_parts = [
            "// Auto-prompt injection for " + ai_name,
            "function injectPrompt_" + safe_name + "() {",
            "    console.log('🚀 Injecting prompt into " + ai_name + "...');",
            "    setTimeout(() => {",
            "        try {",
            "            let textArea = document.querySelector('" + config["selector"] + "');",
            "            if (!textArea) {",
            "                textArea = document.querySelector('textarea') || ",
            "                          document.querySelector('[contenteditable=\"true\"]') ||",
            "                          document.querySelector('input[type=\"text\"]');",
            "            }",
            "            if (textArea) {",
            "                textArea.value = '';",
            "                textArea.textContent = '';",
            "                if (textArea.tagName === 'TEXTAREA' || textArea.tagName === 'INPUT') {",
            "                    textArea.value = \"" + escaped_prompt + "\";",
            "                    textArea.dispatchEvent(new Event('input', { bubbles: true }));",
            "                    textArea.dispatchEvent(new Event('change', { bubbles: true }));",
            "                } else {",
            "                    textArea.textContent = \"" + escaped_prompt + "\";",
            "                    textArea.innerHTML = \"" + escaped_prompt + "\";",
            "                    textArea.dispatchEvent(new Event('input', { bubbles: true }));",
            "                }",
            "                textArea.focus();",
            "                textArea.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true }));",
            "                textArea.dispatchEvent(new KeyboardEvent('keydown', { bubbles: true }));",
            "                console.log('✅ Prompt injected successfully into " + ai_name + "');",
            "            } else {",
            "                console.warn('❌ Could not find text input for " + ai_name + "');",
            "            }",
            "        } catch (error) {",
            "            console.error('❌ Error injecting prompt into " + ai_name + ":', error);",
            "        }",
            "    }, " + str(config["wait_time"]) + "000);",
            "}",
            "injectPrompt_" + safe_name + "();"
        ]
        
        return '\n'.join(script_parts)
    
    def generate_universal_bookmarklet(self):
        """Generate a universal bookmarklet for prompt injection"""
        escaped_prompt = self.escape_string_for_js(self.prompt)
        
        js_code = 'javascript:(function(){const prompt="' + escaped_prompt + '";'
        js_code += 'const selectors=['
        js_code += '\'textarea[placeholder*="Message"]\','
        js_code += '\'div[contenteditable="true"]\','
        js_code += '\'textarea[placeholder*="prompt"]\','
        js_code += '\'textarea[placeholder*="Ask"]\','
        js_code += '\'textarea[placeholder*="Type"]\','
        js_code += '\'textarea[placeholder*="Enter"]\','
        js_code += '\'textarea\','
        js_code += '\'input[type="text"]\','
        js_code += '\'[contenteditable="true"]\''
        js_code += '];'
        js_code += 'let found=false;'
        js_code += 'for(const selector of selectors){'
        js_code += 'const el=document.querySelector(selector);'
        js_code += 'if(el){'
        js_code += 'if(el.tagName==="TEXTAREA"||el.tagName==="INPUT"){'
        js_code += 'el.value=prompt;'
        js_code += 'el.dispatchEvent(new Event("input",{bubbles:true}));'
        js_code += 'el.dispatchEvent(new Event("change",{bubbles:true}));'
        js_code += '}else{'
        js_code += 'el.textContent=prompt;'
        js_code += 'el.innerHTML=prompt;'
        js_code += 'el.dispatchEvent(new Event("input",{bubbles:true}));'
        js_code += '}'
        js_code += 'el.focus();'
        js_code += 'found=true;'
        js_code += 'break;'
        js_code += '}'
        js_code += '}'
        js_code += 'if(found){'
        js_code += 'alert("✅ Prompt injected successfully!");'
        js_code += '}else{'
        js_code += 'alert("❌ Could not find text input field");'
        js_code += '}'
        js_code += '})();'
        
        return js_code
    
    def open_ai_with_prompt(self, ai_name, config):
        """Open AI website with auto-prompt injection"""
        try:
            # Just open the URL directly
            webbrowser.open(config['url'])
            
            # Store tab info for later injection
            self.opened_tabs.append({
                'name': ai_name,
                'url': config['url'],
                'config': config
            })
            
            print(f"  📂 Opened {ai_name} - Use bookmarklet or console to inject prompt")
            
        except Exception as e:
            print(f"  ❌ Failed to open {ai_name}: {e}")
    
    def open_all_tools(self):
        """Open all AI tools"""
        print("🚀 Opening all AI tools...")
        
        for name, config in self.ai_tools.items():
            self.open_ai_with_prompt(name, config)
            time.sleep(1)  # Stagger opening to prevent browser overload
        
        print("✅ All tools opened!")
        print("💡 Use the bookmarklet or browser console to inject prompts")
        print("🔧 Manual submission required for safety")
    
    def get_enhanced_cards(self):
        """Generate enhanced AI cards HTML"""
        cards_html = ""
        for name, config in self.ai_tools.items():
            card_template = '''
            <div class="ai-card">
                <h3>%s</h3>
                <div class="features">Auto-injection ready • %ss delay</div>
                <a href="%s" target="_blank" class="ai-link">Launch %s</a>
            </div>
            '''
            cards_html += card_template % (name, config['wait_time'], config['url'], name)
        return cards_html
    
    def get_html(self):
        """Generate the HTML for the dashboard"""
        prompt_display = self.prompt.replace('<', '&lt;').replace('>', '&gt;')
        cards_html = self.get_enhanced_cards()
        prompt_js = self.escape_string_for_js(self.prompt)
        
        # Build HTML in parts to avoid triple quote issues
        html_parts = []
        
        # Start of HTML
        html_parts.append('<!DOCTYPE html>')
        html_parts.append('<html>')
        html_parts.append('<head>')
        html_parts.append('<title>Enhanced AI Command Center</title>')
        html_parts.append('<style>')
        html_parts.append(self.get_css())
        html_parts.append('</style>')
        html_parts.append('</head>')
        html_parts.append('<body>')
        
        # Body content
        html_parts.append('<div class="container">')
        html_parts.append('<div class="main-panel">')
        html_parts.append('<h1>🚀 Enhanced AI Command Center</h1>')
        
        html_parts.append('<div class="system-status">')
        html_parts.append('<h3 class="terminal-text">')
        html_parts.append('<span class="status-indicator"></span>')
        html_parts.append('AUTO-INJECTION SYSTEM: ARMED')
        html_parts.append('</h3>')
        html_parts.append('<p>Advanced prompt injection protocols loaded. All AI interfaces ready for automated deployment.</p>')
        html_parts.append('</div>')
        
        html_parts.append('<div class="feature-highlight">')
        html_parts.append('<h3>🎯 NEW: Auto-Prompt Injection</h3>')
        html_parts.append('<p>Automatically fills your prompt into all AI chat interfaces. No more copy-pasting!</p>')
        html_parts.append('</div>')
        
        html_parts.append('<div class="prompt-display">')
        html_parts.append('<h3 style="color: #00ffff; margin-bottom: 15px;">📡 ACTIVE PROMPT TRANSMISSION:</h3>')
        html_parts.append('<div class="terminal-text">' + prompt_display + '</div>')
        html_parts.append('</div>')
        
        html_parts.append('<div class="control-center">')
        html_parts.append('<button onclick="launchAllSystems()" class="cyber-btn">🚀 Launch All Sites</button>')
        html_parts.append('<button onclick="copyToClipboard()" class="cyber-btn secondary">📋 Copy Prompt</button>')
        html_parts.append('<button onclick="generateBookmarklet()" class="cyber-btn tertiary">🔖 Get Bookmarklet</button>')
        html_parts.append('</div>')
        
        html_parts.append('<div class="bookmarklet-section" id="bookmarkletSection" style="display: none;">')
        html_parts.append('<h3 style="color: #ffff00; margin-bottom: 15px;">🔖 Universal Prompt Injector</h3>')
        html_parts.append('<p>Drag this bookmarklet to your bookmarks bar, then click it on any AI website to inject your prompt:</p>')
        html_parts.append('<a href="#" id="bookmarkletLink" class="bookmarklet-link">📌 Prompt Injector</a>')
        html_parts.append('<p style="margin-top: 10px; font-size: 0.9em; color: #ccc;">Works on ChatGPT, Claude, Gemini, and most other AI chat interfaces!</p>')
        html_parts.append('</div>')
        
        html_parts.append('<div class="ai-grid">')
        html_parts.append(cards_html)
        html_parts.append('</div>')
        
        html_parts.append('</div>')
        html_parts.append('</div>')
        
        # JavaScript
        html_parts.append('<script>')
        html_parts.append('const promptText = `' + prompt_js + '`;')
        html_parts.append(self.get_javascript())
        html_parts.append('</script>')
        
        html_parts.append('</body>')
        html_parts.append('</html>')
        
        return '\n'.join(html_parts)
    
    def get_css(self):
        """Get CSS styles"""
        css = '''
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Rajdhani', sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            overflow-x: hidden;
            position: relative;
            min-height: 100vh;
        }
        
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 80%, rgba(0, 255, 255, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 0, 255, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(0, 255, 0, 0.1) 0%, transparent 50%),
                linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
            animation: backgroundShift 25s ease-in-out infinite;
            z-index: -1;
        }
        
        @keyframes backgroundShift {
            0%, 100% { transform: scale(1) rotate(0deg); }
            33% { transform: scale(1.1) rotate(120deg); }
            66% { transform: scale(1.05) rotate(240deg); }
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 20px;
            position: relative;
            z-index: 10;
        }
        
        .main-panel {
            background: rgba(10, 10, 10, 0.95);
            border: 2px solid transparent;
            border-radius: 20px;
            padding: 40px;
            backdrop-filter: blur(20px);
            position: relative;
            overflow: hidden;
        }
        
        .main-panel::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            padding: 2px;
            background: linear-gradient(45deg, #00ffff, #ff00ff, #00ff00, #ffff00, #00ffff);
            border-radius: 20px;
            mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            mask-composite: exclude;
            animation: borderGlow 4s ease-in-out infinite;
        }
        
        @keyframes borderGlow {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        h1 {
            font-family: 'Orbitron', monospace;
            text-align: center;
            font-size: 3.5em;
            font-weight: 900;
            margin-bottom: 30px;
            background: linear-gradient(45deg, #00ffff, #ff00ff, #00ff00);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: titlePulse 3s ease-in-out infinite;
            letter-spacing: 3px;
            text-transform: uppercase;
        }
        
        @keyframes titlePulse {
            0%, 100% { text-shadow: 0 0 30px rgba(0, 255, 255, 0.5); }
            50% { text-shadow: 0 0 50px rgba(0, 255, 255, 0.8), 0 0 80px rgba(255, 0, 255, 0.3); }
        }
        
        .system-status {
            background: linear-gradient(135deg, rgba(0, 255, 255, 0.1), rgba(255, 0, 255, 0.1));
            border: 1px solid rgba(0, 255, 255, 0.3);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
        }
        
        .prompt-display {
            background: rgba(0, 20, 40, 0.9);
            border: 1px solid rgba(0, 255, 255, 0.4);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            font-family: 'Courier New', monospace;
            font-size: 1.1em;
            line-height: 1.6;
            box-shadow: inset 0 0 20px rgba(0, 255, 255, 0.1);
            max-height: 200px;
            overflow-y: auto;
        }
        
        .control-center {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 40px 0;
            flex-wrap: wrap;
        }
        
        .cyber-btn {
            background: linear-gradient(45deg, #1a1a2e, #16213e);
            border: 2px solid #00ffff;
            color: #00ffff;
            padding: 15px 30px;
            border-radius: 30px;
            font-family: 'Orbitron', monospace;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            text-transform: uppercase;
            letter-spacing: 2px;
            min-width: 200px;
        }
        
        .cyber-btn:hover {
            background: linear-gradient(45deg, #00ffff, #0080ff);
            color: #000;
            box-shadow: 0 0 30px rgba(0, 255, 255, 0.6);
            transform: translateY(-3px);
        }
        
        .cyber-btn.secondary {
            border-color: #ff00ff;
            color: #ff00ff;
        }
        
        .cyber-btn.secondary:hover {
            background: linear-gradient(45deg, #ff00ff, #ff0080);
            box-shadow: 0 0 30px rgba(255, 0, 255, 0.6);
        }
        
        .cyber-btn.tertiary {
            border-color: #00ff00;
            color: #00ff00;
        }
        
        .cyber-btn.tertiary:hover {
            background: linear-gradient(45deg, #00ff00, #80ff00);
            box-shadow: 0 0 30px rgba(0, 255, 0, 0.6);
        }
        
        .feature-highlight {
            background: linear-gradient(135deg, rgba(0, 255, 0, 0.1), rgba(255, 255, 0, 0.1));
            border: 1px solid rgba(0, 255, 0, 0.3);
            border-radius: 15px;
            padding: 25px;
            margin: 30px 0;
            text-align: center;
        }
        
        .feature-highlight h3 {
            color: #00ff00;
            font-family: 'Orbitron', monospace;
            margin-bottom: 15px;
            font-size: 1.5em;
        }
        
        .ai-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-top: 40px;
        }
        
        .ai-card {
            background: linear-gradient(135deg, rgba(26, 26, 46, 0.9), rgba(22, 33, 62, 0.9));
            border: 1px solid rgba(0, 255, 255, 0.3);
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
        }
        
        .ai-card:hover {
            border-color: #00ffff;
            transform: translateY(-10px) scale(1.02);
            box-shadow: 0 20px 40px rgba(0, 255, 255, 0.2);
        }
        
        .ai-card h3 {
            font-family: 'Orbitron', monospace;
            font-size: 1.8em;
            margin-bottom: 15px;
            color: #00ffff;
            text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
        }
        
        .ai-card .features {
            font-size: 0.9em;
            color: #00ff00;
            margin-bottom: 20px;
        }
        
        .ai-link {
            display: inline-block;
            background: linear-gradient(45deg, #00ffff, #0080ff);
            color: #000;
            padding: 12px 25px;
            text-decoration: none;
            border-radius: 25px;
            font-weight: 600;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .ai-link:hover {
            transform: scale(1.1);
            box-shadow: 0 10px 25px rgba(0, 255, 255, 0.4);
        }
        
        .terminal-text {
            font-family: 'Courier New', monospace;
            color: #00ff00;
            text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            background: #00ff00;
            border-radius: 50%;
            margin-right: 10px;
            animation: statusBlink 2s ease-in-out infinite;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.7);
        }
        
        @keyframes statusBlink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        
        .bookmarklet-section {
            background: rgba(255, 255, 0, 0.1);
            border: 1px solid rgba(255, 255, 0, 0.3);
            border-radius: 15px;
            padding: 25px;
            margin: 30px 0;
        }
        
        .bookmarklet-link {
            display: inline-block;
            background: linear-gradient(45deg, #ffff00, #ff8000);
            color: #000;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 20px;
            font-weight: 600;
            margin: 10px;
            transition: all 0.3s ease;
        }
        
        .bookmarklet-link:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(255, 255, 0, 0.4);
        }
        
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(45deg, rgba(0, 255, 255, 0.9), rgba(0, 255, 0, 0.9));
            color: #000;
            padding: 15px 25px;
            border-radius: 10px;
            font-family: 'Orbitron', monospace;
            font-weight: 600;
            z-index: 10000;
            box-shadow: 0 10px 30px rgba(0, 255, 255, 0.3);
            animation: slideIn 0.5s ease-out;
            max-width: 300px;
            word-wrap: break-word;
        }
        
        @keyframes slideIn {
            from { transform: translateX(400px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(400px); opacity: 0; }
        }
        
        @media (max-width: 768px) {
            h1 { font-size: 2.5em; }
            .control-center { flex-direction: column; align-items: center; }
            .cyber-btn { width: 80%; max-width: 300px; }
            .ai-grid { grid-template-columns: 1fr; }
        }
        '''
        return css
    
    def get_javascript(self):
        """Get JavaScript code"""
        js = '''
        function launchAllSystems() {
            const btn = event.target;
            const originalText = btn.innerHTML;
            btn.innerHTML = '🚀 Launching Systems...';
            btn.disabled = true;
            
            fetch('/open-all')
                .then(response => response.json())
                .then(data => {
                    btn.innerHTML = '✅ Systems Launched!';
                    btn.style.background = 'linear-gradient(45deg, #00ff00, #80ff00)';
                    btn.style.color = '#000';
                    
                    showCyberNotification('🚀 All AI systems opened! Use the bookmarklet to inject prompts.');
                    
                    setTimeout(() => {
                        btn.innerHTML = originalText;
                        btn.disabled = false;
                        btn.style.background = '';
                        btn.style.color = '';
                    }, 5000);
                })
                .catch(error => {
                    console.error('Error:', error);
                    btn.innerHTML = '❌ Launch Failed';
                    setTimeout(() => {
                        btn.innerHTML = originalText;
                        btn.disabled = false;
                    }, 3000);
                });
        }
        
        function copyToClipboard() {
            navigator.clipboard.writeText(promptText)
                .then(() => {
                    showCyberNotification('📋 Prompt copied to clipboard!');
                })
                .catch(() => {
                    const textArea = document.createElement('textarea');
                    textArea.value = promptText;
                    textArea.style.position = 'fixed';
                    textArea.style.opacity = '0';
                    document.body.appendChild(textArea);
                    textArea.select();
                    try {
                        document.execCommand('copy');
                        showCyberNotification('📋 Prompt copied to clipboard!');
                    } catch (err) {
                        showCyberNotification('❌ Failed to copy prompt');
                    }
                    document.body.removeChild(textArea);
                });
        }
        
        function generateBookmarklet() {
            fetch('/get-injection-bookmarklet')
                .then(response => response.json())
                .then(data => {
                    const bookmarkletSection = document.getElementById('bookmarkletSection');
                    const bookmarkletLink = document.getElementById('bookmarkletLink');
                    
                    bookmarkletLink.href = data.bookmarklet;
                    bookmarkletSection.style.display = 'block';
                    
                    showCyberNotification('🔖 Universal bookmarklet generated! Drag it to your bookmarks bar.');
                })
                .catch(error => {
                    console.error('Error:', error);
                    showCyberNotification('❌ Failed to generate bookmarklet');
                });
        }
        
        function showCyberNotification(message) {
            const existingNotifications = document.querySelectorAll('.notification');
            existingNotifications.forEach(n => n.remove());
            
            const notification = document.createElement('div');
            notification.className = 'notification';
            notification.innerHTML = message;
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.style.animation = 'slideOut 0.5s ease-in';
                setTimeout(() => {
                    notification.remove();
                }, 500);
            }, 5000);
        }
        '''
        return js
    
    def start_server(self):
        """Start the HTTP server"""
        try:
            # Create a custom handler factory that includes the checker instance
            handler = partial(CustomHTTPRequestHandler, checker_instance=self)
            
            self.server = HTTPServer(('localhost', self.server_port), handler)
            print(f"✅ Server started at http://localhost:{self.server_port}")
            
            # Open browser
            webbrowser.open(f'http://localhost:{self.server_port}')
            
            # Start server in a separate thread
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            print("🌐 Dashboard opened in browser")
            print("⌨️  Press Ctrl+C to stop the server")
            
            # Keep the main thread alive
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Shutting down server...")
            if self.server:
                self.server.shutdown()
            print("✅ Server stopped")
        except Exception as e:
            print(f"❌ Server error: {e}")
    
    def run(self):
        """Main run method"""
        print("🚀 Enhanced AI Tools Checker v2.0")
        print("=" * 50)
        
        # Read prompt
        if not self.read_prompt():
            print("❌ Failed to load prompt. Exiting...")
            return
        
        print("\n📊 Dashboard Options:")
        print("1. Open web dashboard (recommended)")
        print("2. Open all AI tools directly")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            self.start_server()
        elif choice == '2':
            self.open_all_tools()
            print("\n✅ All AI tools opened!")
            print("💡 Use the generated bookmarklet to inject prompts")
        elif choice == '3':
            print("👋 Exiting...")
        else:
            print("❌ Invalid choice")

def main():
    """Main entry point"""
    checker = EnhancedAIChecker()
    checker.run()

if __name__ == "__main__":
    main()