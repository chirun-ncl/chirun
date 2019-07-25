import logging
import sys
import datetime
from makeCourse import mkdir_p, yaml_header
from subprocess import Popen, PIPE

logger = logging.getLogger(__name__)

def run_pandoc(content, context=None, extra_args = []):
    """ 
        Run pandoc on the given content
    """
    cmd = ['pandoc'] + extra_args

    if context:
        content = yaml_header(context) + '\n\n' + content

    logger.debug(' '.join(cmd))
    proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)

    try:
        output, errs = proc.communicate(content.encode('utf-8'))
    except Exception:
        proc.kill()
        output, errs = proc.communicate()

    if errs:
        logger.error(errs.decode('utf-8'))
        logger.error("Something went wrong running pandoc! Quitting...")
        logger.error("(Use -vv for more information)")
        sys.exit(2)

    return output

def pandoc_item(course, item, template_file=None, out_format='html', force_local=False):
    """
        Render an item using pandoc
        (To be removed!)
    """
    root = course.get_web_root(force_local=force_local)
    outPath = course.get_build_dir() / (item.out_file.with_suffix('.' + out_format))
    outDir = outPath.parent
    mkdir_p(outDir)
    if template_file is None:
        template_file = item.template_name
    template_path = course.theme.source / template_file
    date = datetime.date.today()

    logger.debug('    {src} => {dest}'.format(src=item.title, dest=outPath))

    args = [
        '--mathjax={}'.format(course.mathjax_url),
        '-V', 'web_root={}'.format(root),
    ]
    if template_file == 'slides.revealjs':
        args += [
            '-i',
            '-t',
            'revealjs',
            '-V', 'revealjs-url={}/static/reveal.js'.format(root + course.theme.path),
        ]
    else:
        args += [
            '--toc',
            '--toc-depth=2',
            '--section-divs',
            '--listings',
            '--metadata=date:{}'.format(date),
        ]

    context = course.get_context()
    context.update(item.get_context())
    if item.parent:
        context['chapters'] = [item.get_context() for item in item.parent.content if not item.is_hidden]
    else:
        context['chapters'] = [item.get_context() for item in course.structure if not item.type == 'introduction' and not item.is_hidden]

    body = item.markdown_content(force_local=force_local, out_format=out_format)

    logger.info('Running pandoc on {}'.format(item))
    output = run_pandoc(body, context, args)

    with open(str(outPath),'wb') as f:
        f.write(output)

if __name__ == "__main__":
    pass
