import paramiko

import ntplib
import logging
import os
import sys
import time

from datetime import datetime, timezone
from src.env_conf import settings

LOGGING_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}


class LogUtil:
    def __init__(self):
        pass

    @staticmethod
    def configure_logging(self, logger, level='info'):
        """

        """
        try:
            filename = settings.getValue('LOG_FILE_NAME') + time.strftime("%Y-%m-%dT%H%M%S") + '.log'
            log_file = os.path.join(settings.getValue('LOG_DIR'), filename)

            # Make paramiko log to different file as we don't want the paramiko logs in framework log files
            paramiko_logs = os.path.join(settings.getValue('LOG_DIR'), settings.getValue('PARAMIKO_LOG_FILE'))
            paramiko.util.log_to_file(paramiko_logs, level=LOGGING_LEVELS['warning'])

            logger.setLevel(logging.DEBUG)

            formatter = logging.Formatter('%(asctime)s [%(levelname)-8s]: (%(name)s) - %(message)s', datefmt='%Y-%m-%dT%H:%M:%SZ')

            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setLevel(LOGGING_LEVELS[level])
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

            file_handler = logging.FileHandler(filename=log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except FileNotFoundError as f:
            print(f'File not found error: {f.filename}, {f.args[1]} ')

    @staticmethod
    def get_ntp_time(self):
        """
        Function to get time from NTP server
        :return: datetime in UTC format
        """
        ntp_server = settings.getValue('NTP_SERVER')
        try:
            call = ntplib.NTPClient()
            response = call.request(ntp_server, version=3)
            return datetime.fromtimestamp(response.tx_time, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        except ntplib.NTPException as ex:
            print("NTPException: ", ex)
