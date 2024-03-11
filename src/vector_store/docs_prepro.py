import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
APP_FOLDER = os.getenv("APP_FOLDER", "")
DATA_PATH = os.path.join(APP_FOLDER, './data/documents/2021')

def remove_extra_spaces(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        content = ' '.join(content.split())
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def process_directory(directory):
    txt_files = [f for f in os.listdir(directory) if f.endswith('.txt')]
    total_files = len(txt_files)

    for i, filename in enumerate(txt_files, start=1):
        file_path = os.path.join(directory, filename)
        remove_extra_spaces(file_path)
        progress = (i / total_files) * 100
        print(f"Processed {filename} ({i}/{total_files}, {progress:.2f}%)")


def preprocess_docs(directory):
    process_directory(directory)





def main():
    directory_path = DATA_PATH
    preprocess_docs(directory_path)


if __name__ == "__main__":
    main()