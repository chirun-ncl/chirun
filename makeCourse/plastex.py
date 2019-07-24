import logging
import re
import shutil
import sys
from makeCourse import mkdir_p
from pathlib import Path
from subprocess import Popen, PIPE

logger = logging.getLogger(__name__)


class PlastexRunner:

    tmpDir = ''

    def load_latex_content(self, sourceItem):
        self.tmpDir = self.temp_path(sourceItem)
        self.runPlastex(sourceItem)

        base_file = sourceItem.base_file.with_suffix('.paux')
        out_path = self.temp_path() / (sourceItem.url_clean + '.paux')
        logger.debug('    Moving paux output: {base_file} => {out_path}'.format(
            base_file=base_file,
            out_path=out_path
        ))
        shutil.move(str(base_file), str(out_path))

        root_dir = self.get_root_dir()

        source_file = root_dir / self.tmpDir / (sourceItem.url + '.html')
        with open(str(source_file), encoding='utf-8') as f:
            texContents = f.read()
        # TODO: an abstraction for applying the following as a series of filters
        texContents = self.fixPlastexQuirks(texContents)
        texContents = self.getEmbeddedImages(texContents, sourceItem.title)
        texContents = self.burnInExtras(texContents, False, 'html')
        return texContents

    def fixPlastexQuirks(self, text):
        # Stop markdown from listifying things.
        reItemList = re.compile(r'<p>\s*([\(\[]*)([A-z0-9]{1,3})([\)\]\.\:])')
        text = reItemList.sub(lambda m: '<p>' + m.group(1) + m.group(2) + "\\" + m.group(3), text)

        # Stop pandoc from interpreting plastex output as code
        reStartSpaces = re.compile(r'^ +', re.M)
        text = reStartSpaces.sub('', text)
        reSmartQuotes = re.compile(r'`(.*?)\'')
        text = reSmartQuotes.sub(lambda m: "\'" + m.group(1) + "\'", text)

        # Remove empty paragraphs
        reEmptyP = re.compile(r'<p></p>')
        text = reEmptyP.sub('', text)

        return text

    def getTikzTemplateArgs(self):
        tikzPath = self.config.get('tikz_template')
        if tikzPath:
            logger.debug('Using tikz template: ' + tikzPath)
            return "--tikz-template=%s" % tikzPath
        else:
            return ""

    def runPlastex(self, sourceItem):
        logger.debug(sourceItem.source)
        root_dir = self.get_root_dir()
        outPath = root_dir / self.tmpDir
        outPaux = root_dir / self.temp_path()
        inPath = root_dir / sourceItem.source

        cmd = 'plastex --dir={outPath} \
		{tikzArgs} \
		--sec-num-depth=3 --toc-depth=3 --split-level=-1 --toc-non-files\
		--renderer=HTML5ncl --base-url={baseURL}\
		--paux-dirs={outPaux} \
		--filename={outFile} {inPath} 2>&1'.format(
            outPath=outPath,
            tikzArgs=self.getTikzTemplateArgs(),
            baseURL=self.get_web_root(),
            outPaux=outPaux,
            outFile=sourceItem.url,
            inPath=inPath
        )

        logger.info('Running plastex on {}'.format(sourceItem))
        logger.debug(cmd)
        proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        stdout = proc.stdout.read().decode('utf-8')
        proc.stdout.close()

        rc = proc.wait()
        if rc != 0:
            sys.stderr.write("Error: Something went wrong with the latex compilation! Quitting...\n")
            logger.debug(stdout)
            sys.stderr.write("(Use -vv for more information)\n")
            sys.exit(2)

    def getEmbeddedImages(self, texContents, title):
        logger.debug('    Moving embedded images:')
        # Markdown Images

        # TODO: make this extensible
        patterns = [
            re.compile(r'!\[[^\]]*\]\((?P<url>[^\)]*)\)'),
            re.compile(r'<object class=\"tikzpicture\" data=\"(?P<url>[^\)]*)\" type=\"image/svg\+xml\">'),
        ]

        def fix_image_path(m):
            raw_path = Path(m.group('url'))
            inFile = raw_path.name
            inPath = self.get_root_dir() / self.tmpDir / 'images' / inFile
            outPath = self.get_build_dir() / 'static' / title / inFile
            logger.debug('        %s => %s' % (inPath, outPath))

            # Move the file into build tree's static dir
            mkdir_p(outPath.parent)
            shutil.copyfile(str(inPath), str(outPath))

            # Update the output of plastex to reflect the change
            finalPath = str(Path('./build/static') / title / inFile)
            start, end = m.span('url')
            start -= m.start()
            end -= m.start()
            img = m.group(0)
            return img[:start] + finalPath + img[end:]

        for pattern in patterns:
            texContents = pattern.sub(fix_image_path, texContents)

        return texContents
