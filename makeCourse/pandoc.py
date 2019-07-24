import logging
import sys
import datetime
from makeCourse import mkdir_p
from subprocess import Popen, PIPE

logger = logging.getLogger(__name__)


class PandocRunner:
    def run_pandoc(self, item, template_file=None, out_format='html', force_local=False):
        root = self.get_web_root(force_local=force_local)
        outPath = self.get_build_dir() / (item.out_file.with_suffix('.' + out_format))
        outDir = outPath.parent
        mkdir_p(outDir)
        if template_file is None:
            template_file = item.template_file
        template_path = self.theme.source_path / template_file
        date = datetime.date.today()

        logger.debug('    {src} => {dest}'.format(src=item.title, dest=outPath))

        if template_file == 'slides.revealjs':
            cmd = [
                'pandoc', '--mathjax={}'.format(self.mathjax_url),
                '-i', '-t', 'revealjs', '-s',
                '-V', 'revealjs-url={}/static/reveal.js'.format(root + self.theme.path),
                '-V', 'web_root={}'.format(root),
                '--template', str(template_path),
                '-o', str(outPath),
            ]
        else:
            cmd = [
                'pandoc', '-s', '--toc', '--toc-depth=2', '--section-divs', '--listings',
                '--title-prefix={}'.format(self.config['title'].replace(' ','-')), '--mathjax={}'.format(self.mathjax_url),
                '--metadata=date:{}'.format(date),
                '-V', 'web_root={}'.format(root),
                '--template', str(template_path),
                '-o', str(outPath),
            ]

        content = item.markdown(force_local=force_local, out_format=out_format).encode('utf-8')
        logger.info('Running pandoc on {}'.format(item))
        logger.debug(' '.join(cmd))
        proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)

        try:
            outs, errs = proc.communicate(content)
        except Exception:
            proc.kill()
            outs, errs = proc.communicate()

        if outs:
            logger.debug(outs.decode('utf-8'))
        if errs:
            logger.error(errs.decode('utf-8'))
            logger.error("Something went wrong running pandoc! Quitting...")
            logger.error("(Use -vv for more information)")
            sys.exit(2)


if __name__ == "__main__":
    pass
