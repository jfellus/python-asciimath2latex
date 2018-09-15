import re
import sys

def print_node(node, level):
    n = 10
    #tt = [node.text[i:i+n] for i in range(0, len(node.text), n)]
    #print("\t"*level + ("\n"+"\t"*level).join(tt))
    print("\t"*level + "- " + node.text)
    for n in node.children:
        print_node(n, level+1)

class Node(object):
    def __init__(self, parent=None):
        self.children = []
        self.parent = None
        self.text = ""
        if parent:
            self.parent = parent
            parent.children.append(self)

    def add_text_after(self, text):
        text = text.strip()
        if text:
            if self.text:
                n = Node(self.parent)
                n.text = text
                return n
            else:
                self.text = text
        return self

    def dump(self):
        print_node(self, 0)

def build_expressions_tree(x):
    root = Node()
    curnode = Node(root)
    while True:
        m = re.search(r'[()]', x)
        if not m:
            curnode.add_text_after(x)
            return root
        delim = m.group()
        i = m.start()
        if delim == '(':
            curnode = curnode.add_text_after(x[:i])
            curnode = curnode.add_text_after('()')
            curnode = Node(curnode)
        else:
            curnode = curnode.add_text_after(x[:i])
            curnode = curnode.parent
        x = x[i+1:]

def asciimath2latex(x):
    print(x)
    tree = build_expressions_tree(x)
    tree.dump()
    return tree

def main():
    print(asciimath2latex(sys.stdin.read()))


if __name__ == '__main__':
    main()
