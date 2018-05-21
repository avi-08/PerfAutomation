import re
import logging
import json, openpyxl
import sys
from prettytable import PrettyTable
from openpyxl import Workbook

_LOGGER = logging.getLogger(__name__)


class Monitor:
    def __init__(self):
        pass

    def monitor_netstats(self, client, duration, filename):
        stdin, stdout, stderr = client.exec_command(f'net-stats -i {duration} -t WicQv -A > {filename}')
        logging.debug(f'Executing command : net-stats -i {duration} -t WicQv -A > {filename}')
        return stdout.read().decode()

    def monitor_schedstats(self,client, filename):
        stdin, stdout, stderr = client.exec_command(f'sched-stats -t pcpu-stats > {filename}')
        logging.debug(f'Executing command : sched-stats -t pcpu-stats > {filename}')
        return stdout.read().decode()

    def start_monitoring(self,client):
        stdin, stdout, stderr = client.exec_command(f'sudo python ')
        return stdout.read().decode()

    def get_netstats(self, client, filename):
        stdin, stdout, stderr = client.exec_command(f'cat {filename}')
        logging.debug(f'Excuting command : cat {filename}')
        return stdout.read().decode()

    def get_schedstats(self,client, filename):
        stdin, stdout, stderr = client.exec_command(f'cat {filename}')
        logging.debug(f'Excuting command : cat {filename}')
        return stdout.read().decode()

    def get_traffic(self,client, filename):
        stdin, stdout, stderr = client.exec_command(f'cat /home/trex/Results/{filename}')
        logging.debug(f'Excuting command : cat /home/trex/Results/{filename}')
        return stdout.read().decode()

    def ping(self, client, dest):
        stdin, stdout, stderr = client.exec_command(f'ping {dest} -c 4')
        logging.info(f'ping to {dest}')
        logging.debug(f'Excuting command : ping {dest} -c 4 ')
        a = stdout.read().decode()
        a = a.split('\n\n')[1].split('\n')[1].split(',')
        packet_loss = re.search('(.*?%)', a[2]).group().strip().strip('%')
        if int(packet_loss) == 0:
            return True
        else:
            return False
    def start_trex(self,client ):
        stdin, stdout, stderr = client.exec_command(f'./home/trex/t-rex-64 -i -c 1')
        a = stdout.read().decode()
        if a:
            return True
        else:
            return False

    def start_dpdk(self, client):
        stdin, stdout, stderr = client.exec_command(f'./startshell.sh')
        a = stdout.read().decode()
        if a:
            return True
        else:
            return False

    def sys(self, workbook=None, worksheet=None, f_netstats=None, f_schedstats=None, file_name=None):
        # wb = openpyxl.load_workbook(file_name)
        ws = workbook.create_sheet(worksheet)
        theJSON = json.load(f_netstats)
        print('-' * 150, sep='\n')
        if "hostname" in theJSON["sysinfo"]:
            print("Sys stats for " + theJSON["sysinfo"]["hostname"])
            for stat in theJSON["stats"]:  # Traversing a list
                print("Iteration Number=" + str(stat["iteration"]))
            temp = ['Name', 'Id', 'used', 'latencySensitivity', 'exclaff', 'sysoverlap']
            table = PrettyTable(temp)
            ws.append(temp)
            temp1 = ['Name', 'Id', 'used', 'latencySensitivity', 'exclaff', 'sysoverlap']
            table_exclaff = PrettyTable(temp1)
            sys_dict = stat["sys"]
            for sysId, sys_attrib in sys_dict.items():  # Traversing a dictionary
                temp = [sys_attrib["name"], sys_attrib["id"], sys_attrib["used"], sys_attrib["latencySensitivity"],
                        sys_attrib["exclaff"], sys_attrib["sysoverlap"]]
                table.add_row(temp)
                ws.append(temp)
            ws.append(['\n'])
            ws.append(temp1)
            for sysId, sys_attrib in sys_dict.items():
                if not sys_attrib["exclaff"] == -1:
                    temp1 = [sys_attrib["name"], sys_attrib["id"], sys_attrib["used"], sys_attrib["latencySensitivity"],
                             sys_attrib["exclaff"], sys_attrib["sysoverlap"]]
                    table_exclaff.add_row(temp1)
                    ws.append(temp1)
        print(table)
        print("Entires with exclussive affinity")
        print(table_exclaff)
        print(f'saving data as {worksheet} in {file_name}')

    def vcpus(self, workbook=None, worksheet=None, f_netstats=None, f_schedstats=None, file_name=None):
        worksheet = 'vcpus'
        ws = workbook.create_sheet(worksheet)
        theJSON = json.load(f_netstats)
        print('-' * 150, sep='\n')
        if "hostname" in theJSON["sysinfo"]:
            print("CPU stats for " + theJSON["sysinfo"]["hostname"])
            for stat in theJSON["stats"]:  # Traversing a list
                print("Iteration Number=" + str(stat["iteration"]))
                temp = ['Name', 'Id', 'used', 'latencySensitivity', 'exclaff']
                table = PrettyTable(temp)
                ws.append(temp)
                temp1 = ['Name', 'Id', 'used', 'latencySensitivity', 'exclaff']
                table_exclaff = PrettyTable(temp1)
                vcpus_dict = stat["vcpus"]
                for vcpuId, vcpu_attrib in vcpus_dict.items():  # Traversing a dictionary
                    if "latencySensitivity" in vcpu_attrib:  # Some of the CPU stats dont have latency sensitivity and exclaff so need to validate for that
                        latSen = vcpu_attrib["latencySensitivity"]
                        exclaff = vcpu_attrib["exclaff"]
                    else:
                        latSen = "NA"
                        exclaff = "NA"
                    temp = [vcpu_attrib["name"], vcpu_attrib["id"], vcpu_attrib["used"], latSen, exclaff]
                    table.add_row(temp)
                    ws.append(temp)
                ws.append(['\n'])
                ws.append(temp1)
                for vcpuId, vcpu_attrib in vcpus_dict.items():
                    if not exclaff == -1:
                        temp1 = [vcpu_attrib["name"], vcpu_attrib["id"], vcpu_attrib["used"], latSen, exclaff]
                        table_exclaff.add_row(temp1)
                        ws.append(temp1)

                print(table)
                print("entries with exclaff")
                print(table_exclaff)
        print(f'saving data as {worksheet} in {file_name}')

    def vm_stats(self, workbook=None, worksheet=None, f_netstats=None, f_schedstats=None, file_name=None):
        worksheet = 'VM_stats'
        ws = workbook.create_sheet(worksheet)
        theJSON = json.load(f_netstats)
        print('-' * 150, sep='\n')
        if "hostname" in theJSON["sysinfo"]:
            print(f'VM stats for {theJSON["sysinfo"]["hostname"]} \tpps=Packets Per Second\teps=Errors per Second')
        for stat in theJSON["stats"]:
            print(f'Iteration Number= \" {str(stat["iteration"])}\"')
        temp = ['VM Port', 'switch', 'vnic_dev', 'txpps', 'txpps_drv', 'txeps', 'txeps_drv', 'txmbps', 'txmbps_drv',
                'rxpps', 'rxpps_drv', 'rxeps', 'rxeps_drv', 'rxmbps', 'rxmbps_drv']
        table = PrettyTable(temp)
        ws.append(temp)
        for port in stat["ports"]:
            if "vmnic" in port:
                devname = port["vmnic"]["devname"]
                txpps_drv = port["vmnic"]["txpps"]
                txeps_drv = port["vmnic"]["txeps"]
                txmbps_drv = port["vmnic"]["txmbps"]
                rxpps_drv = port["vmnic"]["rxpps"]
                rxeps_drv = port["vmnic"]["rxeps"]
                rxmbps_drv = port["vmnic"]["rxmbps"]
                temp = [port["name"], port["switch"], devname, port["txpps"], txpps_drv, port["txeps"], txeps_drv,
                        port["txmbps"], txmbps_drv, port["rxpps"], rxpps_drv, port["rxeps"], rxeps_drv, port["rxmbps"],
                        rxmbps_drv]
                table.add_row(temp)
                ws.append(temp)
        print(table)
        print(f'saving data as {worksheet} in {file_name}')

    def check_drop(self, workbook=None, worksheet=None, f_netstats=None, f_schedstats=None, file_name=None):
        # workbook = openpyxl.load_workbook(file_name)
        ws = workbook.create_sheet(worksheet)
        theJSON = json.load(f_netstats)
        print('-' * 150, sep='\n')
        if "hostname" in theJSON["sysinfo"]:
            hdata = "Stats for " + theJSON["sysinfo"]["hostname"] + "\tpps=Packets Per Second\teps=Errors per Second"
            print(hdata)
            for stat in theJSON["stats"]:
                print("Iteration Number=" + str(stat["iteration"]))
            temp = ['Port', 'switch', 'vnic_dev', 'txpps', 'txpps_drv', 'txeps', 'txeps_drv', 'txmbps', 'txmbps_drv',
                    'rxpps', 'rxpps_drv', 'rxeps', 'rxeps_drv', 'rxmbps', 'rxmbps_drv']
            table = PrettyTable(temp)
            ws.append(temp)
            for port in stat["ports"]:
                if "vmnic" in port:
                    devname = port["vmnic"]["devname"]
                    txpps_drv = port["vmnic"]["txpps"]
                    txeps_drv = port["vmnic"]["txeps"]
                    txmbps_drv = port["vmnic"]["txmbps"]
                    rxpps_drv = port["vmnic"]["rxpps"]
                    rxeps_drv = port["vmnic"]["rxeps"]
                    rxmbps_drv = port["vmnic"]["rxmbps"]
                    data = [port["name"], port["switch"], devname, port["txpps"], txpps_drv, port["txeps"], txeps_drv,
                            port["txmbps"], txmbps_drv, port["rxpps"], rxpps_drv, port["rxeps"], rxeps_drv,
                            port["rxmbps"], rxmbps_drv]
                    table.add_row(data)
                    ws.append(data)
        print(table)
        print(f'saving data as {worksheet} in {file_name}')

    def check_txrx_threads(self, workbook=None, worksheet=None, f_netstats=None, f_schedstats=None, file_name=None):
        # wb = openpyxl.load_workbook(file_name)
        ws = workbook.create_sheet(worksheet)
        theJSON = json.load(f_netstats)
        print('-' * 150, sep='\n')
        if "hostname" in theJSON["sysinfo"]:
            print("Threads inventory for " + theJSON["sysinfo"]["hostname"])
            for stat in theJSON["stats"]:  # Traversing a list
                print("Iteration Number=" + str(stat["iteration"]))
            temp = ['Port', 'Switch', 'Thread Id', 'Name', 'Usage', 'Ready', 'Cstp', 'latencySen', 'exclaff']
            table = PrettyTable(temp)
            ws.append(temp)
            sys_dict = stat["sys"]
            for port in stat["ports"]:
                if "sys" in port:
                    for thread in port["sys"]:
                        temp = [port["name"], port['switch'], thread, sys_dict[thread]["name"],
                                sys_dict[thread]["used"], sys_dict[thread]["ready"], sys_dict[thread]["cstp"],
                                sys_dict[thread]["latencySensitivity"], sys_dict[thread]["exclaff"]]
                        table.add_row(temp)
                        ws.append(temp)
            ws.append(['\n'])
            ws.append(['Entries with exclusive affinity'])
            temp1 = ['Port', 'Switch', 'Thread Id', 'Name', 'Usage', 'Ready', 'Cstp', 'latencySen', 'exclaff']
            table_exclaff = PrettyTable(temp1)
            ws.append(temp1)
            for port in stat["ports"]:
                if "sys" in port:
                    for thread in port["sys"]:
                        if not sys_dict[thread]["exclaff"] == -1:
                            temp1 = [port["name"], port['switch'], thread, sys_dict[thread]["name"],
                                     sys_dict[thread]["used"], sys_dict[thread]["ready"], sys_dict[thread]["cstp"],
                                     sys_dict[thread]["latencySensitivity"], sys_dict[thread]["exclaff"]]
                            table_exclaff.add_row(temp1)
                            ws.append(temp1)
        print(table)
        print("Entries with exclusve affinity")
        print(table_exclaff)
        print(f'saving data as {worksheet} in {file_name}')

    def exclaff(self, workbook=None, worksheet=None, f_netstats=None, f_schedstats=None, file_name=None):
        ws = workbook.active
        ws.title = worksheet
        ws['A1'] = 'Scheduler stats'
        sched_stats_file = f_schedstats
        theJSON = json.load(f_netstats)
        print('-' * 150, sep='\n')
        ws.append(['\n'])
        if "hostname" in theJSON["sysinfo"]:
            print("vCPU affinity info for " + theJSON["sysinfo"]["hostname"])
            for stat in theJSON["stats"]:
                print("Iteration Number=" + str(stat["iteration"]))
                cpu_state_head = ['Name', 'Id', 'used', 'latencySensitivity', 'vcpu_exclaff']
            ws.append(cpu_state_head)
            table = PrettyTable(cpu_state_head)
            vcpus_dict = stat["vcpus"]
            dat = {}
            for vcpuId, vcpu_attrib in vcpus_dict.items():
                if "latencySensitivity" in vcpu_attrib:
                    latSen = vcpu_attrib["latencySensitivity"]
                    exclaff = vcpu_attrib["exclaff"]
                else:
                    latSen = "NA"
                    exclaff = "NA"
                temp = [vcpu_attrib["name"], vcpu_attrib["id"], vcpu_attrib["used"], latSen, exclaff]
                dat[vcpu_attrib["id"]] = vcpu_attrib["name"]
                ws.append(temp)
                table.add_row(temp)
        print(table)
        ws.append(['\n'])
        import pandas as pd
        df = pd.read_table(sched_stats_file, sep='\s+')
        thread_dict = {}
        head = ['Cpu', 'Name', 'Node', 'Thread']
        ws.append(head)
        table_sched = PrettyTable(head)
        print("Scheduler stats")
        for idx, thread in enumerate(df.exclusiveTo):
            if not (thread == 0):
                temp = [str(df.cpu[idx]), str(dat[thread]), str(df.node[idx]), thread]
                table_sched.add_row(temp)
                ws.append(temp)
                thread_dict[thread] = {'cpu': str(df.cpu[idx]), 'node': str(df.node[idx])}
        ws.append(['\n'])
        print(table_sched)
        print(f'saving data as {worksheet} in {file_name}')

    def nic_inventory(self, workbook=None, worksheet=None, f_netstats=None, f_schedstats=None, file_name=None):
        # wb = openpyxl.load_workbook(file_name)
        ws = workbook.create_sheet(worksheet)
        theJSON = json.load(f_netstats)
        print('-' * 150, sep='\n')
        if "hostname" in theJSON["sysinfo"]:
            print("Stats for " + theJSON["sysinfo"]["hostname"])
            for stat in theJSON["stats"]:
                print("Iteration Number=" + str(stat["iteration"]))
            temp = ['Port', 'switch', 'txpps', 'txmbps', 'rxpps', 'rxmbps']
            table = PrettyTable(temp)
            ws.append(temp)
        for port in stat["ports"]:
            temp = [port["name"], port["switch"], port["txpps"], port["txmbps"], port["rxpps"], port["rxmbps"]]
            table.add_row(temp)
            ws.append(temp)
        print(table)
        print(f'saving data as {worksheet} in {file_name}')

    def nic_stats(self, workbook=None, worksheet=None, f_netstats=None, f_schedstats=None, file_name=None):
        # wb = openpyxl.load_workbook(file_name)
        ws = workbook.create_sheet(worksheet)
        theJSON = json.load(f_netstats)
        print('-' * 150, sep='\n')
        if "hostname" in theJSON["sysinfo"]:
            print("Stats for " + theJSON["sysinfo"]["hostname"] + "pps=Packets Per Second")
        for stat in theJSON["stats"]:
            print("Iteration Number=" + str(stat["iteration"]))
        temp = ['Port', 'Mac', 'switch', 'txpps', 'txeps', 'txmbps', 'txsize', 'txq_cnt', 'rxpps', 'rxeps', 'rxmbps',
                'rxsize', 'rxq_cnt']
        table = PrettyTable(temp)
        ws.append(temp)
        for port in stat["ports"]:
            if "txqueue" in port:
                txq_cnt = port["txqueue"]["count"]
            else:
                txq_cnt = "NA"
            if "rxqueue" in port:
                rxq_cnt = port["rxqueue"]["count"]
            else:
                rxq_cnt = "NA"
            temp = [port["name"], port["mac"], port["switch"], port["txpps"], port["txeps"], port["txmbps"],
                    port["txsize"], txq_cnt, port["rxpps"], port["rxeps"], port["rxmbps"], port["rxsize"], rxq_cnt]
            table.add_row(temp)
            ws.append(temp)
        print(table)
        print(f'saving data as {worksheet} in {file_name}')

    def get_excel(self):
        wb = openpyxl.Workbook()
        ns = 'server_netstats.logs'
        ss = 'server_schedstats.logs'
        filename = 'excel_dump.xlsx'
        self.exclaff(workbook=wb, worksheet="exclaff", f_netstats=open(ns), f_schedstats=open(ss),
                        file_name=filename)
        self.check_drop(workbook=wb, worksheet="check drop", f_netstats=open(ns), f_schedstats=open(ss),
                           file_name=filename)
        self.check_txrx_threads(workbook=wb, worksheet="Check TxRx", f_netstats=open(ns), f_schedstats=open(ss),
                                   file_name=filename)
        self.nic_inventory(workbook=wb, worksheet="NIC inventory", f_netstats=open(ns), f_schedstats=open(ss),
                              file_name=filename)
        self.nic_stats(workbook=wb, worksheet="Nic Stats", f_netstats=open(ns), f_schedstats=open(ss),
                          file_name=filename)
        self.sys(workbook=wb, worksheet="SYS", f_netstats=open(ns), f_schedstats=open(ss), file_name=filename)
        self.vm_stats(workbook=wb, worksheet="VM Stats", f_netstats=open(ns), f_schedstats=open(ss),
                         file_name=filename)
        wb.save(filename)
