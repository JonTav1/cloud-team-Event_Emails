
from flask import Flask, jsonify
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Initialize Flask app
app = Flask(__name__)

def scrape_events():
    '''
    Scrapes the event data from Columbia Dining events page and returns it as a DataFrame.
    '''
    event_dict = dict()
    options = Options()

    # Don't load images to speed up scraping
    options.add_argument('--blink-settings=imagesEnabled=false')

    driver = webdriver.Chrome(options=options)
    driver.get('https://dining.columbia.edu/content/events')

    wait = WebDriverWait(driver, 10)
    event_group = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="events-listing"]/div/div[2]')))
    event_divs = event_group.find_elements(By.XPATH, './div')

    today = datetime.now()
    year = today.year
    for i in range(len(event_divs)):
        # date range
        event = event_divs[i]
        months = event.find_elements(By.CLASS_NAME, 'month')
        days = event.find_elements(By.CLASS_NAME, 'day')

        start = f"{months[0].text.title()[:3]} {days[0].text} {year}"
        start = datetime.strptime(start, r"%b %d %Y")

        if (start - today).days > 14:
            break
        if len(months) == 2:
            end = f"{months[1].text.title()[:3]} {days[1].text} {year}"
            end = datetime.strptime(end, r"%b %d %Y")
        else:
            end = start

        event_details = event.find_element(By.XPATH, './div[2]')
        event_dict[i] = dict()

        event_name = event_details.find_element(By.XPATH, './h2').text
        event_dict[i]["event_name"] = event_name

        event_dict[i]["start_date"] = start
        event_dict[i]["end_date"] = end

        event_time = event_details.find_element(By.CLASS_NAME, 'event-date').text
        event_dict[i]["time"] = event_time

        try:
            event_locs = event_details.find_element(By.CLASS_NAME, 'event-location-name')
        except NoSuchElementException:
            event_locs = ""
        else:
            event_locs = event_locs.text
        event_dict[i]["loc"] = event_locs

        event_description = event_details.find_element(By.CLASS_NAME, 'description').text
        event_dict[i]["description"] = event_description

    driver.quit()  # Don't forget to close the browser

    # Return as a DataFrame
    return pd.DataFrame.from_dict(event_dict, orient='index')

@app.route('/api/events', methods=['GET'])
def api_events():
    ''' Provide events as JSON '''
    df = scrape_events()
    events = df.to_dict(orient='records')  # Convert the DataFrame to a list of dictionaries
    return jsonify(events)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
