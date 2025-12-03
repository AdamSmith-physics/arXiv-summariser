import json
import smtplib
import datetime

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


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


    def write_email_content(self, relevant_results, receiver_email):

        today = datetime.date.today().strftime("%Y-%m-%d")

        message = MIMEMultipart("alternative")
        message["Subject"] = f"arXiv Summary for {today}"
        message["From"] = self.email_address
        message["To"] = receiver_email

        html = f"""\
        <html>
            <body>
                <h2>Top Relevant arXiv Papers for {today}</h2>
        """
        
        for paper in relevant_results[:3]:
            html += f"""\
                <h3>{paper.title} (ArXiv ID: <a href="{paper.entry_id}">{paper.get_short_id()}</a>)</h3>
                <p><strong>Authors:</strong> {', '.join([author.name for author in paper.authors])}</p>
                <p><strong>Summary:</strong> {paper.summary}</p>
                <hr>
            """

        html += f"""\
                <br>
                <br>
                <h2>Other Relevant arXiv Papers</h2>
        """

        for paper in relevant_results[3:]:
            html += f"""\
                <p>
                <strong>{paper.title} (ArXiv ID: <a href="{paper.entry_id}">{paper.get_short_id()}</a>)</strong><br>
                {', '.join([author.name for author in paper.authors])}
                </p>
            """

        html += f"""\
            </body>
        </html>
        """

        content = MIMEText(html, "html")
        message.attach(content)
        
        return message