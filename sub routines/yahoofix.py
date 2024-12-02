import os

# Directory where the images are stored
SCRAPED_IMAGES_DIR = 'scraped images'

def delete_every_other_image():
    try:
        # Traverse the subdirectories in scraped images
        for root, dirs, files in os.walk(SCRAPED_IMAGES_DIR):
            # Check if the current folder is 'yahoo', skip it
            if 'Yahoo' in root.split(os.sep):
                print(f"Skipping 'yahoo' folder: {root}")
                continue

            # List the files in the current directory
            image_files = [file for file in files if file.lower().endswith(('jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff'))]
            
            # Sort the files to ensure we delete in a predictable order (e.g., alphabetically)
            image_files.sort()

            # Delete every other image
            for i, image in enumerate(image_files):
                if i % 2 != 0:  # If the index is odd, delete the image
                    image_path = os.path.join(root, image)
                    os.remove(image_path)
                    print(f"Deleted {image_path}")
                    
    except Exception as e:
        print(f"Error: {e}")

# Run the function
delete_every_other_image()
