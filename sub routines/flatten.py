import os
import shutil

def flatten_directory(query_folder):
    """
    Move all files from subdirectories of query_folder into the main query_folder.
    Handles filename conflicts by appending a counter to duplicate filenames.
    """
    print("\nFlattening directory structure...")
    for engine_folder in os.listdir(query_folder):
        engine_folder_path = os.path.join(query_folder, engine_folder)
        
        # Only proceed if it's a directory
        if os.path.isdir(engine_folder_path):
            for image_file in os.listdir(engine_folder_path):
                source_path = os.path.join(engine_folder_path, image_file)
                dest_path = os.path.join(query_folder, image_file)
                
                # Handle potential file name conflicts by renaming
                counter = 1
                while os.path.exists(dest_path):
                    file_name, file_ext = os.path.splitext(image_file)
                    dest_path = os.path.join(query_folder, f"{file_name}_{counter}{file_ext}")
                    counter += 1
                
                # Move the file to the main folder
                shutil.move(source_path, dest_path)
                print(f"Moved: {source_path} to {dest_path}")
            
            # Remove the now-empty engine folder
            os.rmdir(engine_folder_path)
            print(f"Removed empty folder: {engine_folder_path}")

# Define the folder to flatten (replace 'scraped_images/fish_curry' with your folder path)
query_folder = "scraped_images/yong tau foo, chilli sauce [DONE]"

# Run the flattening function
if __name__ == "__main__":
    flatten_directory(query_folder)
