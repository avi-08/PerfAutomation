import json
import yaml
from src.util import HostSession

class Moniter:
    n_data = {}
    s_data = {}

    def __init__(self):
        self.n_data = {}
        self.s_data ={}
        pass

    def s_stat(client):
        stdin , stdout, stderr = client.exec_command('sched-stats -t pcpu-stats')
        schedStats = stdout.read().decode()
        schedStats.lstrip(' ').rstrip(' ')
        data = re.sub(' +', ' ', schedStats).split('\n')
        mat_list = []
        for i in range(len(data)):
            mat_list.append(data[i].lstrip().rstrip().split(' '))
        print(mat_list)
        return mat_list

    def n_stat(client):
        stdin , stdout, stderr = client.exec_command('net-stats -i 3 -t WicQv -A ')
        a = stdout.read().decode()
        print(a)



def triger():
    hosts = json.load(open(r'env_conf\host.json'))
    for host in hosts['HOST_DETAILS']:
        client = HostSession.HostSession().connect(host['HOST'], host['USER'], host['PASSWORD'], False)
        traffic_prf = yaml.load(open(r'env_conf\tester-conf.yaml'))
        for test in traffic_prf['tester']:
            if 'packet-size' in test and 'flows' in test:
                for pkt_size in test['packet-size']:
                    Moniter.n_data['host']['pkt_size'] = Moniter.n_stat(client)
                    Moniter.s_data['host']['pkt_size'] = Moniter.s_stat(client)

        print(Moniter.n_data)

triger()