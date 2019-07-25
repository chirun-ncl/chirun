import logging
import re
from . import gen_dict_extract

logger = logging.getLogger(__name__)

def getVimeoHTML(code):
    return '<div class="vimeo-aspect-ratio"><iframe class="vimeo" src="https://player.vimeo.com/video/' + code + '" frameborder="0" \
                            webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe></div>'

def getRecapHTML(code):
    return '<div class="recap-aspect-ratio"><iframe class="recap" src="https://campus.recap.ncl.ac.uk/Panopto/Pages/Embed.aspx?id=' + code + '&v=1" \
                            frameborder="0" gesture=media webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe></div>'

def getYoutubeHTML(code):
    return '<div class="youtube-aspect-ratio"><iframe class="youtube" src="https://www.youtube.com/embed/' + code + '?ecver=1" \
                            frameborder="0" allowfullscreen></iframe></div>'

def getNumbasHTML(URL):
    return '<iframe class="numbas" src="' + URL + '" frameborder="0"></iframe>'

def replaceLabels(course, mdContents):
    for l in gen_dict_extract('label', course.config):
        mdLink = re.compile(r'\[([^\]]*)\]\(' + l['label'] + r'\)')
        mdContents = mdLink.sub(lambda m: "[" + m.group(1) + "](" + course.get_web_root() + l['outFile'] + ".html)", mdContents)
    return mdContents

def burnInExtras(course, mdContents, force_local, out_format):
    mdContentsOrig = mdContents
    reVimeo = re.compile(r'{%vimeo\s*([\d\D]*?)\s*%}')
    reRecap = re.compile(r'{%recap\s*([\d\DA-z-]*?)\s*%}')
    reYoutube = re.compile(r'{%youtube\s*([\d\D]*?)\s*%}')
    reNumbas = re.compile(r'{%numbas\s*([^%{}]*?)\s*%}')
    reSlides = re.compile(r'{%slides\s*([^%{}]*?)\s*%}')
    if out_format == 'pdf':
        mdContents = reVimeo.sub(lambda m: r"\n\n\url{https://vimeo.com/" + m.group(1) + "}", mdContents)
        mdContents = reRecap.sub(lambda m: r"\n\n\url{https://campus.recap.ncl.ac.uk/Panopto/Pages/Viewer.aspx?id=" + m.group(1) + "}", mdContents)
        mdContents = reYoutube.sub(lambda m: r"\n\n\url{https://www.youtube.com/watch?v=" + m.group(1) + "}", mdContents)
        mdContents = reNumbas.sub(lambda m: r"\n\n\url{" + m.group(1) + "}", mdContents)
    else:
        mdContents = reVimeo.sub(lambda m: getVimeoHTML(m.group(1)), mdContents)
        mdContents = reRecap.sub(lambda m: getRecapHTML(m.group(1)), mdContents)
        mdContents = reYoutube.sub(lambda m: getYoutubeHTML(m.group(1)), mdContents)
        mdContents = reNumbas.sub(lambda m: getNumbasHTML(m.group(1)), mdContents)

    if mdContents != mdContentsOrig:
        logger.debug('    Embedded iframes & extras.')
    mdContents = replaceLabels(course, mdContents)
    return mdContents
