# Webscraping project for Food AI

Purpose is to scrape the web across 5 search engines (Bing, DuckDuckGo, Google, Yahoo, Yandex) given a particular food item, e.g fish curry, cream soup etc.

There are several requirements that that the image must have
1. larger than 100x100
2. contains no humans
3. is not a collage of images
4. food item must be unobstructed, text overlay/watermarks on the image itself is fine but cannot be obstructing the food image

All downloaded images must be still manually checked by a human at the end of the day, since these items are going to be trained on by an AI.

~~Theorised File Checking Process~~
~~1. scrape and parse 5 search engines~~
~~2. (REDUNDANT) flatten hierarchy (technically can do in part 1 but its easier to detect for scraping failure)~~
~~3. run through AIChecker~~
~~4. human manual verification~~
~~5. manual uploading of verified folders to onedrive~~

[NEW] AWS Architecture
1. scraper.py run drivers
2. upload to aws bucket
3. AIChecker.py to pull from bucket
4. run ai yolov? on images for surface scraping
5. AIChecker.py to push back to aws bucket
6. notify via SNS
7. SNS link to lambda function deliver message to telegram
8. human manual verification
9. manual uploading of verified folders to onedrive

Structure of AWS Services
![AWS Diagram](image.png)

FACTORED
- ALL (random scrolling and increase in frequency)

PHOTO REQUIREMENTS
- 100x100 minimum
- no collage
- no people

TODO
1. AIChecker.py

ISSUES
1. AWS Free Tier not enough to run NVIDIA GPUs, unable to implement AI checker in practice

PROBLEMS/BUGS
1. Yahoo browser downloading duplicate images