from datetime import datetime, timezone

from src.env_conf import settings
import ntplib


def configure_logging(level):
    """

    """
    log_file_default = os.path.join(settings.getValue('LOG_DIR'), settings.getValue('LOG_FILE_DEFAULT'))

    global _LOGGER
    _LOGGER.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s [%(levelname)-8s]: (%(name)s) - %(message)s', datefmt='%Y-%m-%dT%H:%M:%SZ')

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(LOGGING_LEVELS[level])
    stream_handler.setFormatter(formatter)
    _LOGGER.addHandler(stream_handler)

    file_handler = logging.FileHandler(filename=log_file_default)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    _LOGGER.addHandler(file_handler)


def get_ntp_time():
    """
    Function to get time from NTP server for logging
    :return: datetime in UTC format
    """
    ntp_server = settings.getValue('NTP_SERVER')
    try:
        call = ntplib.NTPClient()
        response = call.request(ntp_server, version=3)
        return datetime.fromtimestamp(response.tx_time, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except ntplib.NTPException as ex:
        print("NTPException: ", ex)



