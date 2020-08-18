import requests
from bs4 import BeautifulSoup
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_SERVER = ""
SMTP_PORT = 0
EMAIL_ADDRESS = ""
PASSWORD = ""
EMAIL_TO = ""


def checkWebPage():
    URL = "https://www.su.nottingham.ac.uk/jobs/"
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(id='web-scraper')
    results = results.prettify()

    file = open("templatenojobs.html", "r")
    template = file.read()
    file.close()

    if(results != template):
        print("Page has changed")
        file = open("newpage.html", "w+")
        file.write(results)
        file.close()

        return True


def createConfig():
    print("\tCreating config file")
    print("\tPlease fill in your email login details")
    file = open("config", "w")
    file.write("SMTP_SERVER=\nSMTP_PORT=\nEMAIL_ADDRESS_FROM=\nPASSWORD=\nEMAIL_ADDRESS_TO=")
    file.close()


def checkConfig():
    global SMTP_SERVER
    global SMTP_PORT
    global EMAIL_ADDRESS
    global PASSWORD
    global EMAIL_TO

    try:
        file = open("config", "r")
    except(FileNotFoundError):
        print("\tConfig file does not exist")
        createConfig()
        exit(1)

    try:
        serverConfig = file.readline()
        portConfig = file.readline()
        emailFromConfig = file.readline()
        passwordConfig = file.readline()
        emailToConfig = file.readline()
    except:
        raise
        print("\tConfig file in wrong format")
        createConfig()
        file.close()
        exit(1)

    file.close()

    server = re.search("^SMTP_SERVER=(.+)$", serverConfig)
    port = re.search("^SMTP_PORT=(.+)$", portConfig)
    emailFrom = re.search("^EMAIL_ADDRESS_FROM=(.+)$", emailFromConfig)
    password = re.search("^PASSWORD=(.+)$", passwordConfig)
    emailTo = re.search("^EMAIL_ADDRESS_TO=(.+)$", emailToConfig)

    if(server is None or port is None or emailFrom is None or password is None or emailTo is None):
        print("\tConfig file not filled in")
        createConfig()
        exit(1)

    SMTP_SERVER = server.group(1)
    SMTP_PORT = int(port.group(1))
    EMAIL_ADDRESS = emailFrom.group(1)
    PASSWORD = password.group(1)
    EMAIL_TO = emailTo.group(1)


def sendEmail():
    s = smtplib.SMTP(host=SMTP_SERVER, port=SMTP_PORT)
    s.starttls()
    s.login(EMAIL_ADDRESS, PASSWORD)

    msg = MIMEMultipart()       # create a message

    # add in the actual person name to the message template
    message = "<p>UoN SU Jobs page has changed: <a href=\"https://www.su.nottingham.ac.uk/jobs/\">Visit Page</a></p>"

    # setup the parameters of the message
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_TO
    msg['Subject'] = "UoN SU Jobs site changed"

    # add in the message body
    msg.attach(MIMEText(message, 'html'))

    # send the message via the server set up earlier.
    s.send_message(msg)

    del msg

    s.quit()


if __name__ == "__main__":
    checkConfig()

    if(checkWebPage()):
        sendEmail()
        print("Sent email")
    else:
        print("Site not changed")

    print("End of program")
