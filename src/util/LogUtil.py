from datetime import datetime, timezone

import ntplib


def get_ntp_time():
    """
    Function to get time from NTP server for logging
    :return: datetime in UTC format
    """
    ntp_server = '10.107.182.200'
    try:
        call = ntplib.NTPClient()
        response = call.request(ntp_server, version=3)
        return datetime.fromtimestamp(response.tx_time, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except ntplib.NTPException as ex:
        print("NTPException: ", ex)

