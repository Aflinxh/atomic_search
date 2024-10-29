import os
import shutil

def delete_folder(folder_path):
    """Delete a folder and its contents."""
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f"Deleted folder: {folder_path}")
    else:
        print(f"Folder not found, skipping: {folder_path}")

def delete_files_with_extension(root_folder, extension):
    """Delete all files with a specific extension in the directory and subdirectories."""
    for foldername, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith(extension):
                file_path = os.path.join(foldername, filename)
                os.remove(file_path)
                print(f"Deleted file: {file_path}")

def reset_app():
    """Remove cache, build artifacts, and other temporary folders."""
    # Folders to delete
    folders_to_delete = ["__pycache__", "dist", "build", "atomic_search.egg-info"]

    # Remove specific folders
    for folder in folders_to_delete:
        delete_folder(folder)

    # Delete all .pyc files
    delete_files_with_extension(".", ".pyc")
    # Delete all .pyo files (compiled Python files with optimization)
    delete_files_with_extension(".", ".pyo")

    print("App reset complete.")

if __name__ == "__main__":
    reset_app()
