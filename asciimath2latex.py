import re
import sys

def print_node(node, level):
    n = 10
    #tt = [node.text[i:i+n] for i in range(0, len(node.text), n)]
    #print("\t"*level + ("\n"+"\t"*level).join(tt))
    print("\t"*level + "- " + node.text)
    for n in node.children:
        print_node(n, level+1)

def _flatten(node):
    return node.flatten()

class Node(object):
    def __init__(self, parent=None, text="", iAfter=-1):
        self.children = []
        self.parent = None
        self.text = text
        if parent:
            self.parent = parent
            if iAfter == -1:
                parent.children.append(self)
            else:
                parent.children.insert(iAfter+1, self)

    def add_text_after(self, text):
        text = text.strip()
        if text:
            if self.text:
                return Node(self.parent, text, self.index())
            else:
                self.text = text
        return self

    def index(self):
        return self.parent.children.index(self)

    def prev(self):
        return self.parent.children[self.index()-1]

    def next(self):
        return self.parent.children[self.index()+1]

    def reparent(self,newp):
        self.parent.children.remove(self)
        newp.children.append(self)
        self.parent = newp

    def dump(self):
        print_node(self, 0)

    def flatten(self):
        c = "".join(map(_flatten, self.children))
        if self.text == "()":
            return r"\left(" + c + r"\right)"
        elif self.text == "{}":
            return "{" + c + "}"
        elif self.text == "[]":
            return "[" + c + "]"
        else:
            return self.text + c


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
        i+=1
        process_binary_operators(c)
        if c.text == "/":
            continue
        iOp = c.text.find("/")
        if iOp == -1:
            continue
        iStart = c.text.rfind(" ", 0, iOp)
        if iStart == -1:
            iStart = 0
        iEnd = c.text.find(" ", iOp+1)
        if iEnd == -1:
            iEnd = len(c.text)-1
        before = c.text[:iStart]
        a = c.text[iStart:iOp]
        b = c.text[iOp+1:iEnd+1]
        after = c.text[iEnd+1:]
        c.text = before
        op = c.add_text_after(a)
        op = op.add_text_after("/")
        op = op.add_text_after(b)
        op = op.add_text_after(after)
    return tree

def surround_with_braces(node):
    if node.text == "()":
        pass
    elif node.text[0]!="{" or node.text[-1]!="}":
        node.text = '{%s}' % node.text
    return node

def reparent_binary_operators(tree):
    i=0
    while i<len(tree.children):
        c = tree.children[i]
        i+=1
        reparent_binary_operators(c)
        if c.text == "/":
            surround_with_braces(c.prev()).reparent(c)
            surround_with_braces(c.next()).reparent(c)
            i-=1
    return tree

def postprocess(tree):
    i=0
    while i<len(tree.children):
        c = tree.children[i]
        i+=1
        postprocess(c)
        if c.text == "()":
            if c.prev().text[-1] == '_' or c.prev().text[-1] == '^':
                c.text = "{}"
            if c.parent.text == "/":
                c.text = "{}"
    return tree


SYMBOLS=[
    ["sum",r'\sum'],
    ["prod",r'\prod'],
    [r"R", r'\mathbb{R}'],
    [r"Pr", r'\mathbb{P}'],
    [r"P", r'\mathbb{P}'],
    [r"in", r"\in"],
    [r"notin", r"\\notin"],
    [r"subset", r"\subset"],
    [r"supset", r"\supset"],
    [r"forall", r"\\forall"],
    [r"exists", r"\exists"],
    [r"implies", r"\\Rightarrow"],

]

RAW_SYMBOLS = [
    [r'[|]-&gt;', r'\\mapsto'],
    [r'-&gt;', r'\\rightarrow'],
    [r'=&gt;', r'\\Rightarrow'],
    [r'&lt;=&gt;', r'\\Leftrightarrow'],
    [r'&gt;=', r'\\geq'],
    [r'&lt;=', r'\\leq'],
]

S_SYMBOLS = [
    ["\\E", "\mathbb{E}"],
    ["\\P", "\mathbb{P}"],

    ["**X**", "\mathcal{X}"],
    ["**Y**", "\mathcal{Y}"],
    ["**Z**", "\mathcal{Z}"],
    ["**L**", "\mathcal{L}"],
    ["**l**", "\mathcal{l}"],

    ["*X*", "\mathbf{X}"],
    ["*Y*", "\mathbf{Y}"],
    ["*Z*", "\mathbf{Z}"],

    ["*x*", "\mathbf{x}"],
    ["*y*", "\mathbf{y}"],
    ["*z*", "\mathbf{z}"],
]



def substitute_symbols(str, additionnal_symbols):
    str = re.sub(r"/", r"\\frac", str)
    for symb in additionnal_symbols:
        try:
            str = re.sub(r"(^|[^a-zA-Z])("+re.escape(symb[0].replace("(", "\\(").replace(")", "\\)"))+r")($|[^a-zA-Z])", r"\1"+symb[1].replace("\\", "\\\\")+r"\3", str)
        except:
            pass
    for symb in RAW_SYMBOLS:
        str = re.sub(symb[0], symb[1], str)
    for symb in SYMBOLS:
        str = re.sub(r"(^|\W)" + symb[0], r"\1"+symb[1], str)
    for symb in S_SYMBOLS:
        str = str.replace(symb[0], symb[1])
    return str

def asciimath2latex(x, symbols):
    #print(x)
    tree = build_expressions_tree(x)
    #tree.dump()
    #print("\n-----process_binary_operators-------\n")
    tree = process_binary_operators(tree)
    tree = reparent_binary_operators(tree)
    #tree.dump()
    #print("\n-----post_process-------\n")
    tree = postprocess(tree)
    #tree.dump()
    #print("\n-----result-----\n")
    return substitute_symbols(tree.flatten(), symbols)

def main():
    print(asciimath2latex(sys.stdin.read()))


if __name__ == '__main__':
    main()
