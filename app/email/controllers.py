"""
filename: controllers.py
description: Controllers for email.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 09/25/18
"""

from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.utils import formataddr
from app.email.models import huey
from app import app
import smtplib
import config

##
## @brief      Sends an email.
##
## @param      msg   The message object containing:
## 					 - subtype: Message type (related)
## 					 - title: Email subject
## 					 - sender: Tuple with (name, email)
## 					 - recipients: Array of emails.
## 					 - html: Rendered html template in string.
##
## @return     None
##
@huey.task(retries= 5, retries_as_argument=True)
def send_email(msg, retries):
	mime = MIMEMultipart(msg["subtype"])
	mime['Subject'] = msg["title"]
	mime['From'] = formataddr(msg["sender"])
	mime['To'] = ", ".join(msg["recipients"])

	# Attatch html
	msgHtml = MIMEText(msg["html"], 'html')
	mime.attach(msgHtml)

	# Attach images
	with app.open_resource("static/sg-logo.png") as fp:
		sg_logo = MIMEImage(fp.read())
		sg_logo.add_header('Content-ID', '<sg-logo>')
		mime.attach(sg_logo)
		fp.close()

	with app.open_resource("static/paw.png") as fp:
		sg_paw = MIMEImage(fp.read())
		sg_paw.add_header('Content-ID', '<sg-paw>')
		mime.attach(sg_paw)
		fp.close()

	try:
		server = smtplib.SMTP(config.MAIL_SERVER, config.MAIL_PORT)
		server.starttls()
		server.login(config.MAIL_USERNAME, config.MAIL_PASSWORD)
		server.sendmail(msg["sender"][1], msg["recipients"], mime.as_string())
	except:

		if retries != 0: raise
		print("ERROR: Email failed after three retries")

	server.quit()
