from anytree import RenderTree, Node


def print_tree(tree: Node):
    for pre, _, node in RenderTree(tree):
        print(f"{pre}{node.name}")
