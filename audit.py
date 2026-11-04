import os
import shutil

project_root = os.getcwd()
expected_files = {
    "config.py": "cortex-brain",
    "main.py": "cortex-brain",
    "requirements.txt": "cortex-brain"
}

print("🔍 Scanning Cortex workspace with Python...")

for file, target_dir in expected_files.items():
    target_folder = os.path.join(project_root, target_dir)
    correct_path = os.path.join(target_folder, file)
    misplaced_path = os.path.join(project_root, file)

    if os.path.exists(correct_path):
        print(f"✔️ '{file}' is correctly placed.")
    elif os.path.exists(misplaced_path):
        print(f"⚠️ Misplacement detected: '{file}' is in root. Moving it...")
        os.makedirs(target_folder, exist_ok=True)
        shutil.move(misplaced_path, correct_path)
        print(f"✅ Restored '{file}' to '{target_dir}'.")
    else:
        print(f"❌ Warning: '{file}' could not be found anywhere.")

print("✨ Audit complete!")