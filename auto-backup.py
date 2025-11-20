import os
import shutil
from datetime import datetime

# Folder sumber & folder tujuan backup
source_folder = input("path yg akan di backup: ")
backup_root   = input("Nama folder backup: ")

try:
    # ────────────────────────────────────────────────
    # 1. Cek apakah folder sumber ada
    # ────────────────────────────────────────────────
    if not os.path.exists(source_folder):
        raise FileNotFoundError(f"Folder sumber '{source_folder}' tidak ditemukan!")

    # ────────────────────────────────────────────────
    # 2. Buat folder backup root (jika belum ada)
    # ────────────────────────────────────────────────
    os.makedirs(backup_root, exist_ok=True)

    # ────────────────────────────────────────────────
    # 3. Buat folder backup berdasarkan timestamp
    # ────────────────────────────────────────────────
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_folder = os.path.join(backup_root, timestamp)

    try:
        os.makedirs(backup_folder)
    except PermissionError:
        raise PermissionError("Tidak punya izin untuk membuat folder backup!")

    # Path final hasil backup
    dest_path = os.path.join(backup_folder, "data_backup")

    # ────────────────────────────────────────────────
    # 4. Copy isi folder
    # ────────────────────────────────────────────────
    try:
        shutil.copytree(source_folder, dest_path)
    except shutil.Error as e:
        raise RuntimeError(f"Terjadi error saat menyalin file: {e}")
    except PermissionError:
        raise PermissionError("Tidak punya izin membaca atau menulis file!")
    except Exception as e:
        raise RuntimeError(f"Error tidak diketahui ketika backup: {e}")

    # ────────────────────────────────────────────────
    # 5. Jika selesai
    # ────────────────────────────────────────────────
    print("Backup berhasil!")
    print(f"Folder sumber  : {source_folder}")
    print(f"Folder backup  : {dest_path}")

# ────────────────────────────────────────────────
# Bagian umum untuk error handling
# ────────────────────────────────────────────────
except FileNotFoundError as e:
    print(f"[ERROR] {e}")

except PermissionError as e:
    print(f"[ERROR] {e}")

except Exception as e:
    print(f"[ERROR] Terjadi kesalahan tidak terduga: {e}")
