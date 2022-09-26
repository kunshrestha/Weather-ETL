#!/usr/bin/env python
# coding: utf-8

# In[6]:


import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

def send_mail(send_from, send_to, subject, body, files=[],
              server="127.0.0.1", port=587, user="", password=""):
    """This function sends email with or without attachment.
    Desable multi level authentication in email server
    for it to work.
    
    Parameters
    send_from: str, sender's email address
    send_to: str or list or str, receiver's address(es)
    subject: str, subject of email
    body: str, plain email body
    files: str or list of str, file path(s) to send as attachment, default []
    server: str, smtp server name, default 127.0.0.1
    port: int, smtp port, default 587,
    user: str, usually sender's email address
    password: str, email password

    Returns nothing
    """
    
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
                # extract the subtype of the file e.g. .csv, .pdf etc.
                _subtype=f[f.index("."):],
                Name=basename(f)
            )
        # After the file is closed
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
        pass
    finally:
        smtp.quit()
