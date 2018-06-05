import os
import imp
import pathlib
import random
import configparser

from ete3 import Tree

class Exporter:
    # borrowed from https://gist.github.com/jhcepas/9205262 :-)
    def to_json(self, node):
        # Read ETE tag for duplication or speciation events
        if not hasattr(node, 'evoltype'):
            dup = random.sample(['N','Y'], 1)[0]
        elif node.evoltype == "S":
            dup = "N"
        elif node.evoltype == "D":
            dup = "Y"

        node.name = node.name.replace("'", '')
            
        json = { "name": node.name, 
                "display_label": node.name,
                "duplication": dup,
                "branch_length": str(node.dist),
                "common_name": node.name,
                "seq_length": 0,
                "type": "node" if node.children else "leaf",
                "uniprot_name": "Unknown",
                }
        if node.children:
            json["children"] = []
            for ch in node.children:
                json["children"].append(self.to_json(ch))
                
        return json

    def print_json(self, node):
        print('var treeData = [' + str(self.to_json(node)) + ']')

    def print_ascii(self, node):
        print(node.get_ascii(show_internal=True))