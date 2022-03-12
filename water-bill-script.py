from venmo_api import Client
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from water_bill import WaterBill
import time
from decouple import config
import json
from webdriver_manager.chrome import ChromeDriverManager

PATH = "/Users/mason/development/chromedriver"
URL = "https://ub.minneapolismn.gov/app/login.jsp"

# Scrape water bill website for water bill information
def get_water_bill():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    # driver = webdriver.Chrome(PATH)
    driver.get(URL)
    driver.find_element_by_id("accountAccessTab").click()
    time.sleep(1)
    driver.find_element_by_id("searchAddress").send_keys(config('address',default=''))
    time.sleep(3)
    driver.find_element_by_id("ui-id-1").click()
    time.sleep(1)
    driver.find_element_by_id("addressSearchButton").click()
    time.sleep(3)
    balance = driver.find_element_by_id("my_account_current_balance").text
    due_date = driver.find_element_by_id("my_account_current_due_date").text
    balance = float(balance.replace('$',''))
    driver.quit()
    return WaterBill(balance, due_date)

# Returns the price each roommate has to pay for the current month's water bill (including myself)
def calculate_price_per_roommate(num_of_roommates, balance):
    return round( balance / num_of_roommates, 2)
    
# Requests money via venmo from roommates
def request_money(venmo_client, roommates, price_per_roommate, due_date):
    for roommate in roommates:
        print("Requesting money from: ", roommate)
        venmo_client.payment.request_money(price_per_roommate, "Water bill " + due_date, roommates[roommate])

def main():
    # Access account with access token
    venmo_client = Client(access_token=config('access_token',default=''))

    # Get water bill details like balance and due date
    water_bill = get_water_bill()

    # Dictionary of roommates. Key value pair of name -> venmo_id
    roommates = json.loads(config('roommates', '{}'))
    
    price_per_roommate = calculate_price_per_roommate((len(roommates)+1), water_bill.balance - 10.72)
    request_money(venmo_client, roommates, price_per_roommate, water_bill.due_date)

if __name__ == "__main__":
    main()
    
