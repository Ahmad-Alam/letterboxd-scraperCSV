import requests
from bs4 import BeautifulSoup
import csv

def convert_rating_to_numeric(rating):
    if rating == 'N/A':
        return -1
    elif rating == '½':
        return 1
    elif rating == '★':
        return 2
    elif rating == '★½':
        return 3
    elif rating == '★★':
        return 4
    elif rating == '★★½':
        return 5
    elif rating == '★★★':
        return 6
    elif rating == '★★★½':
        return 7
    elif rating == '★★★★':
        return 8
    elif rating == '★★★★½':
        return 9
    elif rating == '★★★★★':
        return 10
    else:
        # Handle other cases as needed
        return -1  # Default for unknown ratings

    
def convert_rating_to_stars(rating):
    if rating == 'N/A':
        return 'N/A'
    else:
        return rating


def export_to_csv(file_path, data):
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Movie Name', 'Ratings'])
        for row in data:
            writer.writerow(row)

def get_number_of_pages(soup):
    paginate_list = soup.find("div", class_="paginate-pages")
    if paginate_list:
        paginate_items = paginate_list.find_all("li", class_="paginate-page")
        # Check for unseen-pages
        if "unseen-pages" in str(paginate_list):
            # If unseen-pages is present, consider only the visible page numbers
            visible_pages = [item.find("a").text for item in paginate_items if item.find("a")]
            last_page = int(visible_pages[-1]) if visible_pages else 1
        else:
            # If no unseen-pages, consider all page numbers
            last_page = int(paginate_items[-2].find("a").text) if paginate_items else 1
        return last_page
    else:
        # If there's no pagination element, assume only one page
        return 1


# Get username for ratings
username = input("Enter Letterboxd username: ")

# Construct the initial URL
url = "https://letterboxd.com/{}/films/".format(username)

# Send a GET request to retrieve the first page content
response = requests.get(url)
html_content = response.content

# Create a BeautifulSoup object to parse the HTML
soup = BeautifulSoup(html_content, "html.parser")

# Get the number of pages
num_pages = get_number_of_pages(soup)

# Initialize list to store all ratings data
all_ratings_data = []

# Loop through each page and scrape data
for page in range(1, num_pages + 1):
    # Construct the URL for the current page
    page_url = "{}page/{}/".format(url, page) if page > 1 else url
    
    # Send a GET request to retrieve the page content
    response = requests.get(page_url)
    html_content = response.content
    
    # Create a BeautifulSoup object to parse the HTML
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Find the list containing the movie ratings
    rating_list = soup.find_all("li", class_="poster-container")
    
    # Extract movie titles and ratings from the list
    ratings_data = []
    for item in rating_list:
        try:
            title = item.find("img")["alt"].strip()
            rating = item.find("span", class_="rating").text
        except AttributeError as err:
            rating = "N/A"

        ratings_data.append([title, convert_rating_to_numeric(rating)])

    # Append the current page's ratings data to the overall data
    all_ratings_data.extend(ratings_data)

# Sort the overall ratings data based on numeric values
sorted_ratings = sorted(all_ratings_data, key=lambda x: x[1], reverse=True)

# Export data to CSV file
csv_file_path = "{}_film_ratings_all_pages.csv".format(username)
export_to_csv(csv_file_path, sorted_ratings)
print("Data from all pages has been exported to '{}'.".format(csv_file_path))
