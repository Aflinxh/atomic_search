import shutil
import os

def clear_logs():
    if os.path.exists("dataset-testing/js"):
        shutil.rmtree("dataset-testing/js")
    if os.path.exists("dataset-testing/obfuscated_js_dataset.csv"):
        os.remove("dataset-testing/obfuscated_js_dataset.csv")

    os.makedirs("dataset-testing/js", exist_ok=True)
    open("dataset-testing/obfuscated_js_dataset.csv", "x")
    
if __name__ == "__main__":
    clear_logs()
