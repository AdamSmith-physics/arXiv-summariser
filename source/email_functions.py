

import json
import smtplib


class EmailClient:


    def __init__(self, file_path="settings/email_details.json"):
        email_details = self._load_email_details(file_path)

        self.smtp_server = email_details["smtp_server"]
        self.smtp_port = email_details["smtp_port"]
        self.email_address = email_details["email_address"]
        self.email_password = email_details["email_password"]


    def _load_email_details(self, file_path):
        with open(file_path, 'r') as f:
            settings = json.load(f)
        return settings
    

    def send_email(self, receiver_email, message):
        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.email_address, self.email_password)
                server.sendmail(
                    self.email_address, receiver_email, message.as_string()
                )
            print("Email sent successfully.")
        except Exception as e:
            print(f"Failed to send email: {e}")