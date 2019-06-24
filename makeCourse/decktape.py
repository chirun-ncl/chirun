import logging
import sys
from subprocess import Popen, PIPE

logger = logging.getLogger(__name__)


class DecktapeRunner:
    def run_decktape(self, item):
        htmlPath = self.get_build_dir() / (item.out_file + '.slides.html')
        outPath = self.get_build_dir() / (item.out_file + '.pdf')
        logger.info('    {src} => {dest}'.format(src=item.title, dest=outPath))

        cmd = [
            'decktape', '-s', '1366x768',
            '-p', '10',
            htmlPath,
            outPath,
            '--chrome-arg=--no-sandbox',
        ]

        proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        for stdout_line in iter(proc.stdout.readline, ""):
            logger.debug(stdout_line)

        try:
            outs, errs = proc.communicate()
        except Exception:
            proc.kill()
            outs, errs = proc.communicate()

        if errs:
            logger.error(errs)
            logger.error("Something went wrong running decktape! Quitting...")
            logger.error("(Use -vv for more information)")
            sys.exit(2)


if __name__ == "__main__":
    pass
