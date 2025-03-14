from os import getenv
from dotenv import load_dotenv
load_dotenv()
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from use_cases.MySQLDB import MySQLDB

class Email:
    def __init__(self, destiny: list[str], mensagem: str) -> None:
        self.mysqldb: MySQLDB = MySQLDB(host=getenv("HOST"), user=getenv("USER"), password=getenv("PWD"), database=getenv("DATABASE"))
        self.destiny = destiny
        self.smtp_server: str = getenv('SMTP_SERVER')
        self.port: int = getenv('SERVER_PORT')
        self.sender_email: str = getenv('EMAIL_SENDER')
        self.password: str = getenv("EMAIL_PASSWORD")
        self.message: MIMEMultipart = MIMEMultipart()
        self.message["From"] = self.sender_email
        self.message["To"] = ", ".join(self.destiny)
        self.message["Subject"] = f"!!!ARQUIVO DUPLICADO!!!"
        body: str = mensagem

        self.message.attach(MIMEText(body, "html"))

    def send_email(self) -> None:
        server: smtplib.SMTP = smtplib.SMTP(self.smtp_server, self.port)
        recipients: list = self.destiny
        server.starttls()
        server.login(self.sender_email, self.password)

        server.sendmail(self.sender_email, recipients, self.message.as_string())

        print('E-mail enviado com sucesso!')
        server.quit()
