from src.util import HostSession
import json
import logging
import yaml

_LOGGER = logging.getLogger(__name__)

def trafficGen(packet_size=False):
    trafficGen = json.load(open(r'..\env_conf\trafficGen.json'))
    traffic_prf = yaml.load(open(r'..\env_conf\tester-conf.yaml'))
    client = HostSession.HostSession().connect(trafficGen['HOST'], trafficGen['USERNAME'], trafficGen['PASSWORD'],False)
    if packet_size:
        _LOGGER.info(f'Triggering T-Rex automated Test ')
        # _LOGGER.info(f' Getting traffic profile from  : tester-config.yaml')
        stdin, stdout, stderr = client.exec_command(f'python /home/trex/trex_client/stl/trex_automated.py all {packet_size}')
        a = stdout.read().decode()
    else :
        _LOGGER.info(f'Triggering T-Rex automated Test ')
        # _LOGGER.info(f' Getting traffic profile from  : tester-config.yaml')
        stdin, stdout, stderr = client.exec_command(f'python /home/trex/trex_client/stl/trex_automated.py all')
        a = stdout.read().decode()

    _LOGGER.info(f'{a}')
