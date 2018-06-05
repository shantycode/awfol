import boto3
from ete3 import Tree

'''
Does not do much at the moment - Account with active tasks for a check back needed
'''

def modexec(tmp_session):
    return None
    
    if tmp_session == None:
        return

    func_node = Tree(name='ECS Listing')

    cclient = tmp_session.client(service_name='emr')
    clist = cclient.list_clusters(ClusterStates=['RUNNING'])['Clusters']

    for cluster in clist:
        cluster = func_node.add_child(name=cluster['Name'] + '(Cluster)')
        ecs = tmp_session.client(service_name='ecs')
        
        # TODO check for next token
        for task in ecs.list_tasks(cluster=cluster['Name'], desiredStatus='RUNNING'):
            cluster.add_child(name=task['Name']) 

    return func_node
