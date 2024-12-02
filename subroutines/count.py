import os

def count_images(directory):
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
    total_images = 0

    for root, dirs, files in os.walk(directory):
        total_images += sum(1 for file in files if os.path.splitext(file)[1].lower() in image_extensions)

    return total_images

directory = "scraped images"  # Replace with the path to your "done" folder
print(f"Total number of images: {count_images(directory)}")
