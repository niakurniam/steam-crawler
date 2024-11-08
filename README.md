# Steam Crawler

**A Python-based crawler to extract data from Steam Community.**

## Overview
This project aims to scrape various information from Steam Community website, including:

* User ID
* User Profile
* User Reviews
* Helpful Votes
* Funny Votes
* Recommendation
* Posting Date

## How it works
1. **Target Selection:** Identify the specific Steam individual game pages to crawl.
2. **WebDriver Initialization:** Set up a WebDriver instance (e.g., Chrome, Firefox) to control a browser.
3. **Page Navigation:** Navigate to the target URLs using the WebDriver.
4. **Dynamic Content Interaction:** Use WebDriver's methods to click buttons, scroll pages, or trigger other actions to load dynamic content.
5. **HTML Parsing:** Once the dynamic content is loaded, parse the HTML using BeautifulSoup4.
6. **Data Extraction:** Extract relevant information from the parsed HTML, such as user id, user profile, user reviews, helpful votes, funny votes, recommendation, and posting date.
7. **Data Storage:** Store the extracted data in a CSV format.

## Requirements
* Python 3.x
* Requests library
* BeautifulSoup4 library
* Selenium WebDriver

## Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/niakurniam/steam-crawler.git
2. **Install dependencies**
   ```bash
   pip install requests beautifulsoup4 selenium webdriver-manager
3. **Install WebDriver**
   * Chrome
     ```bash
     webdriver-manager chrome
   * Firefox
     ```bash
     webdriver-manager firefox

## How to Run
1. **Run the crawler script**
   ```bash
   python main.py "$game_id" --filtering "$filter" --language "$language" --max_reviews "$max_reviews"
   ```
   Example:
   ```bash
   python main.py 730 --filtering "toprated" --language "english" --max_reviews 2000
   
