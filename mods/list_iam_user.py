import boto3
from ete3 import Tree

def modexec(tmp_session):
    if tmp_session == None:
        return

    func_node = Tree(name='User Listing')

    iam_node = func_node.add_child(name='IAM')
    role_node = func_node.add_child(name='Roles')
    
    iam = tmp_session.client(service_name='iam')
    
    for userlist in iam.list_users()['Users']:
        name = userlist['UserName']
        iam_child = iam_node.add_child(name=name)
        list = iam.list_attached_user_policies(UserName=name)['AttachedPolicies']
        for pol in list:
            polname = pol['PolicyName']
            iam_child.add_child(name=polname)

 
    for role in iam.list_roles()['Roles']:
        name = role['RoleName']
        role_child = role_node.add_child(name=name)
        list = iam.list_attached_role_policies(RoleName=name)['AttachedPolicies']
        for pol in list:
            polname = pol['PolicyName']
            role_child.add_child(name=polname)

    return func_node