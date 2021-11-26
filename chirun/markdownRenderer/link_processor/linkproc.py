from markdown.treeprocessors import Treeprocessor
from markdown import Extension
import filecmp
import logging
import re
from shutil import copyfile
from pathlib import Path
from chirun import mkdir_p

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
        self.file_id = 0

    def run(self, root):
        moved_links = set()
        links = root.iter("a")
        for count, link in enumerate(links):
            if link in moved_links:
                continue
            src = link.attrib["href"]
            srcmatch = re.match(r"""([^?#]+)([?#].+)*""", src)
            if src[0] != '/' and not src.startswith(('http://', 'https://', 'ftp://')) and srcmatch:
                srcFile = self._item_sourcedir / srcmatch.group(1)
                # Check for content that will be built by chirun
                if srcFile.suffix in ('.html', '.htm', '.md'):
                    item = find_item(self._structure, (srcFile.with_suffix('.md').resolve(),
                                                       srcFile.with_suffix('.tex').resolve()))
                    if item:
                        logger.debug('Found a crossref to chirun item: {}'.format(item))
                        link.attrib["href"] = '/' + item.url + (srcmatch.group(2) or '')
                        continue
                # otherwise, copy the content to build directory and link
                if srcFile.exists():
                    out_href = Path('files') / Path(src).name
                    out_file = self._item_outdir / out_href
                    while out_file.exists() and not filecmp.cmp(out_file, srcFile):
                        new = Path('files') / (str(self.file_id).zfill(4) + '-' + Path(src).name)
                        logger.debug("Output filename {} already used and the file is different. Trying {}..."
                                     .format(out_href, new))
                        out_href = new
                        out_file = self._item_outdir / out_href
                        self.file_id = self.file_id + 1
                    mkdir_p(out_file.parent)
                    copyfile(str(srcFile), str(out_file))
                    link.attrib["href"] = str(out_href)
            moved_links.add(link)


class LinkProcessorExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {
            'item_sourcedir': ['.', "Source directory of the chirun content item"],
            'item_outdir': ['.', "Output build location for the chirun content item"],
            'course_structure': [[], "The chirun course structure"],
        }
        super(LinkProcessorExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        links = LinkTreeprocessor(md, self.getConfig('item_sourcedir'),
                                  self.getConfig('item_outdir'), self.getConfig('course_structure'))
        md.treeprocessors.add("linkprocessor", links, "_end")
        md.registerExtension(self)
