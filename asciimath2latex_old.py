import sys
import os.path
from io import BytesIO
from tempfile import TemporaryFile
import lxml.etree as ET
import asciimathml
from xml.etree.ElementTree import Element, tostring


XSL_FILENAME=os.path.dirname(os.path.abspath(__file__)) + "/yarosh/mmltex.xsl"

def asciimath2latex(input):
    with TemporaryFile() as fMathml:
        mathml = asciimathml.parse(input)
        print(tostring(mathml))
        fMathml.write(tostring(mathml))
        fMathml.seek(0)
        dom = ET.parse(fMathml)
        xslt = ET.parse(XSL_FILENAME)
        transform = ET.XSLT(xslt)
        return transform(dom)
    return ""


def main(args=None):
    print(asciimath2latex(sys.stdin.read()))

if __name__ == "__main__":
    main()
