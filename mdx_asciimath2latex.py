import re, markdown

from markdown.util import etree
from asciimath2latex import asciimath2latex

class ASCIIMath2LatexExtension(markdown.Extension):
    def __init__(self, configs):
        pass

    def extendMarkdown(self, md, md_globals):
        self.md = md

        RE = r'\$([^\$]*)\$'

        md.inlinePatterns.add('', ASCIIMath2LatexPattern(RE), '_begin')

    def reset(self):
        pass

class ASCIIMath2LatexPattern(markdown.inlinepatterns.Pattern):

    def handleMatch(self, m):
        el = etree.Element("math")
        el.text = asciimath2latex(m.group(0))
        return el

def makeExtension(configs=None):
    return ASCIIMath2LatexExtension(configs=configs)
