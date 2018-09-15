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
    def __init__(self, parent=None, text=""):
        self.children = []
        self.parent = None
        self.text = text
        if parent:
            self.parent = parent
            parent.children.append(self)

    def add_text_after(self, text):
        text = text.strip()
        if text:
            if self.text:
                return Node(self.parent, text)
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

def process_binary_operators(tree):
    i=0
    while i<len(tree.children):
        c = tree.children[i]
        process_binary_operators(c)
        if c.text != "/":
            continue
        iOp = c.text.find("/")
        if iOp == -1:
            continue
        iStart = c.text.rfind(" ", 0, iOp)
        if iStart == -1:
            iStart = 0
        iEnd = c.text.find(" ", iOp+1)
        before = c.text[:iStart]
        a = c.text[iStart+1:iOp]
        b = c.text[iOp+1:iEnd]
        after = c.text[iEnd+1:]
        c.text = before
        op = c.add_text_after("/")
        L = Node(op, a)
        R = Node(op, b)
        op = op.add_text_after(after)



def asciimath2latex(x):
    print(x)
    tree = build_expressions_tree(x)
    tree = process_binary_operators(tree)
    tree.dump()
    return tree

def main():
    print(asciimath2latex(sys.stdin.read()))


if __name__ == '__main__':
    main()
