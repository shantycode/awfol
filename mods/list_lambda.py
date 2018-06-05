import boto3
from ete3 import Tree

def modexec(tmp_session):
    if tmp_session == None:
        return

    func_node = Tree(name='Lambda Listing')

    client = tmp_session.client('ec2')

    regions = [region['RegionName'] for region in client.describe_regions()['Regions']]

    for region in regions:
        ll = tmp_session.client('lambda', region_name=region)
        result = ll.list_functions()

        for function in result['Functions']:
            func_node.add_child(name=function['FunctionName'])

        
    return func_node