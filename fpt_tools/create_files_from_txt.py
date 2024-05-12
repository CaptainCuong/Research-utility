import os

def create_files_from_paths(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            path = line.strip()  # Remove leading/trailing whitespace and newline
            if not os.path.exists(path):
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w') as new_file:
                    new_file.write("")  # Write an empty string to create the file

if __name__ == "__main__":
    file_path = input("Enter the path to the text file containing paths: ")
    create_files_from_paths(file_path)
    print("Files created successfully.")