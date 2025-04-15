from functions import *
import time
import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)

from global_vars import *

def main():
    #local_ip = get_my_local_ip()
    local_ip = "127.0.0.1" #FOR TEST ONLY
    external_ip = get_external_ip(external_ip_get_domain)
    while True:
        current_time = datetime.now().time()
        logger.info(f'\n{json.dumps(checks, indent=4)}')
        if is_within_work_hours(current_time):
            check_space(paths, local_ip=local_ip, external_ip=external_ip)
            check_license(license_url = license_url, local_ip=local_ip, external_ip=external_ip)
            check_luna(luna_addr = luna_addr, local_ip=local_ip, external_ip=external_ip)
            check_main_db(main_db_addr, main_db_port, local_ip=local_ip, external_ip=external_ip)
            check_terminals(terminal_ips_file,local_ip=local_ip, external_ip=external_ip)
            check_translator(local_ip=local_ip, external_ip=external_ip)
            check_synchronizer(local_ip=local_ip, external_ip=external_ip)
            atto_conn_data = get_atto_socket_connection_data(translator_config)
            check_atto_socket(atto_conn_data, local_ip, external_ip)

            time.sleep(sleep_time)
        else:
            print("Facepay Monitoring: The current time is outside of work hours.")

if __name__ == '__main__':
    main()
