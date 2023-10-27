import smtplib
import os
from email.mime.text import MIMEText
from email.utils import formatdate
import json


def create_message(from_addr, to_addr, bcc_addrs, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Bcc'] = bcc_addrs
    msg['Date'] = formatdate()
    return msg

def send(from_addr, to_addrs, msg, my_password):
    smtpobj = smtplib.SMTP('smtp.gmail.com', 587) # GmailのSMTPサーバーへ
    smtpobj.ehlo()
    smtpobj.starttls()
    smtpobj.ehlo()
    smtpobj.login(from_addr, my_password)
    smtpobj.sendmail(from_addr, to_addrs, msg.as_string())
    smtpobj.close()
    
def sendMail(userEmail):
    with open('secret.json') as f:
        info = json.load(f)
        
    FROM_ADDRESS = os.getenv("email")
    MY_PASSWORD = os.getenv("password")
    
    TO_ADDRESS = userEmail
    BCC = ''
    SUBJECT = 'ご予約の時間の15分前となりました。'
    BODY = 'cafe labは、管理棟二階３J教室にあります！！ ご来店お待ちしております！！'
    msg = create_message(FROM_ADDRESS, TO_ADDRESS, BCC, SUBJECT, BODY)
    send(FROM_ADDRESS, TO_ADDRESS, msg, MY_PASSWORD)
    

