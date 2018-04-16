import paramiko

import ntplib
import logging
import os
import sys
import re
import inspect
from datetime import datetime
import paramiko
import zipfile

from datetime import datetime, timezone
from src.env_conf import settings
from src.util import HostSession

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

    def configure_logging(self, logger, level='info'):
        """

        """
        try:
            threshold = settings.getValue('COMPRESSION_THRESHOLD')

            filename = settings.getValue('LOG_FILE_PREFIX') + re.sub(":", "", self.get_ntp_time()) + '.log'
            log_file = os.path.join(settings.getValue('LOG_DIR'), filename)

            # Make paramiko log to different file as we don't want the paramiko logs in framework log files
            paramiko_logs = os.path.join(settings.getValue('LOG_DIR'), settings.getValue('PARAMIKO_LOG_FILE'))
            paramiko.util.log_to_file(paramiko_logs, level=LOGGING_LEVELS['warning'])

            logger.setLevel(logging.DEBUG)

            formatter = logging.Formatter('%(message)s')

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

    def get_ntp_time(self, format=None):
        """
        Function to get time from NTP server
        :return: datetime in UTC format
        """
        ntp_server = settings.getValue('NTP_SERVER')
        try:
            call = ntplib.NTPClient()
            response = call.request(ntp_server, version=3)
            if format:
                return datetime.fromtimestamp(response.tx_time, timezone.utc).strftime(format)
            return datetime.fromtimestamp(response.tx_time, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        except ntplib.NTPException as ex:
            print("NTPException: ", ex)

    def info(self, message):
        if settings.getValue('LOG_TIME_SOURCE') == 'HOST':
            log_data = {"log_time":self.get_host_time(), "levelname": "INFO", "name": __name__, "message":message}
        elif settings.getValue('LOG_TIME_SOURCE') == 'NTP':
            log_data = {"log_time": self.get_ntp_time(), "levelname": "INFO", "name": __name__, "message": message}
        else:
            print("Invalid value for configuration parameter LOG_TIME_SOURCE. Valid values: ['HOST', 'NTP']")
            sys.exit(0)
        logging.getLogger().info('%(log_time)s [%(levelname)-8s]: (%(name)s) - %(message)s' % log_data)

    def debug(self, message):
        if settings.getValue('LOG_TIME_SOURCE') == 'HOST':
            log_data = {"log_time":self.get_host_time(), "levelname": "DEBUG", "name": __name__, "message":message}
        elif settings.getValue('LOG_TIME_SOURCE') == 'NTP':
            log_data = {"log_time": self.get_ntp_time(), "levelname": "DEBUG", "name": __name__, "message": message}
        else:
            print("Invalid value for configuration parameter LOG_TIME_SOURCE. Valid values: ['HOST', 'NTP']")
            sys.exit(0)
        logging.getLogger().debug('%(log_time)s [%(levelname)-8s]: (%(name)s) - %(message)s' % log_data)

    def error(self, message):
        if settings.getValue('LOG_TIME_SOURCE') == 'HOST':
            log_data = {"log_time":self.get_host_time(), "levelname": "ERROR", "name": __name__, "message":message}
        elif settings.getValue('LOG_TIME_SOURCE') == 'NTP':
            log_data = {"log_time": self.get_ntp_time(), "levelname": "ERROR", "name": __name__, "message": message}
        else:
            print("Invalid value for configuration parameter LOG_TIME_SOURCE. Valid values: ['HOST', 'NTP']")
            sys.exit(0)
        logging.getLogger().error('%(log_time)s [%(levelname)-8s]: (%(name)s) - %(message)s' % log_data)

    def warning(self, message):
        if settings.getValue('LOG_TIME_SOURCE') == 'HOST':
            log_data = {"log_time":self.get_host_time(), "levelname": "WARNING", "name": __name__, "message":message}
        elif settings.getValue('LOG_TIME_SOURCE') == 'NTP':
            log_data = {"log_time": self.get_ntp_time(), "levelname": "WARNING", "name": __name__, "message": message}
        else:
            print("Invalid value for configuration parameter LOG_TIME_SOURCE. Valid values: ['HOST', 'NTP']")
            sys.exit(0)
        logging.getLogger().warning('%(log_time)s [%(levelname)-8s]: (%(name)s) - %(message)s' % log_data)

    def critical(self, message):
        if settings.getValue('LOG_TIME_SOURCE') == 'HOST':
            log_data = {"log_time": self.get_host_time(), "levelname": "CRITICAL", "name": __name__, "message": message}
        elif settings.getValue('LOG_TIME_SOURCE') == 'NTP':
            log_data = {"log_time":self.get_ntp_time(), "levelname": "CRITICAL", "name": __name__, "message":message}
        else:
            print("Invalid value for configuration parameter LOG_TIME_SOURCE. Valid values: ['HOST', 'NTP']")
            sys.exit(0)
        logging.getLogger().critical('%(log_time)s [%(levelname)-8s]: (%(name)s) - %(message)s' % log_data)

    def exception(self, message):
        if settings.getValue('LOG_TIME_SOURCE') == 'HOST':
            log_data = {"log_time": self.get_host_time(), "levelname": "ERROR", "name": __name__, "message": message}
        elif settings.getValue('LOG_TIME_SOURCE') == 'NTP':
            log_data = {"log_time":self.get_ntp_time(), "levelname": "ERROR", "name": __name__, "message":message}
        else:
            print("Invalid value for configuration parameter LOG_TIME_SOURCE. Valid values: ['HOST', 'NTP']")
            sys.exit(0)
        logging.getLogger().exception('%(log_time)s [%(levelname)-8s]: (%(name)s) - %(message)s' % log_data)

    def get_host_time(self):
        """
        Function returns current ESXi host datetime as string
        :return: (str) Host datetime in string format(%Y-%m-%dT%H:%M:%SZ)
        """
        client = paramiko.SSHClient()
        # client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        _HOST_DETAILS = settings.getValue("HOST_DETAILS")[0]
        client.connect(_HOST_DETAILS["HOST"], username=_HOST_DETAILS["USER"], password=_HOST_DETAILS["PASSWORD"])
        stdin, stdout, stderr = client.exec_command("esxcli system time get")
        output = stdout.read().decode().strip('\n')
        client.close()
        return output

    def find_in_logs(self, files=(), *args):
        pass

    def get_log_files(self):
        log_dir = settings.getValue('LOG_DIR')
        file_prefix = settings.getValue('LOG_FILE_NAME')
        file_paths = os.listdir(log_dir)
        file_paths = [os.path.join(log_dir, x) for x in file_paths]
        regex = re.compile("^([a-z][A-Z])?.*\.log$")
        # filter to get only those that are a files, with a leading
        # digit and end in '.conf'
        file_paths = [x for x in file_paths if os.path.isfile(x) and os.path.basename(x).startswith(file_prefix) and
                      os.path.basename(x).endswith('.log')]

        # load settings from each file in turn
        filenames = [os.path.basename(x) for x in file_paths]
        file_created = [datetime.fromtimestamp((os.path.getctime(x))).strftime('%Y-%m-%dT%H:%M:%SZ') for x in file_paths]
        file_last_modified = [datetime.fromtimestamp((os.path.getmtime(x))).strftime('%Y-%m-%dT%H:%M:%SZ') for x in file_paths]
        return {"filename": filenames, "file created": file_created, "last modified": file_last_modified}

    def make_zipfile(self, source_dir, output_filename):
        print(output_filename)
        try:
            zout = zipfile.ZipFile(output_filename, "a", zipfile.ZIP_DEFLATED)
            for fname in os.listdir(source_dir):
                if os.path.isfile(os.path.join(source_dir, fname)) and fname.endswith('.log'):
                    print(f"writing: {fname} to {zout.filename}")
                    zout.write(os.path.join(source_dir, fname), os.path.basename(os.path.join(source_dir, fname)))
            zout.close()
        except FileNotFoundError as f:
            print(f'FileNotFoundError: {f.filename} {f.args}')
            sys.exit(0)