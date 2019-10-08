import boto3
import os
import imp
import pathlib
import random
import configparser
import argparse
import threading

from ete3 import Tree
from boto3.dynamodb.conditions import Key, Attr
from helper.exporter import Exporter

'''

awfol - aws full organization lister

'''

class OrgHandler:

    def __init__(self):
        env    = 'MAIN'
        config = configparser.ConfigParser()
        config.read('config.ini')

        self.profile  = config.get(env,'PROFILE')
        self.role     = config.get(env,'ROLE')
        self.sess_id  = config.get(env,'SESS_ID')
        self.master   = config.get(env,'MASTER')
        self.filename = config.get(env,'FILE')
        
        self.root_session = boto3.Session(profile_name=self.profile)

        self.modpath = self.build_path('mods')
        self.rulepath = self.build_path('rules')

    def run_all_mods(self):
        return self.exec_mods(self.get_accounts_id())

    def get_accounts(self):
        client = boto3.client('organizations')
        account_list = []

        response = client.list_accounts()

        while 'NextToken' in response:
            account_list += response['Accounts']
            response = client.list_accounts(NextToken=response['NextToken'])

        account_list += response['Accounts']

        return account_list

    def get_accounts_id(self):
        account_list = self.get_accounts()

        account_list = list(filter(lambda client: client['Id'] != self.master, account_list))
        account_list = list(filter(lambda client: client['Status'] == 'ACTIVE', account_list))

        account_list = [client['Id'] for client in account_list]

        return account_list

    def assume_role(self, arn):
        sts_connection = self.root_session.client('sts')
        try:
            assume_role_object=sts_connection.assume_role(
                RoleArn=arn, 
                RoleSessionName=self.sess_id, 
                DurationSeconds=3600)
        except:
            return None

        tmp_credentials = assume_role_object['Credentials']
        
        tmp_access_key = tmp_credentials['AccessKeyId']
        tmp_secret_key = tmp_credentials['SecretAccessKey']
        security_token = tmp_credentials['SessionToken']

        tmp_session = boto3.Session(aws_access_key_id=tmp_access_key,
                                    aws_secret_access_key=tmp_secret_key,
                                    aws_session_token=security_token,
                                    profile_name=self.profile)
        return tmp_session

    def build_arn(self,account_id):
        return "arn:aws:iam::" + str(account_id) + ":" + self.role

    def exec_mods(self, accounts):
        mod_tree = Tree(name='S2 AWS')

        threads = []
        lock = threading.Lock()

        for account_id in accounts:
            for file in os.listdir(self.modpath):
                if file.endswith(".py"):
                    tmp_session = self.assume_role(self.build_arn(account_id))

                    sts = tmp_session.client(service_name='sts')
                    account = sts.get_caller_identity()["Account"]

                    uri = os.path.normpath(os.path.join(os.path.dirname(__file__), os.path.join(self.modpath, file)))
                    path, fname = os.path.split(uri)
                    mname, ext = os.path.splitext(fname)

                    mod = importlib.machinery.SourceFileLoader(mname, uri).load_module()

                    acc_list = mod_tree.search_nodes(name=account)
                    if len(acc_list) == 0 :
                        acc_node = mod_tree.add_child(name=account)
                    else:
                        acc_node = acc_list[0]

                    thread = threading.Thread(target=self.run_mod, args=[tmp_session, mod, acc_node, lock])
                    threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        return mod_tree
    
    def run_mod(self, tmp_session, mod, acc_node, lock):
        child = mod.modexec(tmp_session)
        if child is not None:
            lock.acquire()
            acc_node.add_child(child)
            lock.release()


    def exec_rules(self,tree):
        for file in os.listdir(self.rulepath):
            if file.endswith(".py"):
                uri = self.canonize_path(self.rulepath, file)
                path, fname = os.path.split(uri)
                mname, ext = os.path.splitext(fname)

                rule = importlib.machinery.SourceFileLoader(mname, uri).load_module()
                rule.eval_rule(tree)

    def save_tree(self, tree):
        tree.write(format=3, outfile=self.filename)

    def read_tree(self):
        return Tree(self.filename, format=3)

    def canonize_path(self, suffix, file):
        return os.path.normpath(os.path.join(os.path.dirname(__file__), os.path.join(suffix, file)))

    def build_path(self, suffix):
        return ''.join([os.path.join(os.path.dirname(os.path.realpath(__file__))), '/', suffix])

if __name__ == "__main__":
    orga = OrgHandler()
    exp = Exporter()

    parser = argparse.ArgumentParser(description='awfol - your AWS organization recon tool')
    parser.add_argument('-e', action='store_true', default=False,dest='eval',help='Evaluates the rules. This reads the stored results.')
    parser.add_argument('-r', action='store_true', default=False,dest='read',help='Reads the stored results and prints the tree.')
    parser.add_argument('-x', action='store_true', default=False,dest='exe', help='Execute live on an AWS organization. This stores the results.')
    parser.add_argument('-t', action='store_true', default=False,dest='test',help='Do a test run.')

    args = parser.parse_args()

    if args.read:
        tree = orga.read_tree()
        exp.print_ascii(tree)

    if args.exe:
        tree = orga.run_all_mods()
        orga.save_tree(tree)

    if args.test:
        tree = orga.run_all_mods()
        exp.print_ascii(tree)

    if args.eval:
        tree = orga.read_tree()
        orga.exec_rules(tree)
