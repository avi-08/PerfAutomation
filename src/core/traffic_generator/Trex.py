from src.util import HostSession
import json, threading
import logging
from src.tools import Monitoring
from src.env_conf import settings

_LOGGER = logging.getLogger(__name__)

class Trex:

    def __init__(self):
        self.result_data = {
            "framesizes": [],
            "throughput": [],
            "mpps": [],
            "gbps": [],
            "rx": [],
            "tx": []
        }

    def monitorTest(self, client, frameSize=False):

        if frameSize:
            _LOGGER.info(f'Executing the script trex_automated.py with {frameSize}')
            stdin, stdout, stderr = client.exec_command(f'python /home/trex/trex_client/stl/trex_monitor.py tc-1.1 {frameSize}')
            a = stdout.read().decode()
            _LOGGER.info(f'Results from the tRex with frame size {frameSize} :\n {a}')
            print(a)
        else:
            stdin, stdout, stderr = client.exec_command(f'python /home/trex/trex_client/stl/trex_automated.py tc-1.1 ')
            a = stdout.read().decode()
            _LOGGER.info(f'Results from the tRex \n {a}')
            print(a)

    def get_rx_thread(self,netstats):
        data = netstats['stats'][0]['sys']
        for key in data:
            if data[key]['used'] > 80:
                self.result_data['rx'].append(data[key]['used'])
                break

    def get_data_dict(self, filepath):
        content = filepath.split('\n')
        tab = 0
        """
        result_data = {
                    "framesizes": [],
                    "throughput" : [],
                    "mpps": [],
                    "gbps": [],
                    "rx": [],
                    "tx": []
        }
        """
        total = [] * 6
        count = 0
        str1 = ""
        print(content)
        """
        netstats = eval(Monitoring.getNetStats(client, 'netstats.logs'))
        print(netstats)
        schedstats = Monitoring.getSchedStats(client, 'scstats.logs')
        for x in netstats['stats']:
            print (x)
            if x == 'sys':
                for data in x:
                    print(data)
                    if data['used'] >= 0.0:
                        print (data['used'])
                        result_data['rx'].append(data['used'])
                        break
        """
        for line in content:
            if line.startswith("+") and tab == 0:
                tab = 1
            elif line.startswith("+") and tab == 1:
                tab = 2
            elif line.startswith("+") and tab == 2:
                data = str1.split("|")[1:-1]
                self.result_data['framesizes'].append(int(data[1]))
                self.result_data['throughput'].append(100 * float(data[8]) / 1.19)
                self.result_data['mpps'].append(float(data[8]))
                self.result_data['gbps'].append(float(data[10]))
                tab = 0
            elif line.startswith("|") and tab == 2:
                str1 = line
        return self.result_data


    def trafficGen(self):
        _LOGGER.info('Initating tRex...')
        trafficGen = json.load(open(r'env_conf\trafficGen.json'))
        host = json.load(open(r'env_conf\host.json'))
        trafficGen = trafficGen['TREX']
        host = host['HOST_DETAILS']
        print(host)
        client = HostSession.HostSession().connect(trafficGen['IP'], trafficGen['USERNAME'], trafficGen['PASSWORD'], False)
        self.monitorTest(client)
        file_data = self.get_data_dict(Monitoring.getTraffic(client, 'tc-1.1.txt'))
        # print(Monitoring.getTraffic(client, '/home/trex/Results/tc-1.1.txt'))
        _LOGGER.info(f'{file_data}')
        hosts = settings.getValue('HOST_DETAILS')
        for host in hosts:
            client2 = HostSession.HostSession().connect(host['HOST'], host['USER'], host['PASSWORD'], False)
            client3 = HostSession.HostSession().connect(host['HOST'], host['USER'], host['PASSWORD'], False)
            for frame in self.result_data['framesizes']:
                _LOGGER.info(f'Running traffic with Frame Size : {frame}')
                self.monitorTest(client, frame)
                t1 = threading.Thread(target=Monitoring.monitorNetStats, args=(client2, 5, 'netstats.logs'))
                t2 = threading.Thread(target=Monitoring.monitorSchedStats, args=(client3, 'scstats.logs'))
                t3 = threading.Thread(target=self.monitorTest, args=(client, frame))
                _LOGGER.info(f'creating the thread for Running traffic with {frame} frame size')
                t3.start()
                _LOGGER.info(f'creating the thread for net-stats -i <duration> -t WicQv -A  > netstats.logs')
                t1.start()
                _LOGGER.info(f'creating the thread for sched-stats -t pcpu-stats > scstats.logs')
                t2.start()
                t3.join()
                t1.join()
                t2.join()
                # temp = Monitoring.getNetStats(client, 'netstats.logs')
                netstats = eval(Monitoring.getNetStats(client2, 'netstats.logs'))
                print(netstats)
                self.get_rx_thread(netstats)
                schedstats = Monitoring.getSchedStats(client3, 'scstats.logs')
                _LOGGER.info(f'Result Data for Graph : {self.result_data}')

        # stdin, stdout, stderr = client.exec_command(f'')

        """
        netstats = eval(getNetStats(client1, 'netstats.logs'))
        schedstats = getSchedStats(client2, 'scstats.logs')
        """