import ete3
import re

def eval_rule(tree):
    iam_count = 0
    role_count = 0
    
    for node in tree.search_nodes(name='User Listing'):
        for child in node.search_nodes(name="IAM"):
            for iam in child.get_children():
                for policy in iam.get_children():
                    if re.match(r'.*admin.*',policy.name.lower()):
                        iam_count += 1

        for child in node.search_nodes(name="Roles"):
            for role in child.get_children():            
                for policy in role.get_children():
                    if re.match(r'.*admin.*',policy.name.lower()):
                        role_count += 1
    
    ec2 = 0
    for node in tree.search_nodes(name='EC2 Listing'):
        for child in node.get_children():
            ec2 += 1

    print("User  with admin permissions: " + str(iam_count))
    print("Roles with admin permissions: " + str(role_count))
    print("No of EC2 instances in total: " + str(ec2))