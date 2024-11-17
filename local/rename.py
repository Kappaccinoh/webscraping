import os

# Define the base directory
base_directory = "scraped images"

# Ensure the directory exists
if not os.path.exists(base_directory):
    print(f"The directory '{base_directory}' does not exist.")
else:
    # Iterate through all items in the directory
    for item in os.listdir(base_directory):
        item_path = os.path.join(base_directory, item)
        
        # Check if the item is a directory
        if os.path.isdir(item_path):
            # Replace underscores with spaces in the folder name
            new_name = item.replace("_", " ")
            new_path = os.path.join(base_directory, new_name)
            
            # Rename the directory
            if item != new_name:  # Avoid unnecessary renaming
                os.rename(item_path, new_path)
                print(f"Renamed: '{item}' -> '{new_name}'")
            else:
                print(f"No change needed for: '{item}'")
