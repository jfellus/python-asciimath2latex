import re, markdown

from markdown.util import etree
from asciimath2latex import asciimath2latex

class ASCIIMath2LatexExtension(markdown.Extension):
    def __init__(self, configs):
        pass

    def extendMarkdown(self, md, md_globals):
        self.md = md
        md.preprocessors.add('comments', CommentsPreProcessor(), "_begin")
        md.treeprocessors.add('asciimath-symbols', ASCIIMath2LatexSymbolsTreeProcessor(self), "_begin")
        md.treeprocessors.add('asciimath-eq-mathjax', ASCIIMath2LatexEquationTreeProcessor(self), "_end")
        md.postprocessors.add('asciimath-eq', ASCIIMath2LatexEquationPostProcessor(), "_begin")
        md.postprocessors.add('asciimath', ASCIIMath2LatexPostProcessor(self), "_begin")

    def reset(self):
        pass


class CommentsPreProcessor(markdown.preprocessors.Preprocessor):
    def run(self, lines):
        return [re.sub("//.*", "", x) for x in lines]

class ASCIIMath2LatexSymbolsTreeProcessor(markdown.treeprocessors.Treeprocessor):
    def __init__(self, extension):
        self.extension = extension
        self.extension.symbols = []

    def add_symbol(self, s):
        s = s.split(" ")
        self.extension.symbols.append(s)

    def process(self, node):
        if node.getchildren():
            for child in node.getchildren():
                self.process(child)
        if node.tag != "p":
             return node
        try:
            if node.text.startswith("SYMBOLS\n"):
                for s in node.text.split("\n")[1:]:
                    self.add_symbol(s)
                node.text = ""
        except Exception as e:
            raise e
        return node

    def run(self, node):
        return self.process(node)

class ASCIIMath2LatexPostProcessor(markdown.postprocessors.Postprocessor):
    def __init__(self, extension):
        self.extension = extension

    def run(self, x):
        RE = r'\$([^\$]*)\$'
        x = re.sub(RE, lambda y: "$"+asciimath2latex(y.group(1), self.extension.symbols)+"$", x, flags=re.M)
        return x

class ASCIIMath2LatexEquationTreeProcessor(markdown.treeprocessors.Treeprocessor):
    def process(self, node):
        if node.getchildren():
            for child in node.getchildren():
                self.process(child)
        if node.tag != "mathjax":
             return node
        if node.text.startswith("$\n") and node.text.endswith("\n$"):
            node.text = "$\\begin{align}\n" + node.text[2:-2] + "\\end{align}$"
            c = etree.Element("mathjax")
            c.text = node.text
            node.tag = "center"
            node.text = ""
            node.append(c)
            return node
        return node

    def run(self, node):
        return self.process(node)

class ASCIIMath2LatexEquationPostProcessor(markdown.postprocessors.Postprocessor):
    def run(self, x):
        return x.replace("$\\begin{align}", "\\begin{align}").replace("\\end{align}$", "\\end{align}")

def makeExtension(configs=None):
    return ASCIIMath2LatexExtension(configs=configs)
