#!/usr/bin/env python3
import asyncio
import asyncssh
import sys
import logging
from datetime import datetime
import os

HOST = "0.0.0.0"
PORT = 2222
AUTHORIZED_KEYS_DIR = "authorized_keys"
CHAT_LOG_DIR = "chat_logs"

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("log-chat")

# Global state
SESSIONS = set()
ROOMS = {"general": set()}  # room_name -> set(ChatSession)
SESSIONS_LOCK = asyncio.Lock()
ROOMS_LOCK = asyncio.Lock()
os.makedirs(CHAT_LOG_DIR, exist_ok=True)

# ANSI Cyberpunk colors
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    BLINK = "\033[5m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

# Formatting helpers
def format_system(msg):
    return f"{Colors.CYAN}{Colors.BOLD}[SYSTEM]{Colors.RESET} {msg}"

def format_user(ts, user, msg):
    return f"{Colors.CYAN}⌁[{ts}]{Colors.RESET} {Colors.MAGENTA}{user}{Colors.RESET}: {Colors.YELLOW}{msg}{Colors.RESET}"

def format_dm(ts, sender, target, msg):
    return f"{Colors.CYAN}⌁[{ts}]{Colors.RESET} (DM) {Colors.MAGENTA}{sender}{Colors.RESET} -> {Colors.MAGENTA}{target}{Colors.RESET}: {Colors.YELLOW}{msg}{Colors.RESET}"

# Log chat lines to file per room
def log_chat_line(room: str, line: str):
    try:
        path = os.path.join(CHAT_LOG_DIR, f"{room}.log")
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

async def send_to_session(sess, msg: str):
    try:
        sess._chan.write(msg + "\n")
    except:
        pass

async def broadcast_room(room: str, sender: str, message: str):
    ts = datetime.utcnow().strftime("%H:%M:%S")
    if sender == "SYSTEM":
        formatted = format_system(message)
    else:
        formatted = format_user(ts, sender, message)

    log_chat_line(room, f"[{ts}] {sender}: {message}")

    async with ROOMS_LOCK:
        users = list(ROOMS.get(room, []))

    for sess in users:
        await send_to_session(sess, formatted)

async def send_private(sender: str, target: str, message: str):
    ts = datetime.utcnow().strftime("%H:%M:%S")
    formatted = format_dm(ts, sender, target, message)

    async with SESSIONS_LOCK:
        for sess in SESSIONS:
            if sess.username == target:
                await send_to_session(sess, formatted)
                await send_to_session(sess, f"{Colors.CYAN}(DM SENT){Colors.RESET} to {target}")
                return True
    return False

# ---------------- Chat Session ----------------
class ChatSession(asyncssh.SSHServerSession):
    def __init__(self, username):
        self.username = username
        self._chan = None
        self._buf = ""
        self.room = "general"

    def connection_made(self, chan):
        self._chan = chan

    def connection_lost(self, exc):
        asyncio.create_task(self.leave_room())

    async def leave_room(self):
        async with ROOMS_LOCK:
            if self.room in ROOMS and self in ROOMS[self.room]:
                ROOMS[self.room].remove(self)
                await broadcast_room(self.room, "SYSTEM", f"{self.username} has left the room.")

    def data_received(self, data, datatype):
        self._buf += data
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            line = line.strip()
            if not line:
                continue

            # Handle commands
            if line.startswith("/"):
                asyncio.create_task(self.handle_command(line))
            else:
                asyncio.create_task(broadcast_room(self.room, self.username, line))

    async def handle_command(self, line: str):
        args = line.split()
        cmd = args[0].lower()

        if cmd == "/join":
            if len(args) < 2:
                await send_to_session(self, "Usage: /join <room>")
                return
            new_room = args[1]
            async with ROOMS_LOCK:
                if self.room in ROOMS and self in ROOMS[self.room]:
                    ROOMS[self.room].remove(self)
                    await broadcast_room(self.room, "SYSTEM", f"{self.username} has left the room.")
                if new_room not in ROOMS:
                    ROOMS[new_room] = set()
                ROOMS[new_room].add(self)
                self.room = new_room
                await send_to_session(self, f"You joined room: {new_room}")
                await broadcast_room(new_room, "SYSTEM", f"{self.username} has joined the room.")

        elif cmd == "/leave":
            if self.room == "general":
                await send_to_session(self, "You are already in general room.")
                return
            async with ROOMS_LOCK:
                if self.room in ROOMS and self in ROOMS[self.room]:
                    ROOMS[self.room].remove(self)
                    await broadcast_room(self.room, "SYSTEM", f"{self.username} has left the room.")
                ROOMS["general"].add(self)
                self.room = "general"
                await send_to_session(self, "You returned to general room.")
                await broadcast_room("general", "SYSTEM", f"{self.username} joined general room.")

        elif cmd == "/rooms":
            async with ROOMS_LOCK:
                rooms_list = list(ROOMS.keys())
            await send_to_session(self, "Active rooms: " + ", ".join(rooms_list))

        elif cmd == "/who":
            async with ROOMS_LOCK:
                users_list = [s.username for s in ROOMS.get(self.room, [])]
            await send_to_session(self, f"Users in {self.room}: " + ", ".join(users_list))

        elif cmd == "/msg":
            if len(args) < 3:
                await send_to_session(self, "Usage: /msg <username> <text>")
                return
            target_user = args[1]
            message = " ".join(args[2:])
            ok = await send_private(self.username, target_user, message)
            if not ok:
                await send_to_session(self, f"User {target_user} not found.")

        else:
            await send_to_session(self, "Unknown command: " + cmd)

# ---------------- Public Key Auth ----------------
def load_user_authorized_keys(username):
    path = os.path.join(AUTHORIZED_KEYS_DIR, f"{username}.pub")
    if not os.path.exists(path):
        return []
    keys = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    keys.append(asyncssh.public_key_from_str(line))
    except Exception as e:
        print("Failed loading key:", e)
    return keys

# ---------------- SSH Handler ----------------
class SSHHandler(asyncssh.SSHServer):
    def __init__(self):
        self._username = None

    def begin_auth(self, username):
        self._username = username
        return True

    def public_key_auth_supported(self):
        return True

    def validate_public_key(self, username, key):
        allowed = load_user_authorized_keys(username)
        return key in allowed

    def session_requested(self):
        return True

    def shell_requested(self):
        return True

    async def create_server_session(self, conn, chan):
        username = conn.get_extra_info("username")
        sess = ChatSession(username)
        sess._chan = chan

        # Join general room
        async with ROOMS_LOCK:
            ROOMS["general"].add(sess)
        async with SESSIONS_LOCK:
            SESSIONS.add(sess)

        # Cyberpunk header
        header = f"""
{Colors.MAGENTA}╔═════════════════════════════════════════╗{Colors.RESET}
{Colors.MAGENTA}║  Welcome, {username:<20}                ║{Colors.RESET}
{Colors.MAGENTA}╚═════════════════════════════════════════╝{Colors.RESET}
"""
        await send_to_session(sess, header)
        await send_to_session(sess, format_system("Default room: general"))
        await send_to_session(sess, format_system("Commands: /join /leave /rooms /who /msg <user> <text>"))
        await broadcast_room(sess.room, "SYSTEM", f"{username} joined the room.")

        return sess

# ---------------- Main ----------------
async def start_server():
    server = await asyncssh.create_server(
        lambda: SSHHandler(),
        HOST, PORT,
        server_host_keys=None,
        authorized_client_keys=None
    )
    print(f"[OK] Chat running on port {PORT}")
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(start_server())
    except KeyboardInterrupt:
        print("Server stopped.")
        sys.exit(0)
