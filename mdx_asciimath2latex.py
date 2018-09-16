import re, markdown

from markdown.util import etree
from asciimath2latex import asciimath2latex

class ASCIIMath2LatexExtension(markdown.Extension):
    def __init__(self, configs):
        pass

    def extendMarkdown(self, md, md_globals):
        self.md = md
        md.postprocessors.add('asciimath-eq', ASCIIMath2LatexEquationPostProcessor(), "_begin")
        md.postprocessors.add('asciimath', ASCIIMath2LatexPostProcessor(), "_begin")

    def reset(self):
        pass

class ASCIIMath2LatexPostProcessor(markdown.postprocessors.Postprocessor):
    def run(self, x):
        RE = r'\$([^\$]*)\$'
        x = re.sub(RE, lambda y: "$"+asciimath2latex(y.group(1))+"$", x, flags=re.M)
        return x

class ASCIIMath2LatexEquationPostProcessor(markdown.postprocessors.Postprocessor):
    def run(self, x):
        RE = r'^\s*\$([^\$]*)\$'
        x = re.sub(RE, r"\\begin{equation}\n \1 \n \\end{equation}\n", x, flags=re.M)
        return x

def makeExtension(configs=None):
    return ASCIIMath2LatexExtension(configs=configs)
