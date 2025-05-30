import uuid
import sys
import time
import random
import string
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

from django.core.mail import EmailMessage
from django.template.loader import get_template


def generate_random_code(prefix: str = "D", code_length: int = 5):
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(code_length))


def generate_barcode(
    prefix: str = "P",
):
    random_number = "".join(random.choices("0123456789", k=10))
    return f"{prefix}{random_number}"


def getId(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex}"


def generate_ticket_no(cid: str = "0", company_name: str = "") -> str:
    if cid is None:
        return f"{company_name}00001"
    if len(cid) == 1:
        return f"{company_name}0000{cid}"
    elif len(cid) == 2:
        return f"{company_name}000{cid}"
    elif len(cid) == 3:
        return f"{company_name}00{cid}"
    elif len(cid) == 4:
        return f"{company_name}0{cid}"
    else:
        return f"{company_name}{cid}"


def Syserror(e):
    exception_type, exception_object, exception_traceback = sys.exc_info()
    filename = exception_traceback.tb_frame.f_code.co_filename
    line_number = exception_traceback.tb_lineno
    print("ERROR --> Mesaage: ", e)
    print("ERROR --> Exception type: ", exception_type)
    print("ERROR --> File name: ", filename)
    print("ERROR --> Line number: ", line_number)
    return None


def convert_hour(seconds):
    tm_obj = time.gmtime(seconds)
    if tm_obj.tm_hour > 0:
        if tm_obj.tm_min > 0:
            return f"{tm_obj.tm_hour}:{tm_obj.tm_min}"
        return f"{tm_obj.tm_hour}:0"
    else:
        return f"0:{tm_obj.tm_min}"


def encrypt_user_secret_token(message):
    cipher_suite = Fernet(settings.USER_SECRET_KEY)
    encrypted_message = cipher_suite.encrypt(message.encode()).decode()
    return encrypted_message


def decrypt_user_secret_token(encrypted_message):
    try:
        cipher_suite = Fernet(settings.USER_SECRET_KEY)
        decrypted_message = cipher_suite.decrypt(encrypted_message).decode()
        return decrypted_message
    except InvalidToken:
        return None


def validate_quantity(quant: str) -> any:
    try:
        intQuant = int(quant)
        return intQuant
    except ValueError:
        try:
            floatQuant = float(quant)
            return floatQuant
        except ValueError:
            return None


def sendEmail_template(email_to, subject, email_template_path, email_context):
    if not settings.IS_ALLOWED_EMAIL_SEND:
        return False
    try:
        message = get_template(email_template_path).render(email_context)
        msg = EmailMessage(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            email_to,
        )
        msg.content_subtype = "html"
        msg.send()
        print("email send ", subject)
        return True
    except Exception as e:
        print("error  email send ", e)
        return False
