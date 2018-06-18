import argparse
import sys
import os
import re
from prettytable import PrettyTable
from sys import platform

from src.env_conf import settings
from src.util import HostUtil
from src.util import HostSession


class Parser:
    def __init__(self, prog=__file__):
        self.prog = prog
        pass

    def parse_cmd_args(self):
        """
        Function to parse command line arguments
        :return: Dictionary containing command line args
        """
        parser = argparse.ArgumentParser(prog=self.prog, formatter_class=argparse.ArgumentDefaultsHelpFormatter, description='Automation Performance Test Framework')
        parser.add_argument('-s', '--list-settings', action='store', type=str,
                            help='list settings configuration and exit(type "all" to print all settings)',
                            metavar=('SETTING_NAME',))
        parser.add_argument('-v', '--verbose', action='store_true',
                            help='Set verbosity level for console output as DEBUG; default level is INFO')
        parser.add_argument('-e', '--list-env-details', action='store', help="List host details and exit", type=str,
                            choices=['all', 'compact'])
        parser.add_argument('-q', '--list-host-optimizations', action='store_true',
                            help='List current host optimization parameters and exit')
        parser.add_argument('-w', '--host-optimization-type', action='store', type=str,
                            help= 'Specify host configuration type(default=standard), possible values="standard + splittx","standard + splitrx", "standard + rss","standard +\
                             splittx + splitrx " "standard + splittx + rss"',
                            metavar=('CONFIG_TYPE',))
        parser.add_argument('-l', '--list-testcases', action='store_true', help='get a list of testcases')
        parser.add_argument('-g', '--get-testcase', action="store", type=str,
                            help='get details of specified testcase', metavar=('TESTCASE',))
        parser.add_argument('-t', '--testcase', action="store", type=str, metavar=('TESTCASE',),
                            help='Run test for given test case'
                                 '; a comma seperated list for running multiple tests')
        parser.add_argument('-o', '--list-operations', action='store_true',
                            help='get a list of all available operations and exit')
        parser.add_argument('-p', '--perform', action='store', type=str,
                            choices=['host_optimization', 'vm_deploy', 'vm_optimization', 'traffic_config', 'run_traffic',
                                     'monitoring', 'reporting', 'cleanup',],
                            help='Perform given operation; provide ', metavar=('OPERATION',))
        parser.add_argument('-b', '--generate-support-bundle', action='store', type=str, nargs='*'
                            , default=None, help='Generate support bundle dumps. COMMAND(optional): Provide additional commands seperated by "," \
                            other than those present in command.json.', metavar=('COMMAND',))
        parser.add_argument('--dependency-install', action='store_true', help='install all the dependency required.')
        args = vars(parser.parse_args())
        return args

    def get_usecases(self, dirpath):
        files = os.path.join(dirpath, 'usecases')
        print('-'*80, 'Operation\t\t\t\tDescription', '-'*80, sep='\n')
        for file in os.listdir(files):
            filepath = os.path.join(files, file)
            if os.path.isfile(filepath) and not (file.startswith('__') or file.startswith('tech_support')):
                print(f'{re.sub(".py", "", file)}')
        print('-'*80)
        pass

    def process_cmd_switches(self, args):
        """ Process --list cli arguments if needed

        :param args: A dictionary with all CLI arguments
        """
        if args['list_settings']:
            print(str(settings))
            sys.exit(0)
        if args['list_testcases']:
            print(args['list_testcases'])
            if len(settings.getValue('TESTCASES')) > 0:
                #if args['list_testcase'] == 'all':
                for a in settings.getValue('TESTCASES'):
                    print(self.dict_to_table(a, a['NAME'], False))
                    print('\n')
                """
                if args['list_testcase'] == 'single':
                    for a in settings.getValue('TESTCASES'):
                        if a['FLOWTYPE'] == 'single':
                            print(self.dict_to_table(a, a['NAME'], False))
                            print('\n')
                if args['list_testcase'] == 'multiple':
                    for a in settings.getValue('TESTCASES'):
                        if a['FLOWTYPE'] == 'multiple':
                            print(self.dict_to_table(a, a['NAME'], False))
                            print('\n')
                """
            else:
                print("No defined testcases found")
            sys.exit(0)
        if args['get_testcase']:
            data = args['get_testcase'].strip().split('=')
            flag = True
            #for a in settings.getValue('TESTCASES'):
            if len(data) > 1:
                if data[0] == 'flow':
                    if data[1] == 'single':
                        print(f'Searching Testcase with {data[1]} flow')
                        for a in settings.getValue('TESTCASES'):
                            if a['FLOWTYPE'] == 'single':
                                print(self.dict_to_table(a, a['NAME'], False))
                                print('\n')
                                flag = False
                    if data[1] == 'multiple':
                        print(f'Searching Testcase with {data[1]} flow')
                        for a in settings.getValue('TESTCASES'):
                            if a['FLOWTYPE'] == 'multiple':
                                print(self.dict_to_table(a, a['NAME'], False))
                                print('\n')
                                flag = False
                if data[0] == 'vm':
                    print(f'Searching Testcase with {data[1]} virtual machines')
                    for a in settings.getValue('TESTCASES'):
                        if len(a['VM_NAME']) == int(data[1]):
                            print(self.dict_to_table(a, a['NAME'], False))
                            print('\n')
                            flag= False
            else:
                print(f'Searching Testcase with Name : {args["get_testcase"]}')
                for a in settings.getValue('TESTCASES'):
                    if a['NAME'] == args['get_testcase']:
                        print(self.dict_to_table(a, a['NAME'], False))
                        print('\n')
                        flag = False
            if flag:
                print("No defined testcase found.")
            sys.exit(0)

        if args['list_operations']:
            self.get_usecases(os.path.dirname(os.path.dirname(__file__)))
            sys.exit(0)

        if args['list_host_optimizations']:
            print(self.dict_to_table(settings.getValue('ESXI65'), 'HOST optimization settings', False))
            sys.exit(0)
        if args['list_env_details'] == 'all':
            hosts = settings.getValue('HOST_DETAILS')
            print('Environment Details')
            for host in hosts:
                client = HostSession.HostSession().connect(host['HOST'], host['USER'], host['PASSWORD'], False)
                HostUtil.HostUtil().list_env_details(client)
            sys.exit(0)

        if args['list_env_details'] == 'compact':
            hosts = settings.getValue('HOST_DETAILS')
            print('Environment Details compact')
            for host in hosts:
                client = HostSession.HostSession().connect(host['HOST'], host['USER'], host['PASSWORD'], False)
                HostUtil.HostUtil().list_env_detail_compact(client)
            sys.exit(0)

        if args['dependency_install']:
            print(f'pip install -r {os.path.dirname(os.path.abspath(__file__))}/dependency.txt')
            if self.get_os() == 'linux':
                os.system(f'pip install -r {os.path.dirname(os.path.abspath(__file__))}/dependency.txt')
            elif self.get_os() == 'darwin':
                os.system(f'pip install -r {os.path.dirname(os.path.abspath(__file__))}/dependency.txt')
            else:
                # print(self.get_os())
                os.system(f'pip install -r {os.path.dirname(os.path.abspath(__file__))}/dependency.txt')
            sys.exit(0)

    def dict_to_table(self, data, header, row_major=True):
        x = PrettyTable()
        if header:
            x.title = header
        if row_major:
            for key in data:
                if type(data[key]) != list and type(data[key]) != tuple:
                    x.add_column(key, [data[key]])
                else:
                    x.add_column(key, data[key])
        else:
            x.field_names = ['Parameter ', 'value']
            for i in data:
                x.add_row([i, data[i]])
        x.align = 'l'
        return x

    def get_os(self):
        if platform == "linux" or platform == "linux2":
            return "linux"
        elif platform == "darwin":
            return "darwin"
        elif platform == "win32":
            return "win32"
