import uuid
import sys
import random
import string
import re
from os.path import basename
import os



def generate_random_code(prefix:str="D", code_length:int=5):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(code_length))

def generate_barcode(prefix:str="P",):
    random_number = ''.join(random.choices('0123456789', k=10))
    return f'{prefix}{random_number}'

def getId(prefix: str = "") -> str:
    return f'{prefix}{uuid.uuid4().hex}'


def generate_ticket_no(cid: str = '0', company_name: str = '') -> str:
    if cid is None:
        return f'{company_name}00001'
    if len(cid) == 1:
        return f'{company_name}0000{cid}'
    elif len(cid) == 2:
        return f'{company_name}000{cid}'
    elif len(cid) == 3:
        return f'{company_name}00{cid}'
    elif len(cid) == 4:
        return f'{company_name}0{cid}'
    else:
        return f'{company_name}{cid}'


def Syserror(e):
    exception_type, exception_object, exception_traceback = sys.exc_info()
    filename = exception_traceback.tb_frame.f_code.co_filename
    line_number = exception_traceback.tb_lineno
    print("ERROR --> Mesaage: ", e)
    print("ERROR --> Exception type: ", exception_type)
    print("ERROR --> File name: ", filename)
    print("ERROR --> Line number: ", line_number)
    return None

def extract_sheet_number(filename):
    match = re.search(r'SH(\d+)', filename)
    if match:
        sheet_number = int(match.group(1))
        return sheet_number
    return 1

def validate_file_name(file_name):
    pattern = r'^((PDR|CDBR|RS|PS|FDR|MISC)-\d+SH\d*|(PDR|CDBR|RS|PS|FDR|MISC)-\d+)$'
    if re.match(pattern, file_name):
        return True
    else:
        return False
    
def extract_drawing_type_number(file_name):
    # Define the patterns using regular expressions
    drawing_type_pattern = r'(PDR|CDBR|RS|PS|FDR|MISC)'
    drawing_number_pattern = r'-(.*?)(SH\d+)?$'  # Exclude the SH{some number} pattern if it exists at the end
    # Extract drawing type
    drawing_type_match = re.search(drawing_type_pattern, file_name)
    drawing_type = drawing_type_match.group(1) if drawing_type_match else None
    # Extract drawing number
    drawing_number_match = re.search(drawing_number_pattern, file_name)
    drawing_number = drawing_number_match.group(1) if drawing_number_match else None
    return drawing_type, drawing_number

def check_duplicate_drawing(drawing_data, target_drawing_type, target_drawing_number):
    # Count occurrences of the target drawing type and number in the drawing data
    count = sum(1 for item in drawing_data if item["drawing_type"] == target_drawing_type and item["drawing_number"] == target_drawing_number)
    # Return True if more than one occurrence is found
    return count > 1

def parse_user_agent(request):
    # Initialize variables for OS, browser, and device
    os = ''
    browser = ''
    device = ''
    user_agent_string = request.META.get('HTTP_USER_AGENT', None)
    # Detect operating system
    if 'Windows' in user_agent_string:
        os = 'Windows'
    elif 'Linux' in user_agent_string:
        os = 'Linux'
    elif 'Macintosh' in user_agent_string:
        os = 'Macintosh'
    elif 'Android' in user_agent_string:
        os = 'Android'
    elif 'iOS' in user_agent_string:
        os = 'iOS'
    # Add more conditions for other operating systems as needed
    # Detect browser
    if 'Chrome' in user_agent_string:
        browser = 'Chrome'
    elif 'Firefox' in user_agent_string:
        browser = 'Firefox'
    elif 'Safari' in user_agent_string:
        browser = 'Safari'
    elif 'Edge' in user_agent_string:
        browser = 'Edge'
    elif 'Opera' in user_agent_string:
        browser = 'Opera'
    # Add more conditions for other browsers as needed
    # Detect device
    if 'Mobile' in user_agent_string:
        device = 'Mobile'
    elif 'Tablet' in user_agent_string:
        device = 'Tablet'
    elif 'Windows NT' in user_agent_string:  # Assuming it's a desktop if not Mobile or Tablet
        device = 'Desktop'
    # Add more conditions for other devices as needed
    client_ip = request.META.get('REMOTE_ADDR', None)
    # If REMOTE_ADDR is not available, try X-Forwarded-For header (commonly used when behind proxies)
    if not client_ip:
        client_ip = request.META.get('HTTP_X_FORWARDED_FOR', '')
        client_ip = client_ip.split(',')[0].strip()
    return f"{f'OS-{os}' if os else''} {f'Browser-{browser}' if browser else''} {f'Device-{device}' if device else''} {f'IP-{client_ip}' if client_ip else ''}"



def check_valid_version(string):
    try:
        float_value = float(string)
        int_value = int(float_value)  # Try converting to int to check if it's an integer
        if int_value <= 0:
            return False
        return True
    except ValueError:
        return False
    
def find_corresponding_dwg(tif_pdf_file_name, dwg_files):
        for dwg_file in dwg_files:
            file_name = dwg_file.name
            if file_name.startswith(tif_pdf_file_name) and (file_name.endswith('.dwg') or file_name.endswith('.DWG')):
                return dwg_file
        return None
    
def exist_corresponding_tif_pdf(dwg_file_name, all_files):
    posiible_file_name = [f'{dwg_file_name}.{ext}' for ext in ["PDF", "pdf", "TIF", "tif", "TIFF", "tiff"]]
    is_exist = False
    for file in all_files:
        file_name = file.name
        extension = file_name.split(".")[-1].upper()  # Get the last extension (case-insensitive)
        if extension == "DWG":
            continue
        if file_name in posiible_file_name:
            is_exist = True
            break 
    return is_exist

def is_delete_drawing_file(old_sheet_no, new_sheet_no):
    if old_sheet_no == new_sheet_no:
        return False
    elif old_sheet_no > 1 and new_sheet_no > 1:
        return False
    return True

def get_file_name(file_path):
    if file_path:
        return basename(file_path)
    return None

def get_only_file_name(filename):
    name, extension = os.path.splitext(filename)
    return name

def get_file_name_and_extension(filename):
    name, extension = os.path.splitext(filename)
    return name, extension[1:].upper() 


def check_file(file_list, file):
    newfile = None
    for i in file_list:
        if i.name == file:
            newfile = i
    return newfile

