#!/bin/bash
# Bismillaahirrahmaanirrahiim
# Author: @A.RAHMAT-x4s
# Deskripsi: Script pembuat repository otomatis dari Terminal Debian Proot

REPO_NAME="AIbashira-Core"
GITHUB_USER="raahmatrahmat"

echo -e "\e[96m[1/4] Memastikan Git Initialized...\e[0m"
git init

echo -e "\e[96m[2/4] Membuat Repository di GitHub via GH-CLI...\e[0m"
# Mencoba membuat repo di cloud langsung dari terminal
gh repo create $GITHUB_USER/$REPO_NAME --public --source=. --remote=origin --push

# Fallback jika repo sudah ada atau gagal dibuat
if [ $? -ne 0 ]; then
    echo -e "\e[91m[!] Repo mungkin sudah ada, mencoba menghubungkan ulang...\e[0m"
    git remote remove origin 2>/dev/null
    git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
fi

echo -e "\e[96m[3/4] Konfigurasi Branch Utama...\e[0m"
git branch -M main

echo -e "\e[96m[4/4] Sinkronisasi Final...\e[0m"
git add .
git commit -m "Bismillaah: Finalizing GitHub Setup" || echo "[INFO] Nothing new to commit."
git push -u origin main

echo -e "\e[92m[SUCCESS] Repository $REPO_NAME telah aktif dan terhubung!\e[0m"
echo -e "\e[93m[INFO] Sekarang jalankan: python executor_v3.py (Jika belum berjalan)\e[0m"
