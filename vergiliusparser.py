# import libraries
import urllib2
import urlparse
import re
import os
import sys
import json
import depgraph
from bs4 import BeautifulSoup


class Struct:
    def __init__(self, text):
        self._text = text.replace("unionvolatile", "volatile union").replace("unnamed-", "unnamed_")
        self._keyword = ""
        self._name = ""
        self._deps = []
        self._forward = []
        self._fill_deps()

    def _fill_deps(self):
        lines = self._text.splitlines()
        x = re.compile(r"^\s*(struct|enum|union)\s+([A-Za-z0-9_]+)(\**)")
        match = x.match(lines[1])
        self._keyword = match.group(1)
        self._name = match.group(2)
        for line in lines[2:]:
            line = line.replace("volatile ", "")
            match = x.match(line)
            if match:
                name = match.group(2)
                if match.group(3):
                    self._forward.append(name)
                else:
                    self._deps.append(name)
        self._deps = list(set(self._deps))
        self._forward = list(set(self._forward))

    @property
    def text(self):
        return self._text

    @property
    def keyword(self):
        return self._keyword

    @property
    def name(self):
        return self._name

    @property
    def deps(self):
        return self._deps

    @property
    def forward(self):
        return self._forward


def scrape_contents(url):
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page, "html.parser")
    copyblock = soup.find("div", attrs={"id": "copyblock"})
    text = copyblock.text
    page.close()
    return text


def scrape_kernel(url, outfile):
    if not os.path.exists(outfile + ".json"):
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page, "html.parser")
        mydiv = soup.find("div", attrs={"id": "myDiv"})
        links = [urlparse.urljoin(url, a.get('href')) for a in mydiv.find_all('a', href=True)]
        page.close()
        types = []
        for i in range(0, len(links)):
            link = links[i]
            if i % 100 == 0:
                print "%d/%d" % (i, len(links))
            types.append(scrape_contents(link))
        f = open(outfile + ".json", "w")
        f.write(json.dumps(types))
        f.close()
    else:
        f = open(outfile + ".json", "r")
        types = json.load(f)
        f.close()

    file = open(outfile, "w")
    file.write("#include \"basetypes.h\"\n\n")

    structs = [Struct(t) for t in types]

    byname = {}
    for s in structs:
        byname[s.name] = depgraph.Dataset(s.name, tool=s)

    forward = set()
    for s in structs:
        for f in s.forward:
            forward.add(f)
    forward = sorted(list(forward))

    file.write("// Forward declarations\n")
    for f in forward:
        s = byname[f].tool
        file.write("%s %s;\n" % (s.keyword, s.name))
    file.write("\n")

    for s in structs:
        for dep in s.deps:
            byname[s.name].dependson(byname[dep])
    kernel = depgraph.Dataset("VERGILIUS")
    for s in structs:
       kernel.dependson(byname[s.name])

    def print_struct(name):
        if name != kernel.name:
            file.write(byname[name].tool.text)
            file.write("\n\n")

    @depgraph.buildmanager
    def build(dep, reason):
        print_struct(dep.name)

    file.write("// Types\n")
    for root in kernel.roots():
        print_struct(root.name)
    build(kernel)

    file.close()


def main():
    if len(sys.argv) < 3:
        print "usage: vergiliusparser url outfile"
        sys.exit(1)
    url = sys.argv[1] # "http://localhost:2015/www.vergiliusproject.com/kernels/x64/Windows%208.1%20_%202012R2/Update%201.html"
    outfile = sys.argv[2] # x64_windows81_update1.h
    scrape_kernel(url, outfile)


if __name__ == "__main__":
    main()
