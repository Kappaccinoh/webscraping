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

# Maximum images to download per engine (specific overrides below)
MAX_IMAGES = 200
NO_PROGRESS_TIMEOUT = 20  # Time in seconds to wait if no progress is made

# Configure Chrome WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run without UI
chrome_options.add_argument("--no-sandbox")  # Required for some Linux environments
chrome_options.add_argument("--disable-dev-shm-usage")  # Handle shared memory issues
chrome_options.add_argument("--disable-gpu")  # Optional for headless mode
chrome_options.add_argument("--window-size=1920,1080")  # Set a default screen size

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

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
                break
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
    
    # Post-process for Yahoo: Delete every other image
    if search_engine == "yahoo":
        print(f"Post-processing: Deleting every other image in {folder_path}")
        delete_every_other_image(folder_path)
        print("\nPost-processing for Yahoo completed")
    
    # Post-process for Bing: Delete the first 8 images
    if search_engine == "bing":
        print(f"Post-processing: Deleting the first 8 images in {folder_path}")
        delete_first_n_images(folder_path, 8)
        print("\nPost-processing for Bing complete.")

    return

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

# Add this function to count the number of images in a folder
def count_images_in_folder(folder_path):
    if not os.path.exists(folder_path):
        return 0
    return len([f for f in os.listdir(folder_path) if f.endswith((".jpg", ".png", ".jpeg"))])

# Define the scrape_images function to continue if images are insufficient
def scrape_images(search_engine, query, query_folder):
    capitalized_engine = "DuckDuckGo" if search_engine == "duckduckgo" else search_engine.capitalize()
    
    # Replace underscores with spaces in the folder name
    folder_name = capitalized_engine.replace("_", " ")
    folder_path = os.path.join(query_folder, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    downloaded_urls = set()
    navigate_function = navigation_functions[search_engine]
    navigation_generator = navigate_function(query)
    
    max_images = 400 if search_engine == "yahoo" else MAX_IMAGES
    image_count = count_images_in_folder(folder_path)
    last_download_time = time.time()

    if image_count >= max_images:
        print(f"{capitalized_engine} folder already has {image_count} images. Skipping...")
        return

    print(f"{capitalized_engine} folder has {image_count}/{max_images} images. Continuing scraping...")

    while image_count < max_images:
        try:
            soup = next(navigation_generator)
        except StopIteration:
            print(f"No more pages to scrape for {capitalized_engine}.")
            break
        except Exception as e:
            print(f"Error navigating {capitalized_engine}: {e}. Skipping...")
            break

        image_tags = soup.find_all("img")
        progress_made = False

        for img_tag in image_tags:
            if image_count >= max_images:
                print(f"Reached max limit of {max_images} images for {capitalized_engine}")
                break
            img_url = img_tag.get("src") or img_tag.get("data-src")
            if img_url:
                img_url_full = img_url if img_url.startswith("http") else "https:" + img_url
                if img_url_full in downloaded_urls:
                    continue
                downloaded_urls.add(img_url_full)
                save_name = f"{capitalized_engine}_{image_count + 1:04d}.jpg"
                save_path = os.path.join(folder_path, save_name)
                try:
                    if download_image(img_url_full, save_path):
                        image_count += 1
                        progress_made = True
                        last_download_time = time.time()
                except requests.exceptions.RequestException as e:
                    print(f"Failed to download image from {img_url_full}: {e}. Skipping...")
                    continue

        if not progress_made and (time.time() - last_download_time) > NO_PROGRESS_TIMEOUT:
            print(f"No progress for {NO_PROGRESS_TIMEOUT} seconds. Moving to next search engine.")
            break

    return

# Modify main to include error handling and retries
def main():
    queries = ["potato cutlet, deep fried",
        "dim sum, turnip cake, steamed",
        "chicken burrito",
        "bun, custard",
        "achar",
        "cauliflower masala",
        "sambal sweet potato leaves",
        "plain aglio aglio",
        "japanese shoyu ramen",
        "braised pork ribs, with black mushroom and taucheo",
        "soup, chicken noodle, instant prepared",
        "pow, lotus seed paste",
        "jam, unspecified",
        "braised egg in soya sauce",
        "vegetable u-mian",
        "pumpkin, boiled",
        "bread, focaccia"
    ]

    completed_count = 0

    for query in queries:
        query_folder = os.path.join(BASE_DIR, query.replace(" ", "_"))
        os.makedirs(query_folder, exist_ok=True)

        for engine in SEARCH_ENGINES:
            try:
                print(f"\nScraping images from {engine.capitalize()} for query '{query}'...")
                scrape_images(engine, query, query_folder)
            except Exception as e:
                print(f"Error with {engine.capitalize()} for query '{query}': {e}. Skipping engine...")

        # After scraping, zip the folder
        zip_name = f"{query.replace(' ', '_')}"
        zip_path = zip_folder(query_folder, zip_name)

        # Now upload the zip to S3
        bucket_name = 'REDACTED'
        s3_key = f"downloaded_raw/{zip_name}.zip"
        try:
            upload_to_s3(zip_path, bucket_name, s3_key)
        except Exception as e:
            print(f"Error uploading {zip_path} to S3: {e}. Skipping upload...")

        # Clean up the local zip file after upload
        if os.path.exists(zip_path):
            os.remove(zip_path)
            print(f"Deleted local zip file {zip_path}")
        
        completed_count += 1

        # Send an SNS notification for every 5 completed folders
        if completed_count % 5 == 0:
            sns_message = f"{completed_count} folders have been successfully scraped, zipped, and uploaded to S3."
            sns_subject = f"Progress Update: {completed_count} Folders Completed"
            send_sns_notification(sns_message, sns_subject)

    # Final notification after all queries are processed
    sns_message = f"The images for all {len(queries)} queries have been successfully scraped and uploaded to S3."
    sns_subject = f"Image Scraping for All {len(queries)} Queries Completed"
    send_sns_notification(sns_message, sns_subject)

if __name__ == "__main__":
    try:
        main()
    finally:
        driver.quit()