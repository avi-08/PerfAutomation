import json, openpyxl
from prettytable import PrettyTable
from src.env_conf import settings
from src.util import ParserUtil, LogUtil
import os
# from os.path import isfile, join
settings.load_from_dir(os.path.join(os.path.dirname(os.path.realpath(__file__))))

_LOGGER = LogUtil.LogUtil()


class Report:
    def __init__(self):
        pass

    def sys(self, workbook=None, worksheet=None, f_netstats=None, f_schedstats=None, file_name=None, print_flag=True):
        _LOGGER.info(f'Parsing data for SYS')
        # wb = openpyxl.load_workbook(file_name)
        ws = workbook.create_sheet(worksheet)
        theJSON = json.load(f_netstats)
        if "hostname" in theJSON["sysinfo"]:
            if print_flag:
                print("Sys stats for " + theJSON["sysinfo"]["hostname"])
            for stat in theJSON["stats"]:  # Traversing a list
                if print_flag:
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
        if print_flag:
            print(table)
            print("Entires with exclussive affinity")
            print(table_exclaff)
        print(f' - saving worksheet as {worksheet} in {file_name}')

    def vcpus(self, workbook=None, worksheet=None, f_netstats=None, f_schedstats=None, file_name=None, print_flag=True):
        _LOGGER.info(f'Parsing data for vCPUs')
        worksheet = 'vcpus'
        ws = workbook.create_sheet(worksheet)
        theJSON = json.load(f_netstats)
        if "hostname" in theJSON["sysinfo"]:
            if print_flag:
                print("CPU stats for " + theJSON["sysinfo"]["hostname"])
            for stat in theJSON["stats"]:  # Traversing a list
                if print_flag:
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
                if print_flag:
                    print(table)
                    print("entries with exclaff")
                    print(table_exclaff)
        print(f' - saving worksheet as {worksheet} in {file_name}')

    def vm_stats(self, workbook=None, worksheet=None, f_netstats=None, f_schedstats=None, file_name=None, print_flag=True):
        _LOGGER.info(f'Parsing data for VM_stats')
        worksheet = 'VM_stats'
        ws = workbook.create_sheet(worksheet)
        theJSON = json.load(f_netstats)
        if "hostname" in theJSON["sysinfo"]:
            if print_flag:
                print(f'VM stats for {theJSON["sysinfo"]["hostname"]} \tpps=Packets Per Second\teps=Errors per Second')
        for stat in theJSON["stats"]:
            if print_flag:
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
        if print_flag:
            print(table)
        print(f' - saving worksheet as {worksheet} in {file_name}')

    def check_drop(self, workbook=None, worksheet=None, f_netstats=None, f_schedstats=None, file_name=None, print_flag=True):
        _LOGGER.info(f'Parsing data for Check Drop')
        # workbook = openpyxl.load_workbook(file_name)
        ws = workbook.create_sheet(worksheet)
        theJSON = json.load(f_netstats)
        if "hostname" in theJSON["sysinfo"]:
            hdata = "Stats for " + theJSON["sysinfo"]["hostname"] + "\tpps=Packets Per Second\teps=Errors per Second"
            if print_flag:
                print(hdata)
            for stat in theJSON["stats"]:
                if print_flag:
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
        if print_flag:
            print(table)
        print(f' - saving worksheet as {worksheet} in {file_name}')

    def check_txrx_threads(self, workbook=None, worksheet=None, f_netstats=None, f_schedstats=None, file_name=None, print_flag=True):
        # wb = openpyxl.load_workbook(file_name)
        _LOGGER.info(f'Parsing data for Check Tx and Rx ')
        ws = workbook.create_sheet(worksheet)
        theJSON = json.load(f_netstats)
        if "hostname" in theJSON["sysinfo"]:
            if print_flag:
                print("Threads inventory for " + theJSON["sysinfo"]["hostname"])
            for stat in theJSON["stats"]:  # Traversing a list
                if print_flag:
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
        if print_flag:
            print(table)
            print("Entries with exclusve affinity")
            print(table_exclaff)
        print(f' - saving worksheet as {worksheet} in {file_name}')

    def exclaff(self, workbook=None, worksheet=None, f_netstats=None, f_schedstats=None, file_name=None, print_flag=True):
        _LOGGER.info(f'Parsing data for Exclaff')
        ws = workbook.active
        ws.title = worksheet
        ws['A1'] = 'Scheduler stats'
        sched_stats_file = f_schedstats
        theJSON = json.load(f_netstats)
        ws.append(['\n'])
        if "hostname" in theJSON["sysinfo"]:
            if print_flag:
                print("vCPU affinity info for " + theJSON["sysinfo"]["hostname"])
            for stat in theJSON["stats"]:
                if print_flag:
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
        if print_flag:
            print(table)
        ws.append(['\n'])
        import pandas as pd
        df = pd.read_table(sched_stats_file, sep='\s+')
        thread_dict = {}
        head = ['Cpu', 'Name', 'Node', 'Thread']
        ws.append(head)
        table_sched = PrettyTable(head)
        if print_flag:
            print("Scheduler stats")
        for idx, thread in enumerate(df.exclusiveTo):
            if not (thread == 0):
                temp = [str(df.cpu[idx]), str(thread), str(df.node[idx]), thread]
                table_sched.add_row(temp)
                ws.append(temp)
                thread_dict[thread] = {'cpu': str(df.cpu[idx]), 'node': str(df.node[idx])}
        ws.append(['\n'])
        if print_flag:
            print(table_sched)
        print(f' - saving worksheet as {worksheet} in {file_name}')

    def nic_inventory(self, workbook=None, worksheet=None, f_netstats=None, f_schedstats=None, file_name=None, print_flag=True):
        # wb = openpyxl.load_workbook(file_name)
        _LOGGER.info(f'Parsing data for Nic Inventory')
        ws = workbook.create_sheet(worksheet)
        theJSON = json.load(f_netstats)
        if "hostname" in theJSON["sysinfo"]:
            if print_flag:
                print("Stats for " + theJSON["sysinfo"]["hostname"])
            for stat in theJSON["stats"]:
                if print_flag:
                    print("Iteration Number=" + str(stat["iteration"]))
            temp = ['Port', 'switch', 'txpps', 'txmbps', 'rxpps', 'rxmbps']
            table = PrettyTable(temp)
            ws.append(temp)
        for port in stat["ports"]:
            temp = [port["name"], port["switch"], port["txpps"], port["txmbps"], port["rxpps"], port["rxmbps"]]
            table.add_row(temp)
            ws.append(temp)
        if print_flag:
            print(table)
        print(f' - saving worksheet as {worksheet} in {file_name}')

    def nic_stats(self, workbook=None, worksheet=None, f_netstats=None, f_schedstats=None, file_name=None, print_flag=True):
        _LOGGER.info(f'Parsing data for Nic Status')
        # wb = openpyxl.load_workbook(file_name)
        ws = workbook.create_sheet(worksheet)
        theJSON = json.load(f_netstats)
        if "hostname" in theJSON["sysinfo"]:
            if print_flag:
                print("Stats for " + theJSON["sysinfo"]["hostname"] + "pps=Packets Per Second")
        for stat in theJSON["stats"]:
            if print_flag:
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
        if print_flag:
            print(table)
        print(f' - saving worksheet as {worksheet} in {file_name}')

    def get_excel(self, print_flag=True):
        print(f' - Creating a Excel Workbook.')
        _LOGGER.info(f'Creating a WorkBook')
        wb = openpyxl.Workbook()
        print(f' - opening Net-stats and Sched-stats..')
        print(f' - Parsing Net-stats and Sched-stats')
        print('-'*60, sep='\n')
        _LOGGER.info(f'opening the netstat and schedstats logs.')
        ns = 'server_netstats.logs'
        ss = 'server_schedstats.logs'
        # ns = 'netstats(10.110.209.156-64B).log'
        # ss = 'schedstats(10.110.209.156-64B).log'
        filename = 'excel_dump.xlsx'
        path = os.path.dirname(os.path.abspath(__file__))
        # files = [f for f in listdir(path) if isfile(join(path, f))]
        # print(files)
        _LOGGER.info(f'Create a worksheet for Exclaff')
        self.exclaff(workbook=wb, worksheet="exclaff", f_netstats=open(ns), f_schedstats=open(ss),
                        file_name=filename, print_flag=print_flag)
        _LOGGER.info(f'Create a worksheet for Check Drop')
        self.check_drop(workbook=wb, worksheet="check drop", f_netstats=open(ns), f_schedstats=open(ss),
                           file_name=filename, print_flag=print_flag)
        _LOGGER.info(f'Create a worksheet for Check Tx Rx')
        self.check_txrx_threads(workbook=wb, worksheet="Check TxRx", f_netstats=open(ns), f_schedstats=open(ss),
                                   file_name=filename,print_flag=print_flag)
        _LOGGER.info(f'Create a worksheet for Nic Inventory.')
        self.nic_inventory(workbook=wb, worksheet="NIC inventory", f_netstats=open(ns), f_schedstats=open(ss),
                              file_name=filename, print_flag=print_flag)
        _LOGGER.info(f'Create a worksheet for Nic Status')
        self.nic_stats(workbook=wb, worksheet="Nic Stats", f_netstats=open(ns), f_schedstats=open(ss),
                          file_name=filename, print_flag=print_flag)
        _LOGGER.info(f'Create a worksheet for Sys')
        self.sys(workbook=wb, worksheet="SYS", f_netstats=open(ns), f_schedstats=open(ss), file_name=filename, print_flag=print_flag)
        _LOGGER.info(f'Create a worksheet for VM Stats')
        self.vm_stats(workbook=wb, worksheet="VM Stats", f_netstats=open(ns), f_schedstats=open(ss),
                         file_name=filename, print_flag=print_flag)
        _LOGGER.info(f'Saving the Excel in {filename}')
        wb.save(filename)
        print(f' - Saving the Excel in {filename}')