from FC15.models import EmailActivate
from django.core.mail import send_mail
from FC15Website.settings import EMAIL_FROM
from random import Random

# Generate a random string
def random_string(str_length = 50):
    ans_str = ''
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    length = len(chars) - 1
    random = Random()
    for i in range(str_length):
        ans_str += chars[random.randint(0, length)]
    return ans_str


# Add a record and send a mail to activate accounts
def mail_activate(email, username):
    email_activate = EmailActivate()
    email_activate.username = username
    email_activate.activate_string = random_string()
    email_activate.save()

    email_title = 'Please activate your account for FC15'
    email_body = 'Please click the link to activate your account for FC15:\nhttp://' # should add the address of the server
    email_body += email_activate.activate_string
    return send_mail(email_title, email_body, EMAIL_FROM, [email])