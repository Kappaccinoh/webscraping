import os
import shutil
import re

def unflatten_directory(query_folder):
    """
    Moves images in query_folder back into subdirectories based on search engine names.
    Assumes images are prefixed with the search engine name (e.g., 'Bing_0001.jpg').
    """
    print("\nUnflattening directory structure...")
    
    # Regular expression to match filenames with search engine prefix
    engine_prefix_pattern = re.compile(r"^(Bing|DuckDuckGo|Google|Yahoo|Yandex)_(\d+)\.jpg", re.IGNORECASE)
    
    for image_file in os.listdir(query_folder):
        image_path = os.path.join(query_folder, image_file)
        
        # Skip if it's not a file
        if not os.path.isfile(image_path):
            continue
        
        # Identify search engine prefix in the filename
        match = engine_prefix_pattern.match(image_file)
        if match:
            # Get search engine name and adjust capitalization as needed
            engine_name = match.group(1)
            if engine_name.lower() == "duckduckgo":
                engine_name = "DuckDuckGo"
            else:
                engine_name = engine_name.capitalize()
            
            engine_folder_path = os.path.join(query_folder, engine_name)
            
            # Create subfolder for the search engine if it doesn't exist
            os.makedirs(engine_folder_path, exist_ok=True)
            
            # Move the file to the appropriate subfolder
            destination_path = os.path.join(engine_folder_path, image_file)
            shutil.move(image_path, destination_path)
            print(f"Moved {image_file} to {engine_folder_path}")
        else:
            print(f"Skipped file without a recognizable prefix: {image_file}")

# Define the folder to unflatten (replace 'scraped_images/fish_curry' with your folder path)
query_folder = "scraped_images/yong tau foo, chilli sauce [DONE]"

# Run the unflattening function
if __name__ == "__main__":
    unflatten_directory(query_folder)
