import requests
import wikipedia
import pywhatkit as kit
from email.message import EmailMessage
import smtplib
from decouple import config



EMAIL = config("EMAIL")  # Fetch your email from the environment
PASSWORD = config("PASSWORD")  # Fetch your app-specific password securely



def findIP():
    ip_address=requests.get('https://api.ipify.org?format=json').json()
    return ip_address["ip"]


def search_on_wikipedia():
    results=wikipedia.summary(query, sentences=2)
    return results


def search_on_google(query):
    kit.search(query)

def youtube(video):
    kit.playonyt(video)


def send_email(receiver_add,subject,message):
    try:
        email=EmailMessage()
        email['To']=receiver_add
        email['Subject']=subject
        email['From']=EMAIL
        
        email.set_content(message)
        s=smtplib.SMTP("smtp.gmail.com",587)
        s.starttls()
        s.login(EMAIL,PASSWORD)
        s.send_message(email)
        s.close()
        return True

    except Exception as e:
        print(e)
        return False