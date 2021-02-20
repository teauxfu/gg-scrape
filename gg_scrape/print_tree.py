from anytree import RenderTree

def print_tree(tree: 'tree'):
    for pre, _, node in RenderTree(tree):
        print(f"{pre}{node.name}")