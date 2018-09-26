"""
filename: controllers.py
description: Controllers for email.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 09/25/18
"""

from app.config_email import huey
from app import app
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

@huey.task()
def send_email(msg):
	print(msg.keys())
	with app.app_context():
		msgRoot = MIMEMultipart(msg["subtype"])
		msgRoot['Subject'] = msg["title"]
		msgRoot['From'] = "sgnoreply@rit.edu"
		msgRoot['To'] = msg["recipients"][0]
		msgHtml = MIMEText(msg["html"], 'html')
		msgRoot.attach(msgHtml)

		s = smtplib.SMTP('mymail.rit.edu', 465)
		s.starttls()
		s.login("sgnoreply", "")
		s.sendmail("sgnoreply@rit.edu", msg["recipients"], msgRoot.as_string())
		s.quit()