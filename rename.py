import os

def rename_files(folder_path):
    for filename in os.listdir(folder_path):
        # Skip directories
        if os.path.isdir(os.path.join(folder_path, filename)):
            continue
        
        # Only rename if filename is longer than 13 characters
        if len(filename) > 13:
            new_name = filename[13:]
            old_file = os.path.join(folder_path, filename)
            new_file = os.path.join(folder_path, new_name)
            
            # Rename the file
            os.rename(old_file, new_file)
            print(f'Renamed: "{filename}" -> "{new_name}"')
        else:
            print(f'Skipped (filename too short): "{filename}"')

if __name__ == "__main__":
    folder = input("Enter the folder path: ")
    rename_files(folder)
