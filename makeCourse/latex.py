import logging
import os
import shutil
import collections
from subprocess import Popen, PIPE
from pathlib import Path

logger = logging.getLogger(__name__)

class LatexRunner(object):
    compiler = 'pdflatex'
    args = None
    wd = None
    filename = None

    def __init__(self,filename, wd='.'):
        self.wd = wd
        self.filename = filename
        self.args = ['-halt-on-error', '-recorder', str(filename)]

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
            raise Exception("Error: Something went wrong running: {}\n\n{}".format(' '.join(cmd), ''.join(stdout_tail)))

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
            logger.debug('  Deleting: {}'.format(filename))
            try:
                os.remove(filename)
            except OSError:
                pass

class BibtexRunner(LatexRunner):
    compiler = 'bibtex'
    args = None

    def __init__(self,aux_filename, wd='.'):
        self.wd = wd
        self.args = [str(aux_filename.with_suffix(''))]

def runPdflatex(course, item):
    in_dir = course.get_root_dir() / item.source.parent
    aux_filename = in_dir / item.in_file.with_suffix('.aux')

    if item.recently_built():
        if course.args.cleanup_all:
            LatexRunner(item.in_file, in_dir).clean_aux()
        return

    LatexRunner(item.in_file, in_dir).exec()

    # Test for bibtex commands
    with open(aux_filename) as f:
        f_read = f.read()
        if r'\bibstyle' in f_read or r'\bibdata' in f_read:
            BibtexRunner(item.in_file, in_dir).exec()
            LatexRunner(item.in_file, in_dir).exec()

    LatexRunner(item.in_file, in_dir).exec()

    inPath = in_dir / item.base_file.with_suffix('.pdf')
    outPath = course.get_build_dir() / item.named_out_file.with_suffix('.pdf')
    logger.debug('    Creating directory for pdf output: {outDir}'.format(outDir=outPath.parent))
    Path.mkdir(outPath.parent, parents=True, exist_ok=True)
    logger.debug('    Moving pdf output: {inPath} => {outPath}'.format(inPath=inPath, outPath=outPath))
    shutil.move(str(inPath), str(outPath))

    LatexRunner(item.in_file, in_dir).clean_out()
    if course.args.cleanup_all:
        LatexRunner(item.in_file, in_dir).clean_aux()

if __name__ == "__main__":
    pass
