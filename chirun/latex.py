import logging
import os
import re
import shutil
import collections
import pypdf
from subprocess import Popen, PIPE
from pathlib import Path
from chirun import mkdir_p, slugify, copytree

logger = logging.getLogger(__name__)


class LatexSplitter(object):
    toc_match = re.compile(r'\\contentsline\s*\{(\w+)\}\{(\\numberline\s*\{([\w.-]+)\})*([^\}]+)\}\{(\d+)\}\{([\w*]+\.[\w.-]+)\}')  # noqa: E501
    pdfset_dir = None

    class TocEntry:
        title = None
        code = None
        page = 0
        pdf_page = None
        slug = None
        levels = {
            'document': -2,
            'part': -1,
            'chapter': 0,
            'section': 1,
            'subsection': 2,
            'subsubsection': 3,
            'paragraph': 4
        }

        def __init__(self, levelname):
            self.level = self.levels[levelname]

        def __repr__(self):
            rep = "<TocEntry: (code: {}, level: {}".format(self.code, self.level)
            if self.pdf_page:
                rep += ", page: {} [pdf {}]".format(self.page, self.pdf_page + 1)
            else:
                rep += ", page: {}".format(self.page)
            if self.title:
                rep += ", title: {}".format(self.title)
            rep += ")>"
            return rep

    class PDFPageLookup:
        def __init__(self, in_path):
            def all_pages(pages, p=[]):
                if '/Kids' in pages:
                    kids = pages['/Kids'].getObject()
                    for k in kids:
                        all_pages(k.getObject(), p)
                else:
                    p.append(pages)
                return p

            def all_dests(dests, d={}):
                if '/Kids' in dests:
                    kids = dests['/Kids'].getObject()
                    for k in kids:
                        d.update(all_dests(k.getObject(), d))
                if '/Names' in dests:
                    n = dests['/Names'].getObject()
                    for k, v in zip(n[::2], n[1::2]):
                        v = v.getObject()
                        dest = v
                        if '/D' in v:
                            dest = v['/D'].getObject()
                        page_obj = dest[0].getObject()
                        d[k] = self.pages.index(page_obj)
                return d

            pdf = pypdf.PdfReader(str(in_path))
            root = pdf.trailer['/Root'].getObject()
            self.pages = all_pages(root['/Pages'].getObject())
            if '/Names' in root:
                names = root['/Names'].getObject()
                dests_root = names['/Dests'].getObject()
                self.dests = all_dests(dests_root)
            else:
                logger.warning(
                    "Warning: LaTeX PDF cannot be split into sections. "
                    "You might be able to fix this by including the hyperref package."
                )

        def update_toc(self, toc):
            for entry in toc:
                if entry.code:
                    entry.pdf_page = self.dests[entry.code]

    def __init__(self, in_path, aux_filename):
        self.in_path = in_path
        self.aux_filename = aux_filename
        self.toc = []

    def toc_from_aux(self, level):
        if self.toc:
            return self.toc

        doc = self.TocEntry("document")
        doc.pdf_page = 0
        self.toc.append(doc)
        with open(self.aux_filename) as f:
            while True:
                line = f.readline()
                if not line:
                    break
                m = self.toc_match.search(line)
                if m:
                    entry = self.TocEntry(m.group(1))
                    entry.title = m.group(4)
                    entry.page = m.group(5)
                    entry.code = m.group(6)
                    if entry.level <= level:
                        self.toc.append(entry)
        return self.toc

    def split(self, level):
        self.toc_from_aux(level)
        self.PDFPageLookup(self.in_path).update_toc(self.toc)

        # Create a directory for the split pdf set
        if not self.pdfset_dir:
            file_id = 0
            self.pdfset_dir = self.in_path.with_suffix('')
            while self.pdfset_dir.exists():
                new = Path(str(self.in_path.with_suffix('')) + '-' + str(file_id).zfill(4))
                logger.info("PDF set directory path {} exists. Trying {}...".format(self.pdfset_dir, new))
                self.pdfset_dir = new
                file_id = file_id + 1
            logger.debug('Creating directory for split PDF set: {}'.format(self.pdfset_dir))
            mkdir_p(self.pdfset_dir)

        # Split PDF on the toc entries
        try:
            reader = PyPDF2.PdfFileReader(open(str(self.in_path), 'rb'))
            for idx, entry in enumerate(self.toc):
                entry.slug = slugify(entry.title or self.in_path.with_suffix('').name)
                pdfset_file = self.pdfset_dir / Path(entry.slug).with_suffix('.pdf')
                n = 0
                while pdfset_file.exists():
                    entry.slug = slugify(entry.title or self.in_path.with_suffix('').name, n)
                    pdfset_file = self.pdfset_dir / Path(entry.slug).with_suffix('.pdf')
                    n = n + 1
                if idx + 1 == len(self.toc):
                    end_pg = reader.getNumPages() - 1
                else:
                    end_pg = max(entry.pdf_page, self.toc[idx + 1].pdf_page - 1)

                try:
                    pdftk_args = [
                        str(self.in_path),
                        "cat", "{}-{}".format(entry.pdf_page + 1, end_pg + 1),
                        "output",
                        str(pdfset_file)
                    ]
                    PdftkRunner(pdftk_args).exec()
                except FileNotFoundError as e:
                    logger.warning(e)
                    # Try an alternative implementation with PyPDF2
                    # This seems to choke on certain PDFs, so we use it only as a backup
                    logger.warning('Warning: It looks like the pdftk command might be missing... '
                                   'Please install pdftk if possible in your environment.')
                    logger.warning("Trying to continue using PyPDF2 instead...")
                    writer = PyPDF2.PdfFileWriter()
                    for pg in range(entry.pdf_page, end_pg + 1):
                        writer.addPage(reader.getPage(pg))
                    with open(str(pdfset_file), 'wb') as outfile:
                        writer.write(outfile)
        except Exception as e:
            shutil.rmtree(str(self.pdfset_dir))
            raise e


class LatexRunner(object):
    compiler = 'pdflatex'
    args = None
    wd = None
    filename = None

    class RunnerException(Exception):
        pass

    def __init__(self, filename, wd=Path('.')):
        self.wd = wd
        self.filename = filename
        self.args = ['-halt-on-error', '-interaction=nonstopmode', '-recorder', str(filename)]

    def exec(self):
        stdout_tail = collections.deque(maxlen=8)
        cmd = [self.compiler] + self.args
        logger.info('Running {}: {}'.format(self.compiler, self.wd / self.args[-1]))
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, cwd=str(self.wd), universal_newlines=True)
        for stdout_line in iter(proc.stdout.readline, ""):
            if not stdout_line.isspace():
                stdout_tail.append(stdout_line)
            logger.debug(stdout_line[:-1])
        out, err = proc.communicate()
        if proc.returncode != 0:
            logger.error(err)
            raise self.RunnerException("Error: Something went wrong running: {}\n\n{}"
                                       .format(' '.join(cmd), ''.join(stdout_tail)))

    def clean_aux(self):
        logger.debug('Cleaning up pdflatex auxiliary files.')
        extensions = ['.log', '.aux', '.out', '.bbl', '.blg', '.snm', '.nav', '.toc', '.fls']
        for extension in extensions:
            filename = self.wd / self.filename.with_suffix(extension)
            logger.debug('  Deleting: {}'.format(filename))
            try:
                os.remove(filename)
            except OSError:
                pass

    def clean_out(self):
        logger.debug('Cleaning up pdflatex output documents.')
        extensions = ['.pdf', '.dvi']
        for extension in extensions:
            filename = self.wd / self.filename.with_suffix(extension)
            logger.debug('    Deleting: {}'.format(filename))
            try:
                os.remove(filename)
            except OSError:
                pass


class BibtexRunner(LatexRunner):
    compiler = 'bibtex'
    args = None

    def __init__(self, filename, wd=Path('.')):
        self.wd = wd
        self.args = [str(filename.with_suffix(''))]


class PdftkRunner(LatexRunner):
    compiler = 'pdftk'
    args = None

    def __init__(self, args, wd=Path('.')):
        self.wd = wd
        self.args = args


class PDFLatex(object):
    def __init__(self, course, item):
        self.course = course
        self.item = item
        self.in_dir = self.course.get_root_dir() / self.item.source.parent
        self.in_path = self.in_dir / self.item.base_file.with_suffix('.pdf')
        self.out_path = self.course.get_build_dir() / self.item.named_out_file.with_suffix('.pdf')
        self.aux_filename = self.in_dir / self.item.in_file.with_suffix('.aux')

        if self.item.recently_built():
            if self.course.args.cleanup_all:
                LatexRunner(self.item.in_file, self.in_dir).clean_aux()
            return

    def compile(self):
        # First pdflatex run
        LatexRunner(self.item.in_file, self.in_dir).exec()

        # Test for bibtex commands and run where required
        with open(self.aux_filename) as f:
            f_read = f.read()
            if r'\bibstyle' in f_read or r'\bibdata' in f_read:
                BibtexRunner(self.item.in_file, self.in_dir).exec()
                LatexRunner(self.item.in_file, self.in_dir).exec()

        # Final pdflatex run
        LatexRunner(self.item.in_file, self.in_dir).exec()

    def copy_pdf(self):
        logger.debug('Creating directory for pdf output: {outDir}'.format(outDir=self.out_path.parent))
        Path.mkdir(self.out_path.parent, parents=True, exist_ok=True)
        logger.debug('Moving pdf output: {inPath} => {outPath}'.format(inPath=self.in_path, outPath=self.out_path))
        shutil.move(str(self.in_path), str(self.out_path))

    def copy_pdfset(self, pdfset_dir):
        logger.debug('Creating directory for PDF set output: {}'.format(self.out_path.parent))
        pdfset_out_dir = self.out_path.parent / Path('pdf')
        Path.mkdir(pdfset_out_dir, parents=True, exist_ok=True)
        logger.debug('Moving PDF set output: {} => {}'.format(pdfset_dir, pdfset_out_dir))
        copytree(str(pdfset_dir), str(pdfset_out_dir))

    def process_pdf(self):
        if self.item.recently_built():
            if self.course.args.cleanup_all:
                LatexRunner(self.item.in_file, self.in_dir).clean_aux()
            return
        self.compile()
        self.copy_pdf()
        LatexRunner(self.item.in_file, self.in_dir).clean_out()
        if self.course.args.cleanup_all:
            LatexRunner(self.item.in_file, self.in_dir).clean_aux()

    def process_split_pdf(self):
        if self.item.recently_built():
            if self.course.args.cleanup_all:
                LatexRunner(self.item.in_file, self.in_dir).clean_aux()
            return None
        self.compile()
        splitter = LatexSplitter(self.in_path, self.aux_filename)
        splitter.split(self.item.splitlevel)
        self.copy_pdfset(splitter.pdfset_dir)
        logger.debug('Cleanup PDF set output at: {}'.format(splitter.pdfset_dir))
        shutil.rmtree(str(splitter.pdfset_dir))
        LatexRunner(self.item.in_file, self.in_dir).clean_out()
        if self.course.args.cleanup_all:
            LatexRunner(self.item.in_file, self.in_dir).clean_aux()

        return splitter.toc


if __name__ == "__main__":
    pass
