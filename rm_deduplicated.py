import hashlib
from pathlib import Path
from tqdm import tqdm

def hash_file_content(file_path):
    """Tạo hash từ nội dung file."""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def remove_duplicate_txt_files(folder_path="docs"):
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        print(f"Thư mục '{folder_path}' không tồn tại.")
        return

    seen_hashes = {}
    txt_files = list(folder.glob("*.txt"))
    deleted_count = 0

    for file_path in tqdm(txt_files, desc="Checking for duplicates"):
        file_hash = hash_file_content(file_path)

        if file_hash in seen_hashes:
            # File này trùng với một file đã gặp
            try:
                file_path.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"Lỗi khi xóa {file_path}: {e}")
        else:
            seen_hashes[file_hash] = file_path

    print(f"✅ Đã xóa {deleted_count} file trùng lặp.")

if __name__ == "__main__":
    remove_duplicate_txt_files("docs")
