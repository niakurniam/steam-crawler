import re
import csv
import time
import argparse
from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver

def scrape_reviews(game_id, filtering=None, order=None, max_reviews=None, language=None):
    # Setup webdriver using Chrome
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Your User-Agent Here")  # Replace with random user-agent if needed
    driver = webdriver.Chrome(options=options)

    # Construct URL based on game_id, filtering, and order
    base_url = f"https://steamcommunity.com/app/{game_id}/reviews/?p=1&"
    if filtering:
        base_url += f"browsefilter={filtering}&"
    if order:
        base_url += f"sort={order}&"
    if language:
        base_url += f"filterLanguage={language}"

    driver.get(base_url)
    reviews = []
    collected_reviews = set()
    last_scroll_height = driver.execute_script("return document.body.scrollHeight")

    # Extract the game ID from the URL
    game_id_match = re.search(r"app/(\d+)", base_url)
    game_id = game_id_match.group(1) if game_id_match else "Unknown"

    while len(reviews) <= max_reviews:
        # Scroll down automatically to get more reviews
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(10) # Pause for few seconds

        # Check for new content of reviews
        new_scroll_height = driver.execute_script("return document.body.scrollHeight")
        if new_scroll_height == last_scroll_height:
            break
        last_scroll_height = new_scroll_height

        # Extract reviews from the page source
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        review_cards = soup.select('.apphub_Card')

        for card in review_cards:
            # Extract user profile link and ID
            user_link = card.select_one('.apphub_CardContentAuthorName a')
            if user_link and 'href' in user_link.attrs:
                user_url = user_link['href']
                # Use regex to extract the user ID from the profile URL
                user_id_match = re.search(r"/(profiles|id)/([^/]+)/", user_url)
                unique_id = user_id_match.group(2) if user_id_match else "Unknown"
            else:
                unique_id = None

            review_data = {}

            review_data['user_id'] = unique_id if unique_id else "Unknown"
            collected_reviews.add(unique_id)

            # Extract user name
            regex = re.compile('apphub_CardContentAuthorName')
            user_name = card.find('div', attrs={'class': regex})
            review_data['user_name'] = user_name.text.strip() if user_name else "Unknown"

            # Extract review text
            review_text_div = card.select_one('.apphub_CardTextContent')
            if review_text_div:
                review_text = review_text_div.get_text(separator=" ", strip=True)
                # Use regex to remove "Posted: [Date]" pattern
                # review_text = re.sub(r'Posted: \d{1,2}\s+\w+, \d{4}|Posted: \w+\s+\d{1,2}, \d{4}|Posted: \d{1,2} \w+|Posted: \w+ \d{1,2}', '',
                #                      review_text).strip()
                review_text = re.sub(r'Posted: \d{1,2} \w+(?:, \d{4})?|'r'Posted: \w+ \d{1,2}(?:, \d{4})?', '', review_text).strip()

            if (unique_id, review_text) in collected_reviews:
                continue
            collected_reviews.add((unique_id, review_text))  # Track unique reviews
            review_data['review_text'] = review_text

            # Extract helpful and funny votes
            votes_div = card.select_one('.found_helpful')
            if votes_div:
                votes_text = votes_div.get_text(separator=" ", strip=True)
                helpful_match = re.search(r"(\d+|\d{1,3}(?:,\d{3})) people found this review helpful", votes_text)
                funny_match = re.search(r"(\d+|\d{1,3}(?:,\d{3})) people found this review funny", votes_text)
                review_data['helpful_votes'] = int(helpful_match.group(1).replace(',', '')) if helpful_match else 0
                review_data['funny_votes'] = int(funny_match.group(1).replace(',', '')) if funny_match else 0
            else:
                review_data['helpful_votes'] = 0
                review_data['funny_votes'] = 0

            # Extract recommendation (1 for Recommended, -1 for Not Recommended)
            recommendation = card.find('div', attrs={'class': 'title'})
            if recommendation:
                recommendation_text = recommendation.text.strip()
                review_data['recommendation'] = 1 if recommendation_text == 'Recommended' else -1
            else:
                review_data['recommendation'] = 0

            # Extract date posted
            dateposted_text_div = card.find('div', attrs={'class': 'date_posted'})
            if dateposted_text_div:
                dateposted_text = dateposted_text_div.text.strip()
                dateposted_match = re.search(
                    r'Posted:\s*(\w+ \d{1,2}(?:, \d{4})?|'r'\d{1,2} \w+(?:,\s+\d{4})?)', dateposted_text)
                review_data['date_posted'] = dateposted_match.group(1) if dateposted_match else None
                if review_data['date_posted']:
                    try:
                        # Try parsing with the year format
                        if ',' in review_data['date_posted']:
                            try:
                                # Check for "Day Month, Year" format, e.g., "November 4, 2019"
                                date_posted = datetime.strptime(review_data['date_posted'], "%B %d, %Y")
                            except ValueError:
                                # Check for "Day Month, Year" format, e.g., "4 November, 2019"
                                date_posted = datetime.strptime(review_data['date_posted'], "%d %B, %Y")
                        else:
                            try:
                                # Parse without year
                                date_posted = datetime.strptime(review_data['date_posted'], "%d %B")
                                # Add the current year if needed (optional)
                                date_posted = date_posted.replace(year=datetime.now().year)
                            except ValueError:
                                # print("Error: Invalid date format")
                                # date_posted = None
                                date_posted = datetime.strptime(review_data['date_posted'], "%B %d")
                                date_posted = date_posted.replace(year=datetime.now().year)

                        # If date parsing was successful, format it as "MM/DD/YYYY"
                        if date_posted:
                            formatted_date = date_posted.strftime("%m/%d/%Y")
                            print("Formatted Date:", formatted_date)
                    except ValueError:
                        print("Error: Invalid date format")
                else:
                    print("Date not found.")
            else:
                review_data['date_posted'] = "Unknown"

            reviews.append(review_data)

            # Stop if we've collected enough reviews
            if len(reviews) >= max_reviews:
                break

    driver.quit()

    filename = f"steam_reviews_{game_id}_{filtering}_{language}_{max_reviews}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['user_id', 'user_name', 'review_text', 'helpful_votes', 'funny_votes', 'recommendation', 'date_posted']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for review in reviews:
            writer.writerow(review)
    print(f"Reviews saved to {filename}")

def main():
    parser = argparse.ArgumentParser(description='Steam Review Scraper')
    # parser.add_argument('url', type=str, help='Steam community review URL (e.g., https://steamcommunity.com/app/APP_ID/reviews/)')
    # parser.add_argument('--max_pages', type=int, default=10, help='Maximum number of pages to scrape')
    parser.add_argument('game_id', type=str, help='Steam game ID (e.g., 570 for Dota 2)')
    parser.add_argument('--filtering', type=str, choices=['mostrecent', 'recentlyupdated', 'toprated', 'trendday'],
                        help='Filter reviews (e.g., mostrecent or helpful or recent update or trendday)')
    parser.add_argument('--order', type=str, choices=['asc', 'desc'], help='Order of reviews (e.g., asc or desc)')
    parser.add_argument('--max_reviews', type=int, default=100, help='Maximum number of unique reviews to collect')
    parser.add_argument('--language', type=str, help='Language of reviews to collect (e.g., all, english, spanish, etc.)')
    args = parser.parse_args()

    # Run the scraper with the provided arguments
    scrape_reviews(args.game_id, args.filtering, args.order, args.max_reviews, args.language)

if __name__ == "__main__":
    main()
