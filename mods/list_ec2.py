import boto3
from ete3 import Tree

def modexec(tmp_session):
    if tmp_session == None:
        return

    func_node = Tree(name='EC2 Listing')

    client = tmp_session.client('ec2')

    ec2_regions = [region['RegionName'] for region in client.describe_regions()['Regions']]

    this_name = ""
    ami_name = ""
    for region in ec2_regions:

        ec2 = tmp_session.resource(service_name='ec2', region_name=region)
        instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        
        for instance in instances:
            this_name = ""
            ami_name = ""

            inst_handler = ec2.Instance(instance.id)
            tags = inst_handler.tags or []
            names = [tag.get('Value') for tag in tags if tag.get('Key') == 'Name']
            if names:
                ami_name = names[0]
            else:
                ami_name = '---'

            this_name = instance.id + '(' + ami_name + ')' 
            func_node.add_child(name=this_name)
        
    return func_node