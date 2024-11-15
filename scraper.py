import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image
from io import BytesIO

# Initialize Chrome WebDriver (ensure chromedriver is in your PATH or specify its location)
driver = webdriver.Chrome()

# Set base directory for images
BASE_DIR = "scraped_images"
os.makedirs(BASE_DIR, exist_ok=True)

# Define search engines and their URL formats in alphabetical order
SEARCH_ENGINES = {
    "bing": "https://www.bing.com/images/search?q={query}",
    "duckduckgo": "https://duckduckgo.com/?q={query}&iax=images&ia=images",
    "google": "https://www.google.com/search?q={query}&tbm=isch",
    "yahoo": "https://images.search.yahoo.com/search/images?p={query}",
    "yandex": "https://yandex.com/images/search?text={query}"
}

# Filter out images smaller than 100x100 pixels
MIN_WIDTH = 100
MIN_HEIGHT = 100

# Maximum number of images to download per search engine
MAX_IMAGES = 200
NO_PROGRESS_TIMEOUT = 20  # Time in seconds to wait if no progress is made

# Function to download and save images
def download_image(url, save_path):
    try:
        start_time = time.time()
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise an error for bad responses
        img = Image.open(BytesIO(response.content))
        # Check dimensions
        if img.width >= MIN_WIDTH and img.height >= MIN_HEIGHT:
            img.save(save_path)
            elapsed_time = time.time() - start_time
            print(f"Saved image: {save_path} in {elapsed_time:.2f}s")
            return True
        else:
            print(f"Skipped small image: {url}")
            return False
    except Exception as e:
        print(f"Failed to download image from {url}: {e}")
        return False

# Function to scrape images from each search engine
def scrape_images(search_engine, query, query_folder):
    capitalized_engine = "DuckDuckGo" if search_engine == "duckduckgo" else search_engine.capitalize()
    
    # Create a folder for each search engine within the query folder
    folder_path = os.path.join(query_folder, capitalized_engine)
    os.makedirs(folder_path, exist_ok=True)

    # Check if the folder is empty
    if os.path.exists(folder_path) and os.listdir(folder_path):
        print(f"Folder {folder_path} already populated. Skipping {capitalized_engine}...")
        return  # Skip scraping if the folder is not empty

    # Set to keep track of downloaded URLs
    downloaded_urls = set()
    
    # Navigate to the search engine
    search_url = SEARCH_ENGINES[search_engine].format(query=query)
    driver.get(search_url)
    time.sleep(2)  # Allow page to load

    image_count = 0
    last_download_time = time.time()  # Track time since the last download
    
    while image_count < MAX_IMAGES:
        # Scroll down and allow time for new images to load
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Parse HTML to find image URLs
        soup = BeautifulSoup(driver.page_source, "html.parser")
        image_tags = soup.find_all("img")

        progress_made = False  # Track if new images are downloaded in this loop

        for img_tag in image_tags:
            if image_count >= MAX_IMAGES:
                print(f"Reached max limit of {MAX_IMAGES} images for {capitalized_engine}")
                return
            img_url = img_tag.get("src") or img_tag.get("data-src")
            if img_url:
                # Normalize URL if it doesn't start with "http"
                img_url_full = img_url if img_url.startswith("http") else "https:" + img_url
                
                # Check for duplicates
                if img_url_full in downloaded_urls:
                    continue  # Skip duplicate images

                # Add the URL to the set to avoid duplicates
                downloaded_urls.add(img_url_full)

                # Attempt to download the image
                save_name = f"{capitalized_engine}_{image_count + 1:04d}.jpg"
                save_path = os.path.join(folder_path, save_name)
                if download_image(img_url_full, save_path):
                    image_count += 1
                    progress_made = True  # Update progress if an image is downloaded
                    last_download_time = time.time()  # Reset the last download time

        # Check if no progress has been made within the timeout period
        if not progress_made and (time.time() - last_download_time) > NO_PROGRESS_TIMEOUT:
            print(f"No progress for {NO_PROGRESS_TIMEOUT} seconds. Moving to next search engine.")
            break

    # Post-processing for specific search engines
    if search_engine == "yahoo":
        print("Deleting every other image for Yahoo")
        delete_every_other_image(folder_path)
    elif search_engine == "bing":
        print("Deleting the first 8 images for Bing")
        delete_first_n_images(folder_path, 8)

# Function to delete every other image in a folder (Yahoo-specific)
def delete_every_other_image(folder_path):
    images = sorted(os.listdir(folder_path))
    for i, image in enumerate(images):
        if i % 2 == 1:  # Delete every second image
            os.remove(os.path.join(folder_path, image))
            print(f"Deleted: {image} in {folder_path}")

# Function to delete the first N images in a folder (Bing-specific)
def delete_first_n_images(folder_path, n):
    images = sorted(os.listdir(folder_path))
    for i in range(min(n, len(images))):  # Ensure we don't try to delete more than available images
        os.remove(os.path.join(folder_path, images[i]))
        print(f"Deleted first image: {images[i]} in {folder_path}")

# Main loop to start scraping
def main():
    queries = ["soup, chicken noodle, instant prepared",
    "pow, lotus seed paste",
    "jam, unspecified",
    "braised egg in soya sauce",
    "vegetable u-mian",
    "pumpkin, boiled",
    "bread, focaccia"]
    
    for query in queries:
        # Create a query folder within the BASE_DIR
        query_folder = os.path.join(BASE_DIR, query.replace(" ", "_"))
        os.makedirs(query_folder, exist_ok=True)

        for engine in SEARCH_ENGINES:
            print(f"\nScraping images from {engine.capitalize()} for query '{query}'...")
            scrape_images(engine, query, query_folder)

# Run the main function
if __name__ == "__main__":
    main()

# Close the WebDriver after scraping is done
driver.quit()
