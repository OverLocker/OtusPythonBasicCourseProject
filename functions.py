import shutil
import socket
import yaml

import requests
from datetime import datetime, time
from loguru import logger

from global_vars import *
from HOSTNAME import HOSTNAME

checks = {
    "license": True,
    "disk_space": True,
    "luna": True,
    "main_db": True,
    "atto_socket": True,
    "terminal": True,
    "synchronizer": True,
    "translator": True
}

main_db_errors = 0
atto_socket_errors = 0
terminal_errors = 0
sychronizer_errors = 0

def is_within_work_hours(check_time=None):
    work_start = time(check_start_time)
    work_end = time(check_end_time)
    if check_time is None:
        check_time = datetime.now().time()
    return work_start <= check_time <= work_end

def get_external_ip(external_ip_get_domain):
    try:
        my_external_ip = requests.get(external_ip_get_domain, timeout=5).text
        return my_external_ip
    except Exception as e:
        logger.error(f'Error getting external ip: {e}')
        return None

def get_my_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(default_timeout)
    try:
        s.connect(('10.254.254.254', 1))
        local_ip = s.getsockname()[0]
    except Exception as e:
        local_ip = '127.0.0.1'
        logger.info(f'Error getting local ip: {e}')
    finally:
        s.close()
    return local_ip

def check_space(paths: list, external_ip: str, local_ip: str,  ):
    for path in paths:
        try:
            total, used, free = shutil.disk_usage(path)
            used_percent = int(round((used / total) * 100))
            if used_percent > disk_space_allowed_percent and checks["disk_space"]:
                reason = f'Disk space error OCCURED on:'
                checks["disk_space"] = False
                send_message(local_ip = local_ip, external_ip = external_ip, reason = reason, comment=f'{path=}')
        except Exception as e:
            logger.error(f'Error checking disk space: {e}')

def check_license(license_url: str, local_ip: str, external_ip: str):
    reason = f'License error OCCURED on:'
    try:
        license = requests.get(license_url,timeout=default_timeout).json()
        license_state = license['expiration_time']['is_available']
        if not license_state and checks["license"]:
            checks["license"] = False
            send_message(local_ip = local_ip, external_ip = external_ip, reason = reason)
    except Exception as e:
        logger.error(f'Error while checking license: {e}')
        if checks["license"]:
            send_message(local_ip=local_ip, external_ip=external_ip, reason=reason)
        checks["license"] = False

def check_luna(luna_addr, local_ip, external_ip):
    reason = f'Luna Error error OCCURED on:'
    try:
        luna_ok = requests.get(url= luna_addr, timeout=default_timeout).json()
        if not luna_ok and checks["luna"]:
            checks["luna"] = False
            send_message(local_ip=local_ip, external_ip=external_ip, reason=reason)
    except Exception as e:
        checks["luna"] = False
        logger.error(f'Error  while checking Luna: {e}')
        send_message(local_ip=local_ip, external_ip=external_ip, reason=reason)

def check_main_db(main_db_addr, main_db_port, local_ip, external_ip):
    reason = f'Main DB connection error OCCURED on:'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(default_timeout)
    global main_db_errors
    try:
        s.connect((main_db_addr, main_db_port))
        checks["main_db"] = True
        main_db_errors = 0
        s.shutdown(default_shutdown)
    except Exception as e:
        logger.error(f'Error  while connecting to MainDB: {e}')
        main_db_errors += 1
        if main_db_errors == max_errors:
            send_message(local_ip=local_ip, external_ip=external_ip, reason=reason)
        checks["main_db"] = False
    finally:
        s.close()

def check_terminals(terminal_ips_file, local_ip, external_ip):
    reason = f'Terminal connection error OCCURED on:'
    result = []
    global terminal_errors
    for terminal in open(terminal_ips_file).read().splitlines():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(default_timeout)
            s.connect((terminal, int(80)))
            result.append('True')
        except Exception as e:
            logger.error(f'Error  while connecting to terminal {terminal}: {e}')
            result.append('False')
            checks["terminal"] = False
        if 'False' in result:
            checks["terminal"] = False
            terminal_errors += 1
        if not 'False' in result:
            checks["terminal"] = True
            terminal_errors = 0
        if terminal_errors == max_terminal_errors:
            send_message(local_ip=local_ip, external_ip=external_ip, reason=reason, comment=f'{terminal=}')

def check_translator(local_ip, external_ip):
    reason = f'Translator error OCCURED on:'
    url = f'http://{local_ip}:{translator_port}'
    try:
        attempt = requests.get(url=url, timeout = default_timeout).json()
        if attempt:
            checks["translator"] = True
    except Exception as e:
        logger.error(f'Error  while checking translator: {e}')
        if checks["translator"]:
            send_message(local_ip=local_ip, external_ip=external_ip, reason=reason)
        checks["translator"] = False

def check_synchronizer(local_ip, external_ip):
    reason = f'Synchronizer error OCCURED on:'
    url = f'http://{local_ip}:{synchronizer_port}'
    try:
        attempt = requests.get(url=url, timeout = default_timeout).json()
        if attempt:
            checks["synchronizer"] = True
    except Exception as e:
        logger.error(f'Error  while checking synchronizer: {e}')
        if checks["synchronizer"]:
            send_message(local_ip=local_ip, external_ip=external_ip, reason=reason)
        checks["synchronizer"] = False

def get_atto_socket_connection_data(translator_config):
    with open(translator_config, 'r') as config_file:
        all_data = yaml.safe_load(config_file)
        atto_socket = (all_data["socket"]["host"], all_data["socket"]["port"])
    return atto_socket

def check_atto_socket(atto_socket: tuple, local_ip: str, external_ip: str):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(default_timeout)
    reason = f'Atto socket error OCCURED on:'
    global max_atto_socket_errors
    try:
        s.connect((atto_socket[0], int(atto_socket[1])))
        checks["atto_socket"] = True
        max_atto_socket_errors = 0
    except:
        max_atto_socket_errors += 1
        checks["atto_socket"] = False
        if max_atto_socket_errors == max_errors:
            send_message(local_ip=local_ip, external_ip=external_ip, reason=reason)
    finally:
        s.close()

def send_message(local_ip, external_ip, reason, HOSTNAME = HOSTNAME,
                 tg_url = tg_url, chat_id = CHAT_ID, comment = None):
        message = f'''{reason}
                                    {HOSTNAME=},
                                    {local_ip=},
                                    {external_ip=}
                                    {f'comment: {comment}'}'''
        if message_type == "console":
            logger.info(message)
        if message_type == "telegram":
            logger.info(message)
            requests.get(tg_url, json={'text': message, 'chat_id': chat_id})

