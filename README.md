# Webscraping project for Food AI

Purpose is to scrape the web across 5 search engines (Bing, DuckDuckGo, Google, Yahoo, Yandex) given a particular food item, e.g fish curry, cream soup etc.

There are several requirements that that the image must have
1. larger than 100x100
2. contains no humans
3. is not a collage of images
4. food item must be unobstructed, text overlay/watermarks on the image itself is fine but cannot be obstructing the food image

All downloaded images must be still manually checked by a human at the end of the day, since these items are going to be trained on by an AI.

Theorised File Checking Process
1. scrape and parse 5 search engines
2. run through AIChecker
3. human manual verification

current file structure
scraper.py - driver of the downloading process (done)
AIChecker.py - yolov10 to look through each image? if identified human/other non-food lable then discard, else keep

TODO
1. AIChecker.py
