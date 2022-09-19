#!/usr/bin/env python
# coding: utf-8

# In[2]:

import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

def send_mail(send_from, send_to, subject, body, files=[],
              server="127.0.0.1", port=587, user="", password=""):
    if not isinstance(send_to, list):
        send_to = [send_to]
    if not isinstance(files, list):
        files = [files]

    msg = MIMEMultipart("mixed")
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(body,"plain"))

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                _subtype="csv",
                Name=basename(f)
            )
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)
        
    try:
        smtp = smtplib.SMTP(server,port)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(user, password)
        smtp.sendmail(send_from, send_to, msg.as_string())
    except Exception as e:
        print(e)
    finally:
        smtp.quit()



