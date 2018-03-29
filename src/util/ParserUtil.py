import argparse
import sys

from src.env_conf import settings


class Parser:
    def __init__(self):
        pass

    def parse_cmd_args(self):
        """
        Function to parse command line arguments
        :return: Dictionary containing command line args
        """
        parser = argparse.ArgumentParser(prog=__file__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('-s', '--list-settings', action='store_true',
                            help='list effective settings configuration and exit')
        parser.add_argument('-v', '--verbose', action='store_true',
                            help='Set verbosity level for console output as DEBUG; default is INFO')
        parser.add_argument('-l', '--list-testcases', action='store_true', help='get a list of testcases' )
        parser.add_argument('-g', '--get-testcase', action="store", type=str,
                            help='get details of specified testcase', metavar=('TESTCASE',))
        parser.add_argument('-t', '--testcase', action="store", type=str, metavar=('TESTCASE',),
                            help='Run test for given test case'
                                 '; a comma seperated list for running multiple tests')
        parser.add_argument('--list-operations', action='store_true', help='get a list of all available operations')
        parser.add_argument('--perform', action='store', type=str, choices=['host_config', 'vm_deploy', 'vm_config', 'traffic_config', 'run_traffic', 'monitoring', 'reporting', 'cleanup'],
                            help='Perform given operation; provide ', metavar=('OPERATION',))
        args = vars(parser.parse_args())

        return args

    def get_usecases(self, dirpath):

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
            self.get_usecases()
            sys.exit(0)