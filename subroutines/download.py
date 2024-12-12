import boto3
import os
import zipfile
import shutil

# AWS S3 configuration
BUCKET_NAME = 'web-scraping-food-ai-bucket'  # Replace with your bucket name
LOCAL_DOWNLOAD_PATH = 'downloaded zips'  # Local folder to save downloaded files
SCRAPED_IMAGES_DIR = 'scraped images'  # Directory to extract images into

# Create directories if they don't exist
os.makedirs(LOCAL_DOWNLOAD_PATH, exist_ok=True)
os.makedirs(SCRAPED_IMAGES_DIR, exist_ok=True)

# Initialize S3 client
s3_client = boto3.client('s3', region_name='us-east-1')

def download_zip_files_from_s3(bucket_name, local_path):
    try:
        # List objects in the bucket
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        if 'Contents' not in response:
            print("No objects found in the bucket.")
            return

        # Iterate through the objects in the bucket
        for obj in response['Contents']:
            file_key = obj['Key']
            # Check if the object is a ZIP file
            if file_key.endswith('.zip'):
                # Replace underscores with spaces in the file name
                file_name = os.path.basename(file_key).replace('_', ' ')
                zip_dir_name = os.path.splitext(file_name)[0]  # Removing .zip extension
                extract_dir = os.path.join(SCRAPED_IMAGES_DIR, zip_dir_name)

                # Skip if the directory already exists
                if os.path.exists(extract_dir):
                    print(f"Skipping {file_name}, already extracted to {extract_dir}.")
                    continue

                local_file_path = os.path.join(local_path, file_name)
                print(f"Downloading {file_key} to {local_file_path}...")

                # Download the file
                s3_client.download_file(bucket_name, file_key, local_file_path)
                print(f"Downloaded {file_name} successfully!")

                # Extract the ZIP file to a subdirectory in the scraped images folder
                extract_zip_file(local_file_path, SCRAPED_IMAGES_DIR, file_name)
            else:
                print(f"Skipping non-ZIP file: {file_key}")

        # After all downloads and extractions, remove the 'downloaded zips' folder
        shutil.rmtree(local_path)
        print(f"Deleted the folder: {local_path}")

    except Exception as e:
        print(f"Error downloading files: {e}")

def extract_zip_file(zip_path, extract_to, zip_file_name):
    try:
        # Create a subdirectory for each ZIP file in the scraped images directory (replace underscores with spaces)
        zip_dir_name = os.path.splitext(zip_file_name)[0].replace('_', ' ')  # Removing .zip extension and replacing _ with space
        extract_dir = os.path.join(extract_to, zip_dir_name)
        os.makedirs(extract_dir, exist_ok=True)

        # Extract the ZIP file to that subdirectory
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            print(f"Extracted {zip_path} to {extract_dir}")
    except Exception as e:
        print(f"Error extracting {zip_path}: {e}")

# Call the function
download_zip_files_from_s3(BUCKET_NAME, LOCAL_DOWNLOAD_PATH)
