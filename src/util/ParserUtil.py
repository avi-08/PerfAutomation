import argparse
import sys
import os
import re
from prettytable import PrettyTable

from src.env_conf import settings


class Parser:
    def __init__(self, prog=__file__):
        self.prog = prog
        pass

    def parse_cmd_args(self):
        """
        Function to parse command line arguments
        :return: Dictionary containing command line args
        """
        parser = argparse.ArgumentParser(prog=self.prog, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('-s', '--list-settings', action='store', type=str,
                            help='list settings configuration and exit(type "all" to print all settings)',
                            metavar=('SETTING_NAME',))
        parser.add_argument('-v', '--verbose', action='store_true',
                            help='Set verbosity level for console output as DEBUG; default level is INFO')
        parser.add_argument('-e', '--list-env-details', action='store_true', help="List host details and exit")
        parser.add_argument('--list-host-optimizations', action='store_true',
                            help='List current host optimization parameters and exit')
        parser.add_argument('--host-optimization-type', action='store', type=str,
                            help='Specify host configuration type(default=standard), possible values="standard + splittx", "standard + rss", "standard + splittx + rss"',
                            metavar=('CONFIG_TYPE',))
        parser.add_argument('-l', '--list-testcases', action='store_true', help='get a list of testcases')
        parser.add_argument('-g', '--get-testcase', action="store", type=str,
                            help='get details of specified testcase', metavar=('TESTCASE',))
        parser.add_argument('-t', '--testcase', action="store", type=str, metavar=('TESTCASE',),
                            help='Run test for given test case'
                                 '; a comma seperated list for running multiple tests')
        parser.add_argument('--list-operations', action='store_true',
                            help='get a list of all available operations and exit')
        parser.add_argument('-p', '--perform', action='store', type=str,
                            choices=['host_config', 'vm_deploy', 'vm_config', 'traffic_config', 'run_traffic',
                                     'monitoring', 'reporting', 'cleanup'],
                            help='Perform given operation; provide ', metavar=('OPERATION',))
        parser.add_argument('--collect-tech-support', action='store', type=str, nargs='*'
                            , default='', help='Collect tech support dumps. COMMAND(optional): Provide additional commands other than those present in command.json.')
        args = vars(parser.parse_args())
        print(args)
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
            if len(settings.getValue('TESTCASES')) > 0:
                print(settings.getValue('TESTCASES'))
            else:
                print("No defined testcases found")
            sys.exit(0)
        if args['get_testcase']:
            print(args['get_testcase'])
            if settings.getValue('TESTCASES')[0]['NAME'] == [args['get_testcase']]:
                print(settings.getValue('TESTCASES')[args['get_testcase']])
            else:
                print("No defined testcase found by that name.")
            sys.exit(0)

        if args['list_operations']:
            self.get_usecases(os.path.dirname(os.path.dirname(__file__)))
            sys.exit(0)

        if args['list_host_optimizations']:
            print(self.dict_to_table(settings.getValue('ESXI65'), 'HOST optimization settings'))
            sys.exit(0)

    def dict_to_table(self, data, header, row_major=True):
        x = PrettyTable()
        x.title = header
        if row_major:
            for key in data:
                if type(data[key]) != list and type(data[key]) != tuple:
                    x.add_column(key, [data[key]])
                else:
                    x.add_column(key, data[key])
        else:
            x.field_names = ['key', 'value']
            for i in data:
                x.add_row([i, data[i]])

        return x