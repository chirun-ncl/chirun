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

    def __init__(self,filename, wd='.'):
        self.wd = wd
        self.args = [str(filename), '-halt-on-error']

    def exec(self):
        stdout_tail = collections.deque(maxlen=8)
        cmd = [self.compiler] + self.args
        logger.info('Running {}: {}'.format(self.compiler, self.wd / self.args[0]))
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, cwd=str(self.wd), universal_newlines=True)
        for stdout_line in iter(proc.stdout.readline, ""):
            if not stdout_line.isspace():
                stdout_tail.append(stdout_line)
            logger.debug(stdout_line)
        out, err = proc.communicate()
        if proc.returncode != 0:
            logger.error(err)
            raise Exception("Error: Something went wrong running: {}\n\n{}".format(' '.join(cmd), ''.join(stdout_tail)))

class BibtexRunner(LatexRunner):
    compiler = 'bibtex'
    args = None

    def __init__(self,aux_filename, wd='.'):
        self.wd = wd
        self.args = [str(aux_filename.with_suffix(''))]

def runPdflatex(course, item):
    in_dir = course.get_root_dir() / item.source.parent
    tex_filename = in_dir / item.in_file
    aux_filename = in_dir / item.in_file.with_suffix('.aux')

    LatexRunner(tex_filename, in_dir).exec()

    # Test for bibtex commands
    with open(aux_filename) as f:
        f_read = f.read()
        if r'\bibstyle' in f_read or r'\bibdata' in f_read:
            BibtexRunner(aux_filename, in_dir).exec()
            LatexRunner(tex_filename, in_dir).exec()

    LatexRunner(tex_filename, in_dir).exec()

    inPath = in_dir / item.base_file.with_suffix('.pdf')
    outPath = course.get_build_dir() / item.named_out_file.with_suffix('.pdf')
    logger.debug('    Creating directory for pdf output: {outDir}'.format(outDir=outPath.parent))
    Path.mkdir(outPath.parent, parents=True, exist_ok=True)
    logger.debug('    Moving pdf output: {inPath} => {outPath}'.format(inPath=inPath, outPath=outPath))
    shutil.move(str(inPath), str(outPath))

    if not course.args.lazy:
        logger.info('    Cleaning up after pdflatex...')
        extensions = ['.log', '.aux', '.out', '.pdf', '.snm', '.nav', '.toc']
        for extension in extensions:
            filename = '{base}{extension}'.format(base=in_dir / item.base_file, extension=extension)
            logger.debug('        Deleting: {}'.format(filename))
            try:
                os.remove(filename)
            except OSError:
                pass


if __name__ == "__main__":
    pass
