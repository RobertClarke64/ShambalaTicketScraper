# import libraries
import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import os.path
from twilio.rest import Client
from datetime import datetime
import argparse

CONFIG_TEMPLATE = "TWILIO_ACCOUNT_SID=\nTWILIO_AUTH_TOKEN=\nNUMBER_TO=\nTWILIO_NUMBER_FROM="

TWILIO_ACCOUNT_SID = ""
TWILIO_AUTH_TOKEN = ""
NUMBER_TO = ""
TWILIO_NUMBER_FROM = "''"


def createConfig():
    print("\tCreating config file")
    print("\tPlease fill in your registration number details")
    file = open("config", "w")
    file.write(CONFIG_TEMPLATE)
    file.close()


def checkConfig():
    global TWILIO_ACCOUNT_SID
    global TWILIO_AUTH_TOKEN
    global NUMBER_TO
    global TWILIO_NUMBER_FROM

    try:
        file = open("config", "r")
    except(FileNotFoundError):
        print("\tConfig file does not exist")
        createConfig()
        exit(1)

    try:
        accountSidConfig = file.readline()
        authTokenConfig = file.readline()
        numberToConfig = file.readline()
        numberFromConfig = file.readline()
    except:
        raise
        print("\tConfig file in wrong format")
        createConfig()
        file.close()
        exit(1)

    file.close()

    accountSid = re.search("^TWILIO_ACCOUNT_SID=(.+)$", accountSidConfig)
    authToken = re.search("^TWILIO_AUTH_TOKEN=(.+)$", authTokenConfig)
    numberTo = re.search("^NUMBER_TO=(.+)$", numberToConfig)
    numberFrom = re.search("^TWILIO_NUMBER_FROM=(.+)$", numberFromConfig)

    TWILIO_ACCOUNT_SID = accountSid.group(1)
    TWILIO_AUTH_TOKEN = authToken.group(1)
    NUMBER_TO = numberTo.group(1)
    TWILIO_NUMBER_FROM = numberFrom.group(1)


def sendText():
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    message = client.messages.create(
        to=NUMBER_TO,
        from_=TWILIO_NUMBER_FROM,
        body="Shambala tickets site has been modified")

    print(message.sid)

def template():
    checkPage("template.html")


def checkPage(filePath):
    checkConfig()

    urlpage = 'https://www.shambalafestival.org/buy-tickets/'
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)

    driver.get(urlpage)
    driver.switch_to.frame("iFrameResizer0")

    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "t1-adult-tickets"))
        )
    except:
        pass

    try:
        results = driver.find_element_by_id("t1-adult-tickets")
        #print('Number of results', len(results))

        #result = results[0].text
        result = results.text
        file = open(filePath, "w+")
        file.write(result)
        file.close()
    except Exception as e:
        print(e)
        file = open("error.html", "w+")
        file.write(driver.page_source)
        file.close()
        driver.quit()
        exit(1)

    driver.quit()

    return result



if __name__ == "__main__":

    checkConfig()

    parser = argparse.ArgumentParser(description='Check for template creator argument')
    parser.add_argument('-T', "--template", help="Create template file to monitor changes from", action="store_true")
    args = parser.parse_args()

    if args.template or not os.path.isfile("template.html"):
        template()
        print("Created template from current page state")
        same = true
    else:
        result = checkPage("current.html")
        file = open("template.html", "r")
        template = file.read()
        file.close()

        same = template == result

        if not same:
            print("Site changed")
            sendText()
        else:
            print("Site not changed")


    now = datetime.now()
    file = open("timerun.txt", "a+")
    file.write(str(now.date()) + " " + str(now.time()) + "\n" + "Page " +
               ("same" if same else "different") +"\n")
    file.close()
