import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
from io import BytesIO
import random

import boto3
import zipfile

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
MAX_IMAGES = 200  # Maximum images to download per engine
NO_PROGRESS_TIMEOUT = 20  # Time in seconds to wait if no progress is made

# Configure Chrome WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run without UI
chrome_options.add_argument("--no-sandbox")  # Required for some Linux environments
chrome_options.add_argument("--disable-dev-shm-usage")  # Handle shared memory issues
chrome_options.add_argument("--disable-gpu")  # Optional for headless mode
chrome_options.add_argument("--window-size=1920,1080")  # Set a default screen size

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Random scroll simulation for dynamic content loading
def random_scroll():
    scroll_distance = random.randint(1000, 3000)
    driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
    time.sleep(random.uniform(1, 3))

# Navigation functions for each search engine
def navigate_bing(query):
    driver.get(f"https://www.bing.com/images/search?q={query}")
    time.sleep(2)
    while True:
        random_scroll()
        try:
            see_more_button = driver.find_element(By.XPATH, "//a[contains(@class, 'btn_seemore')]")
            if see_more_button.is_displayed():
                see_more_button.click()
                time.sleep(random.uniform(1, 3))
        except:
            pass
        yield BeautifulSoup(driver.page_source, "html.parser")

def navigate_duckduckgo(query):
    driver.get(f"https://duckduckgo.com/?q={query}&iax=images&ia=images")
    time.sleep(2)
    for _ in range(random.randint(5, 10)):
        random_scroll()
        yield BeautifulSoup(driver.page_source, "html.parser")

def navigate_google(query):
    driver.get(f"https://www.google.com/search?q={query}&tbm=isch")
    time.sleep(2)
    while True:
        random_scroll()
        yield BeautifulSoup(driver.page_source, "html.parser")

def navigate_yahoo(query):
    driver.get(f"https://images.search.yahoo.com/search/images?p={query}")
    time.sleep(2)
    while True:
        random_scroll()
        try:
            show_more_button = driver.find_element(By.XPATH, "//button[@name='more-res']")
            if show_more_button.is_displayed():
                show_more_button.click()
                time.sleep(random.uniform(1, 3))
        except:
            pass
        yield BeautifulSoup(driver.page_source, "html.parser")

def navigate_yandex(query):
    driver.get(f"https://yandex.com/images/search?text={query}")
    time.sleep(2)
    while True:
        random_scroll()
        try:
            show_more_button = driver.find_element(By.XPATH, "//button[contains(@class, 'FetchListButton-Button')]")
            if show_more_button.is_displayed():
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
        start_time = time.time()  # Start timer for each image download
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        
        if img.width >= MIN_WIDTH and img.height >= MIN_HEIGHT:
            img.save(save_path)
            download_time = time.time() - start_time  # Calculate time taken to download the image
            print(f"Saved image: {save_path} in {download_time:.2f} seconds")
            return True
        else:
            print(f"Skipped small image: {url}")
            return False
    except Exception as e:
        print(f"Failed to download image from {url}: {e}")
        return False

# Scraping function
def scrape_images(search_engine, query, query_folder):
    folder_path = os.path.join(query_folder, search_engine.capitalize())
    os.makedirs(folder_path, exist_ok=True)

    if os.listdir(folder_path):  # Skip if folder already populated
        print(f"Folder {folder_path} already exists. Skipping {search_engine}...")
        return

    downloaded_urls = set()
    max_images = MAX_IMAGES
    navigate_function = navigation_functions[search_engine]
    navigation_generator = navigate_function(query)

    image_count = 0
    last_download_time = time.time()
    start_scrape_time = time.time()  # Track the total time to scrape images

    while image_count < max_images:
        try:
            soup = next(navigation_generator)
        except StopIteration:
            print(f"No more pages to scrape for {search_engine}.")
            break

        image_tags = soup.find_all("img")
        progress_made = False

        for img_tag in image_tags:
            if image_count >= max_images:
                print(f"Reached max limit of {max_images} images for {search_engine}")
                break
            img_url = img_tag.get("src") or img_tag.get("data-src")
            if img_url:
                img_url_full = img_url if img_url.startswith("http") else "https:" + img_url
                if img_url_full in downloaded_urls:
                    continue
                downloaded_urls.add(img_url_full)
                save_name = f"{search_engine.capitalize()}_{image_count + 1:04d}.jpg"
                save_path = os.path.join(folder_path, save_name)
                if download_image(img_url_full, save_path):
                    image_count += 1
                    progress_made = True
                    last_download_time = time.time()

        if not progress_made and (time.time() - last_download_time) > NO_PROGRESS_TIMEOUT:
            print(f"No progress for {NO_PROGRESS_TIMEOUT} seconds. Moving to next search engine.")
            break

    total_scrape_time = time.time() - start_scrape_time  # Total time for the entire scraping process
    print(f"Total time taken to scrape images from {search_engine.capitalize()}: {total_scrape_time:.2f} seconds")

# Add this function to zip the folder
def zip_folder(folder_path, zip_name):
    zip_path = f"{folder_path}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for folder_name, subfolders, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(folder_name, filename)
                zip_file.write(file_path, os.path.relpath(file_path, folder_path))
    print(f"Zipped folder {folder_path} into {zip_path}")
    return zip_path

# Add this function to upload the zip file to S3
def upload_to_s3(zip_path, bucket_name, s3_key):
    s3_client = boto3.client('s3', region_name='us-east-1')
    try:
        s3_client.upload_file(zip_path, bucket_name, s3_key)
        print(f"Successfully uploaded {zip_path} to s3://{bucket_name}/{s3_key}")
    except Exception as e:
        print(f"Error uploading to S3: {e}")

# Function to send SNS notification
def send_sns_notification(message, subject):
    sns_client = boto3.client('sns', region_name='us-east-1')
    sns_topic_arn = 'REDACTED'  # Replace with your SNS topic ARN
    try:
        sns_client.publish(
            TopicArn=sns_topic_arn,
            Message=message,
            Subject=subject
        )
        print(f"Notification sent: {subject}")
    except Exception as e:
        print(f"Error sending SNS notification: {e}")
        raise

# Main function with added zipping and uploading steps
def main():
    queries = ["soup chicken noodle"]  # Example search query
    for query in queries:
        query_folder = os.path.join(BASE_DIR, query.replace(" ", "_"))
        os.makedirs(query_folder, exist_ok=True)

        for engine in SEARCH_ENGINES:
            print(f"\nScraping images from {engine.capitalize()} for query '{query}'...")
            scrape_images(engine, query, query_folder)

        # After scraping, zip the folder
        zip_name = f"{query.replace(' ', '_')}"
        zip_path = zip_folder(query_folder, zip_name)

        # Now upload the zip to S3
        bucket_name = 'REDACTED' # Define the bucket name
        s3_key = f"downloaded_raw/{zip_name}.zip"  # Define the path in the bucket
        upload_to_s3(zip_path, bucket_name, s3_key)

        # Send SNS notification about the upload
        sns_message = f"The images for '{query}' have been successfully scraped and uploaded to S3."
        sns_subject = f"Image Scraping for '{query}' Completed"
        send_sns_notification(sns_message, sns_subject)

        # Optionally, clean up the local zip file after upload
        if os.path.exists(zip_path):
            os.remove(zip_path)
            print(f"Deleted local zip file {zip_path}")

if __name__ == "__main__":
    try:
        main()
    finally:
        driver.quit()
