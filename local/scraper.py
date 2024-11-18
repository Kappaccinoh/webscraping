import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image
from io import BytesIO
import random

# Set up Chrome WebDriver (ensure chromedriver is in your PATH or specify its location)
driver = webdriver.Chrome()

# Set base directory for images
BASE_DIR = "scraped images"
os.makedirs(BASE_DIR, exist_ok=True)

# Define search engines and their URL formats
SEARCH_ENGINES = {
    "bing": "https://www.bing.com/images/search?q={query}",
    "duckduckgo": "https://duckduckgo.com/?q={query}&iax=images&ia=images",
    "google": "https://www.google.com/search?q={query}&tbm=isch",
    "yahoo": "https://images.search.yahoo.com/search/images?p={query}",
    "yandex": "https://yandex.com/images/search?text={query}"
}

# Image filters
MIN_WIDTH = 100
MIN_HEIGHT = 100

# Maximum images to download per engine (specific overrides below)
MAX_IMAGES = 200
NO_PROGRESS_TIMEOUT = 20  # Time in seconds to wait if no progress is made

# Navigation functions for each engine
def random_scroll():
    scroll_distance = random.randint(1000, 3000)
    driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
    time.sleep(random.uniform(1, 3))

def navigate_bing(query):
    search_url = f"https://www.bing.com/images/search?q={query}"
    driver.get(search_url)
    time.sleep(2)
    while True:
        random_scroll()
        # Check for "See more images" button
        try:
            see_more_button = driver.find_element(By.XPATH, "//a[contains(@class, 'btn_seemore')]")
            if see_more_button.is_displayed():
                print("Clicking 'See more images' button...")
                see_more_button.click()
                time.sleep(random.uniform(1, 3))
        except:
            pass
        yield BeautifulSoup(driver.page_source, "html.parser")

def navigate_duckduckgo(query):
    search_url = f"https://duckduckgo.com/?q={query}&iax=images&ia=images"
    driver.get(search_url)
    time.sleep(2)
    for _ in range(random.randint(5, 10)):  # Increase random scrolls for DuckDuckGo
        random_scroll()
        yield BeautifulSoup(driver.page_source, "html.parser")

def navigate_google(query):
    search_url = f"https://www.google.com/search?q={query}&tbm=isch"
    driver.get(search_url)
    time.sleep(2)
    while True:
        random_scroll()
        yield BeautifulSoup(driver.page_source, "html.parser")

def navigate_yahoo(query):
    search_url = f"https://images.search.yahoo.com/search/images?p={query}"
    driver.get(search_url)
    time.sleep(2)
    while True:
        random_scroll()
        # Check for "Show more images" button
        try:
            show_more_button = driver.find_element(By.XPATH, "//button[@name='more-res']")
            if show_more_button.is_displayed():
                print("Clicking 'Show more images' button...")
                show_more_button.click()
                time.sleep(random.uniform(1, 3))
        except:
            pass
        yield BeautifulSoup(driver.page_source, "html.parser")

def navigate_yandex(query):
    search_url = f"https://yandex.com/images/search?text={query}"
    driver.get(search_url)
    time.sleep(2)
    while True:
        random_scroll()
        # Check for "Show more" button
        try:
            show_more_button = driver.find_element(By.XPATH, "//button[contains(@class, 'FetchListButton-Button')]")
            if show_more_button.is_displayed():
                print("Clicking 'Show more' button...")
                show_more_button.click()
                time.sleep(random.uniform(1, 3))
        except:
            pass
        yield BeautifulSoup(driver.page_source, "html.parser")

# Map navigation functions
navigation_functions = {
    "bing": navigate_bing,
    "duckduckgo": navigate_duckduckgo,
    "google": navigate_google,
    "yahoo": navigate_yahoo,
    "yandex": navigate_yandex
}

# Download and save images
def download_image(url, save_path):
    try:
        start_time = time.time()
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
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

# Main scraping function
def scrape_images(search_engine, query, query_folder):
    capitalized_engine = "DuckDuckGo" if search_engine == "duckduckgo" else search_engine.capitalize()
    
    # Replace underscores with spaces in the folder name
    folder_name = capitalized_engine.replace("_", " ")
    folder_path = os.path.join(query_folder, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    if os.path.exists(folder_path) and os.listdir(folder_path):
        print(f"Folder {folder_path} already populated. Skipping {capitalized_engine}...")
        return

    downloaded_urls = set()
    max_images = 400 if search_engine == "yahoo" else MAX_IMAGES
    navigate_function = navigation_functions[search_engine]
    navigation_generator = navigate_function(query)

    image_count = 0
    last_download_time = time.time()

    while image_count < max_images:
        try:
            soup = next(navigation_generator)
        except StopIteration:
            print(f"No more pages to scrape for {capitalized_engine}.")
            break

        image_tags = soup.find_all("img")
        progress_made = False

        for img_tag in image_tags:
            if image_count >= max_images:
                print(f"Reached max limit of {max_images} images for {capitalized_engine}")
                return
            img_url = img_tag.get("src") or img_tag.get("data-src")
            if img_url:
                img_url_full = img_url if img_url.startswith("http") else "https:" + img_url
                if img_url_full in downloaded_urls:
                    continue
                downloaded_urls.add(img_url_full)
                save_name = f"{capitalized_engine}_{image_count + 1:04d}.jpg"
                save_path = os.path.join(folder_path, save_name)
                if download_image(img_url_full, save_path):
                    image_count += 1
                    progress_made = True
                    last_download_time = time.time()

        if not progress_made and (time.time() - last_download_time) > NO_PROGRESS_TIMEOUT:
            print(f"No progress for {NO_PROGRESS_TIMEOUT} seconds. Moving to next search engine.")
            break

# Main function
def main():
    queries = ["soup, chicken noodle, instant prepared",
        "pow, lotus seed paste",
        "jam, unspecified",
        "braised egg in soya sauce",
        "vegetable u-mian",
        "pumpkin, boiled",
        "bread, focaccia"]  # Example search query

    for query in queries:
        query_folder = os.path.join(BASE_DIR, query)
        
        # Replace spaces with underscores in folder name for query
        query_folder = query_folder.replace(" ", " ")

        os.makedirs(query_folder, exist_ok=True)

        for engine in SEARCH_ENGINES:
            print(f"\nScraping images from {engine.capitalize()} for query '{query}'...")
            scrape_images(engine, query, query_folder)

if __name__ == "__main__":
    main()
    driver.quit()
