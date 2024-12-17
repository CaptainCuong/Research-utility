import os
import fnmatch

def list_folders_in_current_directory():
    """
    Lists all folders in the current directory.

    :return: List of folder names in the current directory.
    """
    current_directory = os.getcwd()  # Get the current directory
    folders = []

    # Iterate over all entries in the current directory
    for entry in os.listdir(current_directory):
        # Check if the entry is a directory
        if os.path.isdir(os.path.join(current_directory, entry)):
            folders.append(entry)
    return folders


def search_files_by_name(pattern, folders):
    """
    Search recursively for files with names matching a given text pattern in specified folders.

    :param pattern: Text pattern to match file names.
    :param folders: List of folders to search in.
    :return: List of matching file paths.
    """
    matching_files = []

    if 'all' in folders:
        folders = list_folders_in_current_directory()

    pattern = pattern.lower()
    for folder in folders:
        # Walk through each directory in the folder
        for root, dirs, files in os.walk(folder):
            for file_name in files:
                # Check if the file name matches the pattern
                if pattern in file_name.lower():
                    matching_files.append(os.path.join(root, file_name))

    return matching_files

# Example usage:
folders_to_search = ['all']
name_pattern = 'hypersph'  # Example pattern to match .txt files
found_files = search_files_by_name(name_pattern, folders_to_search)

print(f"Files matching the pattern '{name_pattern}':")
for file in found_files:
    print(file)