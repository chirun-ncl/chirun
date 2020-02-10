import logging
import os
import shutil
from subprocess import Popen, PIPE
from pathlib import Path

logger = logging.getLogger(__name__)


def runPdflatex(course, item):
    inDir = course.get_root_dir() / item.source.parent

    cmd = ['pdflatex', '-halt-on-error', str(item.in_file)]
    logger.info('Running pdflatex: {}'.format(inDir / item.in_file))

    # latex often requires 2 runs to resolve labels
    # TODO: make number of runs a parameter
    for _ in range(2):
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, cwd=str(inDir), universal_newlines=True)
        for stdout_line in iter(proc.stdout.readline, ""):
            logger.debug(stdout_line)

        out, err = proc.communicate()

        if proc.returncode != 0:
            logger.error(err)
            raise Exception("Error: Something went wrong running pdflatex!")

    inPath = inDir / item.base_file.with_suffix('.pdf')
    outPath = course.get_build_dir() / item.named_out_file.with_suffix('.pdf')
    logger.debug('    Creating directory for pdf output: {outDir}'.format(outDir=outPath.parent))
    Path.mkdir(outPath.parent, parents=True, exist_ok=True)
    logger.debug('    Moving pdf output: {inPath} => {outPath}'.format(inPath=inPath, outPath=outPath))
    shutil.move(str(inPath), str(outPath))

    if not course.args.lazy:
        logger.info('    Cleaning up after pdflatex...')
        extensions = ['.log', '.aux', '.out', '.pdf', '.snm', '.nav', '.toc']
        for extension in extensions:
            filename = '{base}{extension}'.format(base=inDir / item.base_file, extension=extension)
            logger.debug('        Deleting: {}'.format(filename))
            try:
                os.remove(filename)
            except OSError:
                pass


if __name__ == "__main__":
    pass
