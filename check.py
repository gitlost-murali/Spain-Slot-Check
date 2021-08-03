from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import datetime
import random

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import os
import pytesseract
import pytz
import traceback

import telegram_send

# get the standard UTC time 
UTC = pytz.utc
  
# it will get the time zone 
# of the specified location
IST = pytz.timezone('Asia/Kolkata')

options = Options()
options.add_argument('--headless')

def open_check_close(driver):
    driver.get("http://www.exteriores.gob.es/Embajadas/NUEVADELHI/en/Noticias/Pages/Articulos/20210716_NOT01.aspx")

    # para_link = driver.findElement(By.xpath("//div[@class='ms-rtestate-field']/p")
    # print("Loading website...")
    time.sleep(10)
    WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "// a[contains(text(), 'app.bookitit.com/en/hosteds/')]"))).click()

    # driver.find_element_by_xpath("// a[contains(text(), 'app.bookitit.com/en/hosteds/')]").click()

    # driver.find_element_by_xpath("// a[contains(text(),\
    # 'app.bookitit.com/en/hosteds/')]").click()

    # print("Clicked the instructions link.. Loading...")
    time.sleep(10)

    ### Reference for Switching to active tab
    # https://stackoverflow.com/questions/28715942/how-do-i-switch-to-the-active-tab-in-selenium
    driver.switch_to.window(driver.window_handles[-1])

    WebDriverWait(driver, 120).until(EC.element_to_be_clickable((By.XPATH, "// div[contains(text(),'CONTINUE')]"))).click()

    # driver.find_element_by_xpath("// div[contains(text(),\
    # 'CONTINUE')]").click()

    time.sleep(10)

    # print("Continuing after agreed..")

    WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "// a[contains(text(),'STUDENT VISA')]"))).click()
    # driver.find_element_by_xpath("// a[contains(text(),\
    # 'STUDENT VISA')]").click()

    # print("Clicked on Student visa... Fetching details...")
    time.sleep(5)
    try:
        myElem = WebDriverWait(driver, 90).until(EC.invisibility_of_element_located((By.CLASS_NAME, 'clsDivBktWidgetDefaultLoading')))
        # print("Page is ready!")
    except Exception:
        print("Loading took too much time!")

    x = datetime.datetime.now(IST)
    timestamp = x.strftime("%H:%M:%S_%d-%b-%Y")

    image_filename = f"images/{timestamp}.png"

    driver.save_screenshot(image_filename)
    
    img = Image.open(image_filename)

    text = pytesseract.image_to_string(Image.open(image_filename))
    # print(text)
#    with open(image_filename,"rb") as imgfh:
#        telegram_send.send(captions=["Checking bot integration to group"],images=[imgfh])

    if "No slots available. Try again tomorrow." in text:
        os.remove(image_filename)
    else:
        telegram_send.send(messages=[f"Here's what I found!! => \n\n {text}"])
        draw = ImageDraw.Draw(img)
        # font = ImageFont.truetype(<font-file>, <font-size>)
        font = ImageFont.truetype("sans-serif.ttf", 34)
        # draw.text((x, y),"Sample Text",(r,g,b))
        draw.text((70, 20),f"{timestamp}",(255,0,0),font=font)
        img.save(image_filename)
        with open(image_filename,"rb") as imgfh:
            telegram_send.send(captions=["Here's the supporting screenshot"],images=[imgfh])

while True:
    try:
        driver = webdriver.Firefox(options=options)
        open_check_close(driver)
    except Exception as e:
        print(f"Error occured {e}")
        traceback.print_exc()
        telegram_send.send(messages=[f"Error occured - Will correct soon. \n More: {traceback.print_exc()}"])
    
    # close web driver
    driver.quit()
    time.sleep(random.randint(120, 240))

