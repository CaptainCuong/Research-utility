from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

url = "https://dl.acm.org/doi/proceedings/10.1145/3581783"

# Set up the Selenium WebDriver (you need to have the appropriate driver installed)
# Download the driver from https://sites.google.com/chromium.org/driver/
driver = webdriver.Chrome()

# Navigate to the URL
driver.get(url)

# Find all <a> tags with IDs starting with "heading"
links = driver.find_elements(By.CSS_SELECTOR, 'a[id^="heading"]')

for link in links:
    # Click on the link to activate hidden content
    driver.execute_script("arguments[0].click();", link)
    # link.click()

    # Wait for some time to let the content load (you might need to adjust the time based on the page)
    driver.implicitly_wait(5)

    # Get the updated page source
    page_source = driver.page_source

    # Parse the updated HTML
    soup = BeautifulSoup(page_source, 'html.parser')

    # Now you can work with the updated HTML content
    # For example, print the title of the page
    print("Title after clicking {}: {}".format(link.get_attribute('href'), soup.title.text))

# Close the browser
driver.quit()