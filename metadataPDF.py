from pypdf import PdfReader

# Minta input nama file dari pengguna
filename = input("Masukkan nama file PDF (contoh: contoh.pdf): ")

try:
    # Buka file PDF
    with open(filename, 'rb') as file:
        reader = PdfReader(file)
        
        # Akses informasi dokumen (metadata)
        metadata = reader.metadata
        
        if metadata:
            print("Metadata PDF:")
            print(f"Judul: {metadata.title}")
            print(f"Penulis: {metadata.author}")
            print(f"Tanggal Pembuatan: {metadata.creation_date}")
            print(f"Produsen: {metadata.producer}")
            print(f"Subjek: {metadata.subject}")
        else:
            print("Tidak ada metadata yang ditemukan.")
except FileNotFoundError:
    print(f"File '{filename}' tidak ditemukan. Pastikan nama file benar dan file ada di direktori yang sama.")
except Exception as e:
    print(f"Terjadi error saat memproses file: {e}")

