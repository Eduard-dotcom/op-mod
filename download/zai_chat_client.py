#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Z.ai Chat Client - Lightweight client for old Windows machines
Works with Python 3.4+ and tkinter (included in standard Python distribution)

Usage:
  1. Install Python 3.4+ from python.org (if not already installed)
  2. Get your auth token:
     - Open chat.z.ai in any working browser
     - Press F12 → Console tab
     - Type: localStorage.getItem('token')
     - Copy the resulting string (starts with "eyJ...")
  3. Run this script: python zai_chat_client.py
  4. Paste your token when prompted (or set ZAI_TOKEN env variable)
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import json
import urllib.request
import urllib.error
import ssl
import sys
import os
import threading
import time

# ============================================================
# CONFIGURATION
# ============================================================
BASE_URL = "https://chat.z.ai"
API_V1 = BASE_URL + "/api/v1"
DEFAULT_MODEL = "GLM-5.1"

# Disable SSL verification for old Python versions that might have cert issues
ssl_ctx = ssl.create_default_context()
try:
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
except:
    pass


# ============================================================
# API Client
# ============================================================
class ZaiAPI:
    def __init__(self, token=None):
        self.token = token or os.environ.get("ZAI_TOKEN", "")
        self.chat_id = None
        self.chat_history = []

    def _headers(self):
        h = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Language": "ru-RU",
        }
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def _request(self, method, url, data=None, stream=False):
        """Make HTTP request. Returns response or stream iterator."""
        body = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=body, headers=self._headers(), method=method)

        try:
            resp = urllib.request.urlopen(req, context=ssl_ctx, timeout=60)
            if stream:
                return resp
            return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            try:
                error_json = json.loads(error_body)
                return {"error": error_json.get("detail", str(error_json))}
            except:
                return {"error": f"HTTP {e.code}: {error_body[:200]}"}
        except Exception as e:
            return {"error": str(e)}

    def test_auth(self):
        """Test if the current token is valid."""
        if not self.token:
            return False, "No token provided"
        result = self._request("GET", f"{API_V1}/auths/")
        if "error" in result:
            return False, result["error"]
        return True, f"Logged in as: {result.get('name', 'Unknown')} ({result.get('role', '?')})"

    def create_chat(self, title="Chat"):
        """Create a new chat."""
        result = self._request("POST", f"{API_V1}/chats/new", {"chat": {"title": title}})
        if "error" in result:
            return False, result["error"]
        self.chat_id = result.get("id")
        return True, self.chat_id

    def list_chats(self, page=1):
        """List existing chats."""
        result = self._request("GET", f"{API_V1}/chats/?page={page}")
        if "error" in result:
            return False, result["error"]
        return True, result

    def get_chat(self, chat_id=None):
        """Get chat details."""
        cid = chat_id or self.chat_id
        if not cid:
            return False, "No chat ID set"
        result = self._request("GET", f"{API_V1}/chats/{cid}")
        if "error" in result:
            return False, result["error"]
        return True, result

    def send_message(self, message, stream=True):
        """Send a message and return the response (streaming or not)."""
        if not self.chat_id:
            return False, "No chat ID set. Create or select a chat first."

        self.chat_history.append({"role": "user", "content": message})

        body = {
            "chat": {"id": self.chat_id},
            "model": DEFAULT_MODEL,
            "messages": self.chat_history[-10:],  # Last 10 messages for context
            "stream": stream,
            "params": {},
            "features": {
                "web_search": False,
                "auto_web_search": False,
                "image_generation": False,
            },
        }

        if stream:
            return self._stream_message(body)
        else:
            result = self._request("POST", f"{API_V1}/chats/message", body)
            if "error" in result:
                self.chat_history.pop()  # Remove the user message on error
                return False, result["error"]
            return True, result

    def _stream_message(self, body):
        """Stream SSE response from the API."""
        url = f"{API_V1}/chats/message"
        req_data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=req_data, headers=self._headers(), method="POST")

        try:
            resp = urllib.request.urlopen(req, context=ssl_ctx, timeout=120)
            return self._parse_sse(resp)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            self.chat_history.pop()
            try:
                error_json = json.loads(error_body)
                return False, f"HTTP {e.code}: {error_json.get('detail', error_body[:200])}"
            except:
                return False, f"HTTP {e.code}: {error_body[:200]}"
        except Exception as e:
            self.chat_history.pop()
            return False, str(e)

    def _parse_sse(self, resp):
        """Parse Server-Sent Events from streaming response."""
        full_content = ""
        buffer = ""

        def generator():
            nonlocal full_content, buffer
            try:
                while True:
                    chunk = resp.read(4096)
                    if not chunk:
                        break
                    buffer += chunk.decode("utf-8", errors="replace")

                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()

                        if line.startswith("data:"):
                            data_str = line[5:].strip()
                            if data_str == "[DONE]":
                                if full_content:
                                    self.chat_history.append({"role": "assistant", "content": full_content})
                                return
                            try:
                                data = json.loads(data_str)
                                # Handle different SSE event formats
                                content = self._extract_content(data)
                                if content:
                                    full_content += content
                                    yield content
                            except json.JSONDecodeError:
                                pass
            except Exception as e:
                if full_content:
                    self.chat_history.append({"role": "assistant", "content": full_content})
                yield f"\n[Stream error: {str(e)}]"

        return generator()

    def _extract_content(self, data):
        """Extract text content from various SSE data formats."""
        # OpenAI-style format
        if "choices" in data:
            for choice in data.get("choices", []):
                delta = choice.get("delta", {})
                if "content" in delta:
                    return delta["content"]
        # Z.ai custom format
        if "content" in data:
            if isinstance(data["content"], str):
                return data["content"]
        # Message delta format
        if "type" in data:
            if data["type"] in ("message", "chat:message:delta", "chat:message"):
                return data.get("content", "")
        return ""


# ============================================================
# GUI Application
# ============================================================
class ZaiChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Z.ai Chat Client v1.0")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        self.api = ZaiAPI()
        self.streaming = False
        self.assistant_content = ""

        self._build_ui()
        self._check_token()

    def _build_ui(self):
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        chat_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Chat", menu=chat_menu)
        chat_menu.add_command(label="New Chat", command=self._new_chat)
        chat_menu.add_command(label="List Chats", command=self._list_chats)
        chat_menu.add_separator()
        chat_menu.add_command(label="Set Token", command=self._set_token)
        chat_menu.add_separator()
        chat_menu.add_command(label="Exit", command=self.root.quit)

        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            main_frame, wrap=tk.WORD, state=tk.DISABLED,
            font=("Consolas", 10), bg="#1e1e1e", fg="#d4d4d4",
            insertbackground="white"
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.tag_configure("user", foreground="#569cd6")
        self.chat_display.tag_configure("assistant", foreground="#ce9178")
        self.chat_display.tag_configure("system", foreground="#6a9955")
        self.chat_display.tag_configure("error", foreground="#f44747")

        # Input frame
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(5, 0))

        # Model selector
        model_frame = tk.Frame(input_frame)
        model_frame.pack(fill=tk.X)
        tk.Label(model_frame, text="Model:").pack(side=tk.LEFT)
        self.model_var = tk.StringVar(value=DEFAULT_MODEL)
        model_entry = tk.Entry(model_frame, textvariable=self.model_var, width=20)
        model_entry.pack(side=tk.LEFT, padx=5)

        # Chat ID display
        tk.Label(model_frame, text="Chat ID:").pack(side=tk.LEFT, padx=(10, 0))
        self.chat_id_var = tk.StringVar(value="(none)")
        tk.Label(model_frame, textvariable=self.chat_id_var, fg="gray").pack(side=tk.LEFT)

        # Message input
        msg_frame = tk.Frame(input_frame)
        msg_frame.pack(fill=tk.X, pady=(3, 0))

        self.msg_entry = tk.Entry(msg_frame, font=("Consolas", 10))
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.msg_entry.bind("<Return>", self._on_send)
        self.msg_entry.bind("<Shift-Return>", lambda e: None)  # Allow Shift+Enter for newline

        self.send_btn = tk.Button(msg_frame, text="Send", command=self._on_send, width=8)
        self.send_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # Status bar
        self.status_var = tk.StringVar(value="Ready. Set your token: Chat → Set Token")
        status_bar = tk.Label(self.root, textvariable=self.status_var, anchor=tk.W, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def _check_token(self):
        """Check if token is available from environment."""
        token = os.environ.get("ZAI_TOKEN", "")
        if token:
            self.api.token = token
            self._test_connection()

    def _set_token(self):
        """Prompt user for auth token."""
        token = simpledialog.askstring(
            "Set Auth Token",
            "Paste your Z.ai auth token\n\n"
            "How to get it:\n"
            "1. Open chat.z.ai in a browser\n"
            "2. Press F12 → Console\n"
            "3. Type: localStorage.getItem('token')\n"
            "4. Copy the result (starts with eyJ...)",
            parent=self.root
        )
        if token:
            self.api.token = token.strip()
            self._test_connection()

    def _test_connection(self):
        """Test the API connection."""
        self.status_var.set("Testing connection...")
        self.root.update()

        ok, msg = self.api.test_auth()
        if ok:
            self._append_chat(f"✓ Connected: {msg}\n", "system")
            self.status_var.set(f"Connected: {msg}")
        else:
            self._append_chat(f"✗ Connection failed: {msg}\n", "error")
            self.status_var.set(f"Connection failed: {msg}")

    def _new_chat(self):
        """Create a new chat."""
        self.status_var.set("Creating new chat...")
        self.root.update()

        ok, result = self.api.create_chat()
        if ok:
            self.chat_id_var.set(result[:8] + "...")
            self._append_chat(f"✓ New chat created: {result}\n", "system")
            self.status_var.set(f"Chat: {result[:16]}...")
        else:
            self._append_chat(f"✗ Failed to create chat: {result}\n", "error")
            self.status_var.set("Failed to create chat")

    def _list_chats(self):
        """List existing chats."""
        self.status_var.set("Loading chats...")
        self.root.update()

        ok, result = self.api.list_chats()
        if ok and isinstance(result, list):
            if not result:
                self._append_chat("No chats found.\n", "system")
            else:
                self._append_chat(f"Found {len(result)} chats:\n", "system")
                for chat in result[:20]:
                    title = chat.get("title", "Untitled")
                    cid = chat.get("id", "?")
                    self._append_chat(f"  [{cid[:8]}] {title}\n", "system")
        else:
            self._append_chat(f"✗ Failed to list chats: {result}\n", "error")

    def _on_send(self, event=None):
        """Send a message."""
        if self.streaming:
            return

        message = self.msg_entry.get().strip()
        if not message:
            return

        if not self.api.token:
            messagebox.showwarning("No Token", "Please set your auth token first:\nChat → Set Token")
            return

        if not self.api.chat_id:
            # Auto-create chat
            ok, result = self.api.create_chat()
            if ok:
                self.chat_id_var.set(result[:8] + "...")
                self._append_chat(f"✓ Auto-created chat: {result}\n", "system")
            else:
                self._append_chat(f"✗ Failed to create chat: {result}\n", "error")
                return

        # Display user message
        self._append_chat(f"You: {message}\n", "user")
        self.msg_entry.delete(0, tk.END)
        self.msg_entry.config(state=tk.DISABLED)
        self.send_btn.config(state=tk.DISABLED)

        # Send in background thread
        self.streaming = True
        self.assistant_content = ""
        self.status_var.set("Waiting for response...")

        thread = threading.Thread(target=self._send_message_thread, args=(message,), daemon=True)
        thread.start()

    def _send_message_thread(self, message):
        """Send message in background thread."""
        try:
            self.api.model = self.model_var.get() or DEFAULT_MODEL

            # Try streaming first
            result = self.api.send_message(message, stream=True)

            if isinstance(result, tuple):
                # Error or non-streaming response
                ok, data = result
                if ok:
                    self.root.after(0, self._append_chat, f"Assistant: {data}\n\n", "assistant")
                else:
                    self.root.after(0, self._append_chat, f"✗ Error: {data}\n", "error")
            elif hasattr(result, '__next__'):
                # Streaming generator
                self.root.after(0, self._append_chat, "Assistant: ", "assistant")
                for chunk in result:
                    if chunk:
                        self.assistant_content += chunk
                        self.root.after(0, self._update_streaming_content, self.assistant_content)
                self.root.after(0, self._append_chat, "\n\n", "assistant")

        except Exception as e:
            self.root.after(0, self._append_chat, f"\n✗ Error: {str(e)}\n", "error")

        finally:
            self.streaming = False
            self.root.after(0, self._restore_input)

    def _update_streaming_content(self, content):
        """Update the assistant's streaming content in the chat display."""
        self.chat_display.config(state=tk.NORMAL)
        # Find and replace the last assistant message
        # Simple approach: clear from last "Assistant: " marker
        current_text = self.chat_display.get("1.0", tk.END)
        last_idx = current_text.rfind("Assistant: ")
        if last_idx >= 0:
            # Convert to tk index
            line = current_text[:last_idx].count("\n") + 1
            col = last_idx - current_text[:last_idx].rfind("\n") - 1
            start_idx = f"{line}.{col}"
            self.chat_display.delete(start_idx, tk.END)
            self.chat_display.insert(start_idx, f"Assistant: {content}", "assistant")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def _restore_input(self):
        """Re-enable input after response."""
        self.msg_entry.config(state=tk.NORMAL)
        self.send_btn.config(state=tk.NORMAL)
        self.msg_entry.focus_set()
        self.status_var.set("Ready")

    def _append_chat(self, text, tag=None):
        """Append text to the chat display."""
        self.chat_display.config(state=tk.NORMAL)
        if tag:
            self.chat_display.insert(tk.END, text, tag)
        else:
            self.chat_display.insert(tk.END, text)
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)


# ============================================================
# COMMAND-LINE INTERFACE (fallback for no tkinter)
# ============================================================
def cli_mode():
    """Simple command-line interface."""
    api = ZaiAPI()

    print("=" * 60)
    print("  Z.ai Chat Client - Command Line Mode")
    print("=" * 60)
    print()

    # Check token
    token = os.environ.get("ZAI_TOKEN", "")
    if not token:
        print("No ZAI_TOKEN environment variable set.")
        token = input("Paste your auth token: ").strip()
    api.token = token

    # Test auth
    print("Testing connection...")
    ok, msg = api.test_auth()
    if not ok:
        print(f"ERROR: {msg}")
        print("\nHow to get your token:")
        print("  1. Open chat.z.ai in a browser")
        print("  2. Press F12 → Console")
        print("  3. Type: localStorage.getItem('token')")
        print("  4. Copy the result")
        return
    print(f"Connected: {msg}")

    # Create or select chat
    ok, result = api.create_chat()
    if not ok:
        print(f"Failed to create chat: {result}")
        return
    print(f"Chat created: {result}")

    print("\nCommands: /quit to exit, /new for new chat, /list for chat list")
    print("Type your message and press Enter to send.\n")

    while True:
        try:
            message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not message:
            continue
        if message == "/quit":
            print("Goodbye!")
            break
        if message == "/new":
            ok, result = api.create_chat()
            print(f"New chat: {result}" if ok else f"Error: {result}")
            continue
        if message == "/list":
            ok, result = api.list_chats()
            if ok:
                for chat in result[:10]:
                    print(f"  [{chat.get('id', '?')[:8]}] {chat.get('title', '?')}")
            else:
                print(f"Error: {result}")
            continue

        # Send message
        print("Assistant: ", end="", flush=True)
        result = api.send_message(message, stream=True)

        if isinstance(result, tuple):
            ok, data = result
            if ok:
                print(data)
            else:
                print(f"\nError: {data}")
        elif hasattr(result, '__next__'):
            for chunk in result:
                if chunk:
                    print(chunk, end="", flush=True)
            print()
        print()


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    if "--cli" in sys.argv:
        cli_mode()
    else:
        try:
            root = tk.Tk()
            app = ZaiChatApp(root)
            root.mainloop()
        except tk.TclError:
            print("tkinter not available, switching to CLI mode...")
            cli_mode()
