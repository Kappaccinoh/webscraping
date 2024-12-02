import os

# Directory where the images are stored
SCRAPED_IMAGES_DIR = 'scraped images'

def delete_every_other_image_in_yahoo_folder():
    try:
        # Traverse the subdirectories in scraped images
        for folder_num in os.listdir(SCRAPED_IMAGES_DIR):
            folder_path = os.path.join(SCRAPED_IMAGES_DIR, folder_num)
            if os.path.isdir(folder_path):
                # Check if 'yahoo' folder exists in the current folder
                yahoo_folder_path = os.path.join(folder_path, 'yahoo')
                if os.path.exists(yahoo_folder_path) and os.path.isdir(yahoo_folder_path):
                    print(f"Processing 'yahoo' folder in: {folder_path}")
                    
                    # List all image files in the yahoo folder
                    image_files = [file for file in os.listdir(yahoo_folder_path)
                                   if file.lower().endswith(('jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff'))]

                    # Sort the files to ensure we delete in a predictable order (e.g., alphabetically)
                    image_files.sort()

                    # Delete every other image (starting from the second image)
                    for i, image in enumerate(image_files):
                        if i % 2 != 0:  # If the index is odd, delete the image
                            image_path = os.path.join(yahoo_folder_path, image)
                            os.remove(image_path)
                            print(f"Deleted {image_path}")
                else:
                    print(f"No 'yahoo' folder found in {folder_path}")
    except Exception as e:
        print(f"Error: {e}")

# Run the function
delete_every_other_image_in_yahoo_folder()
