import logging
import os
import re
import shutil
import collections
import pypdf
from subprocess import Popen, PIPE
from pathlib import Path
from plasTeX.TeX import TeX
from chirun import mkdir_p, slugify, copytree

logger = logging.getLogger(__name__)


class LatexSplitter(object):
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
            'paragraph': 4,
            'subparagraph': 5,
            'subsubparagraph': 6,
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
                    kids = pages['/Kids'].get_object()
                    for k in kids:
                        all_pages(k.get_object(), p)
                else:
                    p.append(pages)
                return p

            def all_dests(dests, d={}):
                if '/Kids' in dests:
                    kids = dests['/Kids'].get_object()
                    for k in kids:
                        d.update(all_dests(k.get_object(), d))
                if '/Names' in dests:
                    n = dests['/Names'].get_object()
                    for k, v in zip(n[::2], n[1::2]):
                        v = v.get_object()
                        dest = v
                        if '/D' in v:
                            dest = v['/D'].get_object()
                        page_obj = dest[0].get_object()
                        d[k] = self.pages.index(page_obj)
                return d

            pdf = pypdf.PdfReader(str(in_path))
            root = pdf.trailer['/Root'].get_object()
            self.pages = all_pages(root['/Pages'].get_object())
            if '/Names' in root:
                names = root['/Names'].get_object()
                dests_root = names['/Dests'].get_object()
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

    def toc_from_aux(self, splitlevel):
        """
            Get the table of contents from the .aux files produced by pdflatex.
        """

        if not self.toc:
            self.read_aux_file(self.aux_filename, splitlevel)

        return self.toc

    def read_aux_file(self, filename, splitlevel):
        r"""
            Read a .aux file and save any table of contents entries found in it.

            A TOC entry looks like::

                \@writefile{toc}{\contentsline {chapter}{\numberline {2}Curves and tangents}{12}{chapter.2}\protected@file@percent }

            ``\@input`` commands will cause another .aux file to be read.
        """

        def read_characters(doc, start, length):
            els = doc[start:start+length]
            if not all(isinstance(x,str) for x in els):
                return ''
            return ''.join(els)

        logger.info(f"Loading table of contents from {filename}.")
        with open(filename) as f:
            tex = TeX()
            tex.input(f.read())
            tex.ownerDocument.context.warnOnUnrecognized = False
            doc = tex.parse()
            for i, el in enumerate(doc):
                if el.nodeName != '@':
                    continue

                if read_characters(doc, i+1, 5) == 'input':
                    self.read_aux_file(doc[i+6][0], splitlevel)

                if not (read_characters(doc, i+1, 9) == 'writefile' and doc[i+10][0] == 'toc'):
                    continue

                try:
                    tocline = doc[i+11]

                    if tocline[0].nodeName != 'contentsline':
                        continue

                    level = tocline[1][0]

                    entry = self.TocEntry(level)

                    if entry.level > splitlevel:
                        continue

                    entry.title = tocline[2][-1].textContent
                    entry.page = tocline[3][0].textContent
                    entry.code = tocline[4][0].textContent
                except IndexError as e:
                    continue

                self.toc.append(entry)

        if len(self.toc) == 0:
            doc = self.TocEntry("document")
            doc.pdf_page = 0
            self.toc.append(doc)

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
            reader = pypdf.PdfReader(open(str(self.in_path), 'rb'))

            num_pages = reader.get_num_pages()

            for idx, entry in enumerate(self.toc):
                entry.slug = slugify(entry.title or self.in_path.with_suffix('').name)

                # Find a filename for this section of the PDF
                pdfset_file = self.pdfset_dir / Path(entry.slug).with_suffix('.pdf')
                n = 0
                while pdfset_file.exists():
                    entry.slug = slugify(entry.title or self.in_path.with_suffix('').name, n)
                    pdfset_file = self.pdfset_dir / Path(entry.slug).with_suffix('.pdf')
                    n = n + 1

                start_page = entry.pdf_page

                # Identify the end page
                end_page = num_pages - 1

                for e2 in self.toc[idx+1:]:
                    if e2.level <= entry.level:
                        end_page = e2.pdf_page - 1
                        break

                try:
                    pdftk_args = [
                        str(self.in_path),
                        "cat", "{}-{}".format(start_page + 1, end_page + 1),
                        "output",
                        str(pdfset_file)
                    ]
                    PdftkRunner(pdftk_args).exec()
                except FileNotFoundError as e:
                    logger.warning(e)
                    # Try an alternative implementation with pypdf
                    # This seems to choke on certain PDFs, so we use it only as a backup
                    logger.warning('Warning: It looks like the pdftk command might be missing... '
                                   'Please install pdftk if possible in your environment.')
                    logger.warning("Trying to continue using pypdf instead...")
                    writer = pypdf.PdfWriter()
                    for pg in range(start_page, end_page + 1):
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
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, cwd=str(self.wd), universal_newlines=True,errors="backslashreplace")
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
