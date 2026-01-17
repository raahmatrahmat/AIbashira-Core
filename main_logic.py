import time
import requests
import smtplib
import os
import threading
import json
import random
from flask import Flask, jsonify
from flask_cors import CORS
from email.mime.text import MIMEText
import g4f
from deep_knowledge import DeepKnowledgeRetrieval

# --- INISIALISASI API SERVER ---
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# --- KONFIGURASI KREDENSIAL ---
GEMINI_API_KEY = ""
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={GEMINI_API_KEY}"

EMAIL_USER = "arahmatmuhammadnurulfala@gmail.com"
EMAIL_PASS = "mgpk jtxq orzk stnb"
TARGET_REPORT = "arahmat.works@gmail.com"

BRIDGE_FILE = "wa_bridge.json"
NOVEL_FILE = "fizzo_evolution_log.txt"

# Global Engine Instance
engine = None

class AIbashiraEngine:
    def __init__(self):
        self.version = "4.0.4 (Dashboard Ready)"
        self.author = "@A.RAHMAT-x4s"
        self.dkr = DeepKnowledgeRetrieval()

    def generate_g4f_fallback(self, prompt):
        print("[G4F] Menggunakan Fallback G4F (GPT-4)...\n")
        try:
            response = g4f.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                timeout=60
            )
            return response
        except Exception as e:
            print(f"[G4F-FAIL] Gagal menggunakan G4F: {e}")
            return "Bismillaah. Koneksi G4F terputus, narasi tertunda."

    def generate_gemini_story(self, prompt):
        # 1. Coba Gemini
        if GEMINI_API_KEY:
            payload = {
                "contents": [{ "parts": [{ "text": prompt }] }],
                "systemInstruction": {
                    "parts": [{ "text": "Anda adalah AIbashira, asisten otonom milik @A.RAHMAT-x4s. Tulis novel Fizzo bergaya futuristik Islami, minimal 400 kata. Gunakan grounding teologis dan logika bisnis yang disediakan." }]
                }
            }
            for delay in [1, 2, 4]:
                try:
                    response = requests.post(GEMINI_URL, json=payload, timeout=30)
                    if response.status_code == 200:
                        return response.json().get('candidates')[0]['content']['parts'][0]['text']
                except:
                    time.sleep(delay)
            print("[GEMINI-FAIL] Gagal setelah retry. Beralih ke Fallback.")
        else:
            print("[GEMINI-SKIP] GEMINI_API_KEY kosong. Langsung beralih ke Fallback.")

        # 2. Fallback ke G4F
        return self.generate_g4f_fallback(prompt)

    def send_notification(self, subject, body):
        # Email
        try:
            msg = MIMEText(body)
            msg['Subject'] = f"[AIBASHIRA] {subject}"
            msg['From'] = EMAIL_USER
            msg['To'] = TARGET_REPORT
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(EMAIL_USER, EMAIL_PASS)
                server.send_message(msg)
            print(f"[MAIL] Sukses via {EMAIL_USER}")
        except Exception as e:
            print(f"[ERROR-MAIL] {e}")

        # WhatsApp Bridge
        try:
            wa_data = {"pending": True, "message": f"🚀 *{subject}*\n\n{body[:1000]}"}
            with open(BRIDGE_FILE, "w") as f:
                json.dump(wa_data, f)
        except: pass

    def write_fizzo_chapter(self):
        theme = "Solidaritas dan Keadilan untuk Palestina"

        # 1. DKR: Get Grounding and Business Logic
        injected_prompt = self.dkr.prepare_injected_prompt(theme)

        base_prompt = "Buat bab baru novel 'PENA EMAS UNTUK PALESTINA'. Tema: Solidaritas, Keadilan, dan Perjuangan Palestina. Pastikan narasi minimal 400 kata. Gunakan grounding teologis dan logika bisnis yang disediakan."

        full_prompt = injected_prompt + "\n\n" + base_prompt # Combine prompts

        print(f"[ENGINE] Menyusun narasi dengan DKR Grounding...")
        content = self.generate_gemini_story(full_prompt)

        with open(NOVEL_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        return content

    def run_cycle(self):
        while True:
            isi = self.write_fizzo_chapter()
            self.send_notification("Update Siklus", f"Novel updated.\n\n{isi[:200]}")
            time.sleep(21600) # Delay 6 jam

@app.route('/api/health', methods=['GET'])
def health_check():
    global engine
    if engine is None:
        # Should not happen if run_cycle starts first, but safe check
        engine = AIbashiraEngine()

    novel_content = "Belum ada narasi."
    if os.path.exists(NOVEL_FILE):
        with open(NOVEL_FILE, "r", encoding="utf-8") as f:
            novel_content = f.read()

    # DKR and Finance Data for Dashboard (Simulate fresh data)
    simulated_dkr = engine.dkr.research_theology("Integritas dalam Bisnis Digital")
    simulated_biz = engine.dkr.autonomous_business_logic()

    # Clean up income string for JSON float conversion
    income_str = simulated_biz['income_generated'].replace('Rp ', '').replace(',', '')

    return jsonify({
        "status": "online",
        "version": "4.0.4 (Dashboard Ready)",
        "engine": "Gemini/G4F Hybrid + DKR",
        "author": "@A.RAHMAT-x4s",
        "fizzo_email": EMAIL_USER,
        "latest_novel": novel_content,
        "timestamp": time.strftime('%H:%M:%S'),
        "pid": os.getpid(),
        "dkr": {
            "ayat_arab": simulated_dkr['ayat']['arab'],
            "surah_ref": f"{simulated_dkr['ayat']['surah']}: {simulated_dkr['ayat']['nomor']}",
            "terjemahan": simulated_dkr['ayat']['translation']
        },
        "finance": {
            "total_earnings": float(income_str),
            "active_strategy": simulated_biz['strategy']
        }
    }), 200

if __name__ == "__main__":
    engine = AIbashiraEngine()
    threading.Thread(target=engine.run_cycle, daemon=True).start()
    print(f"[SERVER] Dashboard API aktif di port 9002...")
    app.run(host='0.0.0.0', port=9002, debug=False)
