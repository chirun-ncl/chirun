import markdown
from markdown.treeprocessors import Treeprocessor
from markdown import Extension
from markdown.util import etree
import logging
import shlex
import re
from copy import copy
from shutil import copyfile
from pathlib import Path, PurePath
from makeCourse import mkdir_p

logger = logging.getLogger(__name__)

def find_item(structure, srcFiles):
    for item in structure:
        if item.source.resolve() in srcFiles:
            return item
        if item.content:
            sitem = find_item(item.content, srcFiles)
            if sitem:
                return sitem
    return None

class LinkTreeprocessor(Treeprocessor):
    def __init__(self, md, item_sourcedir, item_outdir, course_structure):
        Treeprocessor.__init__(self, md)
        self._item_sourcedir = Path(item_sourcedir)
        self._item_outdir = Path(item_outdir)
        self._structure = course_structure
        self.fileID = 0

    def run(self, root):
        moved_links = set()
        links = root.iter("a")
        for count, link in enumerate(links):
            if link in moved_links:
                continue
            src = link.attrib["href"]
            srcmatch = re.match(r"""([^?#]+)([?#].+)*""", src)
            if src[0] != '/' and not src.startswith(('http://','https://','ftp://')) and srcmatch:
                srcFile = self._item_sourcedir / srcmatch.group(1)
                # Check for content that will be built by makecourse
                if srcFile.suffix in ('.html', '.htm', '.md'):
                    item = find_item(self._structure, (
                        srcFile.with_suffix('.md').resolve(),
                        srcFile.with_suffix('.tex').resolve()
                        ))
                    if item:
                        logger.debug('Found a crossref to coursebuilder item: {}'.format(item))
                        link.attrib["href"] = '/'+item.url+(srcmatch.group(2) or '')
                        continue
                # otherwise, copy the content to build directory and link
                if srcFile.exists():
                    outSrc = Path('files') / (str(self.fileID).zfill(4) + '-' + Path(src).name)
                    outFile = self._item_outdir / outSrc
                    mkdir_p(outFile.parent)
                    copyfile(str(srcFile),str(outFile))
                    link.attrib["href"] = str(outSrc)
                    self.fileID = self.fileID + 1
            moved_links.add(link)

class LinkProcessorExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {
            'item_sourcedir': ['.', "Source directory of the coursebuilder content item"],
            'item_outdir': ['.', "Output build location for the coursebuilder content item"],
            'course_structure': [[], "The coursebuilder course structure"],
        }
        super(LinkProcessorExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        links = LinkTreeprocessor(md, self.getConfig('item_sourcedir'), self.getConfig('item_outdir'), self.getConfig('course_structure'))
        md.treeprocessors.add("linkprocessor", links, "_end")
        md.registerExtension(self)
