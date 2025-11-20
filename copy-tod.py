import os
import shutil
import pandas as pd
from tkinter import Tk, filedialog

log_file = "not_found_log.txt"

with open(log_file, "w", encoding="utf-8") as log:
    log.write("=== LOG NOT FOUND ===\n\n")

# -----------------------------
# 1. MINTA FILE EXCEL
# -----------------------------
print("Silakan pilih file Excel...")
Tk().withdraw()
excel_path = filedialog.askopenfilename(title="Pilih File Excel", filetypes=[("Excel Files", "*.xlsx *.xls")])

if not excel_path:
    print("Tidak ada file dipilih. Program berhenti.")
    exit()

print(f"File Excel dipilih: {excel_path}")

# -----------------------------
# 2. LOAD DATA & AMBIL KOLOM F (6 DIGIT PERTAMA PO)
# -----------------------------
df = pd.read_excel(excel_path)

po_series = df.iloc[:, 5].astype(str).str[:6]   # kolom F → 6 digit pertama
po_list = po_series.dropna().unique().tolist()

print("\nPO Number (6 digit):")
for po in po_list:
    print(" -", po)

# -----------------------------
# 3. TIGA PATH FOLDER
# -----------------------------
path_candidates = [
    "\\\\192.168.20.95\\sharing 2\\Folder Amoy\\P-LIST\\2025",
    "\\\\192.168.20.95\\sharing 2\\Folder Amoy\\Alfredo\\P-LIST",
    "\\\\192.168.20.95\\sharing 2\\Folder Amoy\\ERISNA\\P-LIST MANUAL"
]

# -----------------------------
# 4. CARI FOLDER YANG MENGANDUNG PO (SUBSTRING)
# -----------------------------
found_folders = {}

print("\nMencari folder yang mengandung PO Number...")

for po in po_list:
    folder_found = None

    for base_path in path_candidates:
        if not os.path.isdir(base_path):
            continue

        for folder_name in os.listdir(base_path):
            full_path = os.path.join(base_path, folder_name)

            if os.path.isdir(full_path) and po in folder_name:
                folder_found = full_path
                break

        if folder_found:
            break

    if folder_found:
        print(f"[FOUND] {po} → {folder_found}")
        found_folders[po] = folder_found
    else:
        print(f"[NOT FOUND] {po}")
        with open(log_file, "a", encoding="utf-8") as log:
            log.write(f"PO NOT FOUND : {po}\n")

if not found_folders:
    print("\nTidak ada folder PO ditemukan.")
    exit()

# -----------------------------
# 5. INPUT TOD
# -----------------------------
tod = input("\nMasukkan nama TOD (subfolder): ")
# -----------------------------
# 6. CARI SUBFOLDER TOD (IGNORE SPACES)
# -----------------------------
all_found_files = []

print("\nMencari subfolder TOD...\n")

tod_clean = tod.replace(" ", "")  # Hapus spasi dari input TOD

for po, folder in found_folders.items():
    tod_folder_found = None

    for folder_name in os.listdir(folder):
        full_path = os.path.join(folder, folder_name)

        if os.path.isdir(full_path):
            # Hapus semua spasi di nama folder saat pencocokan
            folder_clean = folder_name.replace(" ", "")

            # Bandingkan tanpa spasi
            if tod_clean in folder_clean:
                tod_folder_found = full_path
                break

    if tod_folder_found:
        print(f"[FOUND TOD] {tod_folder_found}")

        files = [os.path.join(tod_folder_found, f) for f in os.listdir(tod_folder_found)]
        for f in files:
            print(" -", f)
            all_found_files.append(f)
    else:
        print(f"[TOD NOT FOUND] (yang mengandung '{tod}' / ignore space) di {folder}")
        with open(log_file, "a", encoding="utf-8") as log:
            log.write(f"TOD NOT FOUND for PO {po} : {tod}\n")

if not all_found_files:
    print("\nTidak ada file ditemukan.")
    exit()

# -----------------------------
# 7. KONFIRMASI COPY FILE
# -----------------------------
confirm = input("\nCopy file ke folder baru? (y/n): ").lower()

if confirm != "y":
    print("Copy dibatalkan.")
    exit()

# -----------------------------
# 8. PILIH FOLDER TUJUAN
# -----------------------------
print("\nPilih folder tujuan...")
target_dir = filedialog.askdirectory(title="Pilih Folder Tujuan")

if not target_dir:
    print("Tidak ada folder dipilih.")
    exit()

# -----------------------------
# 9. COPY FILE
# -----------------------------
print("\nMenyalin file...\n")

for f in all_found_files:
    try:
        shutil.copy(f, target_dir)
        print(f"[COPIED] {os.path.basename(f)}")
    except Exception as e:
        print(f"[FAILED] {f} → {e}")

print("\nSelesai! Semua file berhasil disalin.")

# -----------------------------
# 10. AUTO-OPEN LOG FILE
# -----------------------------
print("\nMembuka file log...")

try:
    os.startfile(log_file)  # Windows
except:
    try:
        os.system(f"xdg-open '{log_file}'")  # Linux
    except:
        os.system(f"open '{log_file}'")  # MacOS

print("Log file terbuka.")