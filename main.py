import os
import zipfile
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from decrypt import decrypt

load_dotenv()

BASE = Path(os.getenv("BASE"))
OUTPUT = Path("assets")
ASSETSTUDIO_CLI = Path("cli/AssetStudioModCLI.exe")

IGNORE_EXTENSIONS = {".db", ".hash", ".bytes"}
IGNORE_FILES = {"BundleRevision"}

FOLDERS = [
    "Audio/BGM",
    "Audio/Videos",
    "PUB/Resource/GameData/MediaResources",
    "PUB/Resource/GameData/TableBundles",
    "PUB/Resource/Preload",
    "Video",
]

count_copied = 0
count_unzipped = 0
count_decrypted = 0
count_failed = 0
count_skipped = 0
count_bundle = 0


def extract_zip(zip_path: Path, dest_dir: Path):
    global count_unzipped, count_decrypted, count_failed
    try:
        with zipfile.ZipFile(zip_path, "r") as zip:
            test_info = zip.infolist()[0]
            try:
                zip.read(test_info)
                zip.extractall(dest_dir)
                print(f"UnZip：{zip_path.relative_to(BASE)}")
                count_unzipped += 1
            except RuntimeError:
                password = decrypt(zip_path.name)
                zip.extractall(dest_dir, pwd=password.encode())
                print(f"Decrypt：{zip_path.relative_to(BASE)}")
                count_decrypted += 1
    except Exception as e:
        print(f"Failed：{zip_path.relative_to(BASE)} -> {e}")
        count_failed += 1


def extract_bundle(bundle_path: Path, output_dir: Path):
    global count_bundle, count_failed
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                str(ASSETSTUDIO_CLI),
                str(bundle_path),
                "-o",
                str(output_dir),
                "-t",
                "all",
            ],
            check=True,
        )
        print(f"Bundle：{bundle_path.relative_to(BASE)}")
        count_bundle += 1
    except Exception as e:
        print(f"Failed：{bundle_path.relative_to(BASE)} (bundle) -> {e}")
        count_failed += 1


def copy_file(path: Path, dest: Path):
    global count_copied, count_failed
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(path.read_bytes())
        print(f"Copy：{path.relative_to(BASE)}")
        count_copied += 1
    except Exception as e:
        print(f"Failed：{path.relative_to(BASE)} -> {e}")
        count_failed += 1


def process_folder(folder: Path):
    global count_skipped
    for root, _, files in os.walk(folder):
        for file in files:
            path = Path(root) / file
            relative_path = path.relative_to(BASE)

            if path.suffix.lower() in IGNORE_EXTENSIONS or file in IGNORE_FILES:
                count_skipped += 1
                continue

            if path.suffix.lower() == ".zip":
                dest = OUTPUT / relative_path.with_suffix("")
                extract_zip(path, dest)

            elif path.suffix.lower() == ".bundle":
                dest = OUTPUT / relative_path.with_suffix("")
                extract_bundle(path, dest)

            else:
                dest = OUTPUT / relative_path
                copy_file(path, dest)


def main():
    for folder in FOLDERS:
        folder_path = BASE / folder
        if folder_path.exists():
            process_folder(folder_path)
        else:
            print(f"Skip  跳過不存在資料夾：{folder_path}")

    print("\n--- 統計結果 ---")
    print(f"複製成功：{count_copied}")
    print(f"解壓成功：{count_unzipped}")
    print(f"解密解壓：{count_decrypted}")
    print(f"Bundle解包：{count_bundle}")
    print(f"略過檔案：{count_skipped}")
    print(f"失敗處理：{count_failed}")


if __name__ == "__main__":
    main()
