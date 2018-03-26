from src.util import HostSession
import json
import logging
import yaml

_LOGGER = logging.getLogger(__name__)

def trafficGen():
    trafficGen = json.load(open(r'env_conf\trafficGen.json'))
    traffic_prf = yaml.load(open(r'env_conf\tester-conf.yaml'))
    client = HostSession.HostSession().connect(trafficGen['HOST'], trafficGen['USERNAME'], trafficGen['PASSWORD'], False)
    _LOGGER.info(f'Triggering T-Rex automated Test : {a}')
    # _LOGGER.info(f' Getting traffic profile from  : tester-config.yaml')
    stdin, stdout, stderr = client.exec_command('python /home/trex/trex_client/stl/trex_automated.py all')
    a = stdout.read().decode()
    _LOGGER.info(f'{a}')
