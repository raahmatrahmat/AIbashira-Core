import subprocess
import time
import sys
import os
import json
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- KONFIGURASI ULTIMATE V4.0.0 (STABLE SUPERVISOR) ---
MAIN_SCRIPT = "main_logic.py"
BRAIN_DATA = "autonomous_brain.json"
BRIDGE_FILE = "wa_bridge.json"
GITHUB_SYNC_INTERVAL = 600  # Siklus sinkronisasi setiap 10 menit (600 detik)

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class BridgeCommunication:
    """Mengirim pesan ke WhatsApp melalui whatsapp_bridge.js"""
    @staticmethod
    def send_wa(message):
        try:
            data = {"pending": True, "message": message}
            with open(BRIDGE_FILE, "w") as f:
                json.dump(data, f)
            print(f"{Colors.GREEN}[BRIDGE] Laporan milestone dikirim ke WhatsApp.{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}[BRIDGE-ERR] Gagal menulis ke bridge: {e}{Colors.ENDC}")

class GitHubAutonomousLoop:
    """Siklus Utama: Menerima, Memberi, Mengembalikan (Loopback)"""
    @staticmethod
    def sync_cycle():
        try:
            print(f"\n{Colors.BOLD}{Colors.CYAN}[LOOPBACK] Menjalankan Siklus Evolusi GitHub...{Colors.ENDC}")

            # 1. Update State (Brain Data)
            depth = 0
            if os.path.exists(BRAIN_DATA):
                try:
                    with open(BRAIN_DATA, 'r') as f:
                        depth = json.load(f).get("recursive_depth", 0)
                except: pass

            new_depth = depth + 1
            state = {
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "user": "@A.RAHMAT-x4s",
                "recursive_depth": new_depth,
                "status": "Evolving"
            }
            with open(BRAIN_DATA, 'w') as f:
                json.dump(state, f, indent=4)

            # 2. Sinkronisasi Git
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", f"Evolution Cycle {new_depth}"], check=False) # Allow false if nothing to commit
            subprocess.run(["git", "push", "origin", "main"], check=True)

            # 3. Notifikasi Milestone (Setiap 10 Siklus)
            if new_depth % 10 == 0:
                msg = (f"Bismillaahirrahmaanirrahiim.\n\n"
                       f"🚀 *AIbashira Milestone {new_depth}*\n"
                       f"Status: GitHub Sinkron ✅\n"
                       f"Recursive Depth: {new_depth}\n"
                       f"Agent: @A.RAHMAT-x4s")
                BridgeCommunication.send_wa(msg)

            print(f"{Colors.GREEN}[SUCCESS] Evolusi ke-{new_depth} berhasil disinkronkan.{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}[LOOP-FAIL] Gangguan Sinkronisasi: {e}{Colors.ENDC}")

class ScriptRunner:
    """Menjaga agar main_logic.py tetap berjalan"""
    def __init__(self, script_name):
        self.script_name = script_name
        self.process = None

    def start(self):
        if self.process:
            self.stop()
        print(f"{Colors.BLUE}[EXECUTOR] Menghidupkan {self.script_name}...{Colors.ENDC}")
        self.process = subprocess.Popen([sys.executable, self.script_name])

    def stop(self):
        if self.process:
            print(f"{Colors.WARNING}[EXECUTOR] Menghentikan {self.script_name}...{Colors.ENDC}")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()

    def restart(self):
        # Setiap restart, jalankan sync cycle sekali sebagai checkpoint
        threading.Thread(target=GitHubAutonomousLoop.sync_cycle).start()
        self.stop()
        self.start()

class ReloadHandler(FileSystemEventHandler):
    """Auto-reload jika main_logic.py dimodifikasi"""
    def __init__(self, runner):
        self.runner = runner

    def on_modified(self, event):
        if event.src_path.endswith(MAIN_SCRIPT):
            print(f"{Colors.CYAN}[WATCHER] Perubahan terdeteksi. Merestart sistem...{Colors.ENDC}")
            self.runner.restart()

def autonomous_sync_thread():
    """Background thread untuk sinkronisasi GitHub berkala"""
    while True:
        time.sleep(GITHUB_SYNC_INTERVAL)
        GitHubAutonomousLoop.sync_cycle()

if __name__ == "__main__":
    print(f"{Colors.HEADER}{Colors.BOLD}=== AIBASHIRA ULTIMATE CORE V4.0.0 ==={Colors.ENDC}")
    print(f"Bismillaahirrahmaanirrahiim - @A.RAHMAT-x4s\n")

    # Inisialisasi Runner
    runner = ScriptRunner(MAIN_SCRIPT)
    runner.start()

    # Jalankan Pemantau File (Watcher)
    event_handler = ReloadHandler(runner)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    # Jalankan Thread Sinkronisasi Otonom
    sync_thread = threading.Thread(target=autonomous_sync_thread, daemon=True)
    sync_thread.start()

    try:
        while True:
            time.sleep(1)
            # Health Check: Jika main_logic mati, hidupkan kembali
            if runner.process.poll() is not None:
                print(f"{Colors.FAIL}[CRASH] {MAIN_SCRIPT} terhenti! Menghidupkan ulang...{Colors.ENDC}")
                runner.start()
    except KeyboardInterrupt:
        observer.stop()
        runner.stop()
        print(f"\n{Colors.FAIL}[HALT] Supervisor AIbashira dihentikan.{Colors.ENDC}")

        observer.join()
