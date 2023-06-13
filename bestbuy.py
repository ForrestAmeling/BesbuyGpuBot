import bs4
import sys
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

password = "Password" #Password for bestbuy. 
securityCode = "000" #Credit card security code

print("Starting")

# Product Page (By default, This URL will scan all RTX 3070's at one time.)
#Nvidea 3070
# url = 'https://www.bestbuy.com/site/nvidia-geforce-rtx-3070-8gb-gddr6-pci-express-4-0-graphics-card-dark-platinum-and-black/6429442.p?skuId=6429442'
#AMD 6800
url = 'https://www.bestbuy.com/site/msi-radeon-rx-6800-16g-16gb-gddr6-pci-express-4-0-graphics-card-black-black/6441020.p?skuId=6441020'
def timeSleep(x, driver):
    for i in range(x, -1, -1):
        sys.stdout.write('\r')
        sys.stdout.write('{:2d} seconds'.format(i))
        sys.stdout.flush()
        time.sleep(1)
    driver.refresh()
    sys.stdout.write('\r')
    sys.stdout.write('Page refreshed\n')
    sys.stdout.flush()


def createDriver():
    """Creating driver."""
    options = Options()
    # Change To True if you do not want to see Firefox Browser.
    # Change To False if you want to see Firefox Browser.
    options.headless = True
    # Enter Firefox Profile Here in quotes.
    profile = webdriver.FirefoxProfile(
        r'C:\Users\fameling\AppData\Roaming\Mozilla\Firefox\Profiles\oknumbyk.default-release')
    driver = webdriver.Firefox(profile, options=options, executable_path=GeckoDriverManager().install())
    return driver


def driverWait(driver, findType, selector):
    """Driver Wait Settings."""
    while True:
        if findType == 'css':
            try:
                driver.find_element_by_css_selector(selector).click()
                break
            except NoSuchElementException:
                driver.implicitly_wait(0.2)
        elif findType == 'name':
            try:
                driver.find_element_by_name(selector).click()
                break
            except NoSuchElementException:
                driver.implicitly_wait(0.2)

def findingCards(driver):
    """Scanning all cards."""
    print("Going to BestBuy")
    driver.get(url)
    while True:
        html = driver.page_source
        soup = bs4.BeautifulSoup(html, 'html.parser')
        wait = WebDriverWait(driver, 15)
        wait2 = WebDriverWait(driver, 2)
        try:
            findAllCards = soup.find('button',
                                     {'class': 'btn btn-primary btn-lg btn-block btn-leading-ficon add-to-cart-button'})
            if findAllCards:
                print(f'Button Found!: {findAllCards.get_text()}')

                # Clicking Add to Cart.
                driverWait(driver, 'css', '.add-to-cart-button')
                time.sleep(1)

                # Going To Cart.
                print("Going to cart")
                driver.get('https://www.bestbuy.com/cart')
                print("Went to cart")
                time.sleep(4)

                # Click Shipping Option. (If Available)
                # try:
                #     # wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#fulfillment_1losStandard0")))
                #     print("Clicking Shipping Option.")
                #     driver.find_element_by_id("id^=fulfillment-shipping").click()
                #     # driver.find_element_by_css_selector("div.availability_list :nth-child(25)").click()
                #     # driverWait(driver, 'css', '#fulfillment_1losStandard0')
                #     print("Ship To Home.")
                #     time.sleep(3)
                # except (NoSuchElementException, TimeoutException):
                #     pass

                # Checking if item is still in cart.
                try:
                    wait.until(
                        EC.presence_of_element_located((By.XPATH, "//*[@class='btn btn-lg btn-block btn-primary']")))
                    driver.find_element_by_xpath("//*[@class='btn btn-lg btn-block btn-primary']").click()
                    print("Item Is Still In Cart.")
                except (NoSuchElementException, TimeoutException):
                    print("Item is not in cart anymore. Retrying..")
                    timeSleep(3, driver)
                    findingCards(driver)
                    return

                # Trying Password
                try:
                    print("Attempting to Login.")
                    time.sleep(2)
                    print("Entering Password")
                    driver.find_element_by_id("fld-p1").send_keys(password)
                    time.sleep(1)
                    print("Attempting to Sign In")
                    wait2.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".btn-secondary")))
                    driverWait(driver, 'css', '.btn-secondary')
                    time.sleep(3)
                except (NoSuchElementException, TimeoutException, ElementNotInteractableException):
                    print("Could Not Login.")
                print("Login Successful")

                # Trying CVV
                try:
                    print("\nTrying CVV Number.\n")
                    time.sleep(2)
                    driver.find_element_by_id("credit-card-cvv").send_keys(securityCode)
                    time.sleep(1)

                except (NoSuchElementException, TimeoutException):
                    pass
                print("CVV Entered Successfully")

                # Bestbuy Text Updates. (If Available)
                try:
                    wait2.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#text-updates")))
                    driverWait(driver, 'css', '#text-updates')
                    print("Selecting Text Updates.")
                except (NoSuchElementException, TimeoutException):
                    pass

                # Final Checkout. Bot is ready to buy.
                try:
                    wait2.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".btn-primary")))
                    driverWait(driver, 'css', '.btn-primary')
                except (NoSuchElementException, TimeoutException, ElementNotInteractableException):
                    try:
                        wait2.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".btn-secondary")))
                        driverWait(driver, 'css', '.btn-secondary')
                        timeSleep(5, driver)
                        wait2.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".btn-primary")))
                        time.sleep(1)
                        driverWait(driver, 'css', '.btn-primary')
                    except (NoSuchElementException, TimeoutException, ElementNotInteractableException):
                        print("Could Not Complete Checkout.")

                # Completed Checkout. Sending message with Twilio.
                print('Order Placed!')
                for i in range(3):
                    print('\a')
                    time.sleep(1)
                time.sleep(86400)
                driver.quit()
                return
            else:
                pass

        # This is the Refresh Page Timer if product is out of stock. It is prefered to leave it at 5 seconds.
        except NoSuchElementException:
            pass
        print ("Sold Out")
        timeSleep(1, driver)


if __name__ == '__main__':
    driver = createDriver()
    findingCards(driver)
