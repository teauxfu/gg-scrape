"""Prints a tree."""

from anytree import RenderTree, Node


def print_tree(tree: Node):
    """Prints a tree."""
    for pre, _, node in RenderTree(tree):
        print(f"{pre}{node.name}")
