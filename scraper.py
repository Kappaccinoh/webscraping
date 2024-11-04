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
MAX_IMAGES_YANDEX = 150  # Yandex limit set to 150
MAX_IMAGES_OTHER = 200    # Other search engines limit set to 200

# Function to download and save images
def download_image(url, save_path):
    try:
        response = requests.get(url, timeout=5)
        img = Image.open(BytesIO(response.content))
        # Check dimensions
        if img.width >= MIN_WIDTH and img.height >= MIN_HEIGHT:
            img.save(save_path)
            print(f"Saved image: {save_path}")
            return True
        else:
            print(f"Skipped small image: {url}")
            return False
    except Exception as e:
        print(f"Failed to download image from {url}: {e}")
        return False

# Function to scrape images from each search engine
def scrape_images(search_engine, query, query_folder):
    # Capitalize the search engine name for folder and file naming
    capitalized_engine = search_engine.capitalize()
    
    # Create a folder for each search engine within the query folder
    folder_path = os.path.join(query_folder, capitalized_engine)
    os.makedirs(folder_path, exist_ok=True)

    # Check if the folder is empty
    if os.path.exists(folder_path) and os.listdir(folder_path):
        print(f"Folder {folder_path} already populated. Skipping {capitalized_engine}...")
        return  # Skip scraping if the folder is not empty

    # Navigate to the search engine
    search_url = SEARCH_ENGINES[search_engine].format(query=query)
    driver.get(search_url)
    time.sleep(2)  # Allow page to load

    # Scroll to load more images
    image_count = 0
    scroll_count = 0
    max_images = MAX_IMAGES_OTHER if search_engine != "yandex" else MAX_IMAGES_YANDEX

    while image_count < max_images:
        # Check for "Show more" button on Yandex
        if search_engine == "yandex":
            try:
                load_more_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Show more')]")
                load_more_button.click()
                time.sleep(2)  # Allow more images to load
            except Exception as e:
                print(f"No more 'Show more' button found: {e}")
                break  # Exit if no more load button

        # Scroll down and allow time for new images to load
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        scroll_count += 1

        # Parse HTML to find image URLs
        soup = BeautifulSoup(driver.page_source, "html.parser")
        image_tags = soup.find_all("img")

        # Try downloading images from the current set of image tags
        for idx, img_tag in enumerate(image_tags):
            if image_count >= max_images:
                print(f"Reached max limit of {max_images} images for {capitalized_engine}")
                return
            img_url = img_tag.get("src") or img_tag.get("data-src")
            if img_url and img_url.startswith("http"):
                # Handle Yandex image URLs
                if search_engine == "yandex":
                    img_url = "https:" + img_url if img_url.startswith("//") else img_url
                save_name = f"{capitalized_engine}_{image_count + 1:04d}.jpg"
                save_path = os.path.join(folder_path, save_name)
                if download_image(img_url, save_path):
                    image_count += 1
        
        # Break the loop if scrolling does not load new images after several attempts
        if scroll_count > 10:
            print(f"Reached scroll limit with {image_count} images for {capitalized_engine}")
            break

# Main loop to start scraping
def main():
    query = "curry fish"  # Replace with your search term
    
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
