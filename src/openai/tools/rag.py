import os
import hashlib
import pandas as pd
from crewai_tools import CSVSearchTool
from dotenv import load_dotenv

load_dotenv()

def hash_file(filepath):
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def batch_load_csv(tool, csv_path, batch_size=100):
    flag_dir = ".added_flags"
    os.makedirs(flag_dir, exist_ok=True)

    csv_hash = hash_file(csv_path)
    flag_file = os.path.join(flag_dir, f"{csv_hash}.flag")

    if os.path.exists(flag_file):
        print(f"⏩ Skip: {csv_path} sudah pernah di-add.")
        return

    df = pd.read_csv(csv_path)
    for i in range(0, len(df), batch_size):
        temp = df.iloc[i:i+batch_size]
        temp_path = f"temp_batch_{i}.csv"
        temp.to_csv(temp_path, index=False)

        try:
            tool.add(temp_path)
            print(f"✅ Batch {i}-{i+batch_size} berhasil ditambahkan.")
        except Exception as e:
            print(f"❌ Gagal tambah batch {i}-{i+batch_size}: {e}")
        finally:
            os.remove(temp_path)

    with open(flag_file, "w") as f:
        f.write("added")
    print(f"🏁 Selesai add: {csv_path}")

# Inisialisasi tools
data_penyakit = CSVSearchTool()
data_obat = CSVSearchTool()
# Search_tool = WebsiteSearchTool()

# Jalankan
batch_load_csv(data_penyakit, "data_penyakit_alodokter_cleaned.csv")
batch_load_csv(data_obat, "data_obat_final_updated.csv")
