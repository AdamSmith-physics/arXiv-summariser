import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load email details from file
with open("email_details.dno", "r") as f:
    lines = f.readlines()
    sender_email = lines[0].strip()
    password = lines[1].strip()

receiver_email = "adam.gammon-smith@nottingham.ac.uk"

message = MIMEMultipart("alternative")
message["Subject"] = "multipart test"
message["From"] = sender_email
message["To"] = receiver_email

# Create the plain-text and HTML version of your message
text = """\
Hi,
How are you?
Real Python has many great tutorials:
www.realpython.com"""
html = """\
<html>
  <body>
    <b>Header!</b>
    <h1>This is a heading</h1>
    <p>Hi,<br>
       How are you?<br>
       <a href="http://www.realpython.com">Real Python</a> 
       has many great tutorials.
    </p>
    <p>
        Regards,<br>
        Adam
    </p>
  </body>
</html>
"""

# Turn these into plain/html MIMEText objects
part1 = MIMEText(text, "plain")
part2 = MIMEText(html, "html")

# Add HTML/plain-text parts to MIMEMultipart message
# The email client will try to render the last part first
# message.attach(part1)  # We don't need to include the plain text part!
message.attach(part2)


with smtplib.SMTP_SSL('smtp.virginmedia.com', 465) as server:
    server.login(sender_email, password)
    server.sendmail(
        sender_email, receiver_email, message.as_string()
    )





# s = smtplib.SMTP_SSL('smtp.virginmedia.com', 465)


# s.

# message = """Subject: sent from python
# Hello world"""

# s.sendmail("adam.smith.home@ntlworld.com", "adam.gammon-smith@nottingham.ac.uk", message)
# # terminating the session
# s.quit()