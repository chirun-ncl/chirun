import logging
import re
from . import gen_dict_extract
from bs4 import BeautifulSoup
from .oembed import get_oembed_html
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def html_fragment(source):
    """
        Parse an HTML string representing a single element, and return that element
    """
    return BeautifulSoup(source,'html.parser').contents[0]

def replace_tag(name):
    def dec(fn):
        def wrapper(soup, **kwargs):
            for t in soup.find_all(name):
                t.replace_with(fn(t))
        return wrapper
    return dec

@replace_tag('numbas-embed')
def embed_numbas(embed):
    iframe = html_fragment('<iframe class="numbas" frameborder="0"></iframe>')
    iframe['src'] = embed['data-url']
    return iframe

@replace_tag('vimeo-embed')
def embed_vimeo(embed):
    div = html_fragment('<div class="vimeo-aspect-ratio"><iframe class="vimeo" frameborder="0" \
                            webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe></div>')
    div.iframe['src'] = "https://player.vimeo.com/video/" + embed['data-id']
    return div

@replace_tag('youtube-embed')
def embed_youtube(embed):
    div = html_fragment('<div class="youtube-aspect-ratio"><iframe class="youtube" \
                            frameborder="0" allowfullscreen></iframe></div>')
    div.iframe['src'] = "https://www.youtube.com/embed/{code}?ecver=1".format(code=embed['data-id'])
    return div

@replace_tag('oembed')
def oembed(embed):
    url = embed['data-url']
    html = get_oembed_html(url)
    embed_code = BeautifulSoup(html,'html.parser')
    d = html_fragment('<div class="oembed"></div>')
    o = urlparse(url)
    d['data-embed-domain'] = o.netloc
    for t in embed_code.contents:
        d.append(t)
    return d

def fix_refs(soup, course):
    for a in soup.find_all('a',{'class':'ref'}):
        a['href'] = course.get_web_root() + a['href']

def fix_local_links(soup, course):
    """
        Rewrite URLs relative to the top level, i.e. those starting with a /,
        to use the course's root URL if they don't already.
    """
    root = course.get_web_root()
    for a in soup.find_all('a'):
        url = a.get('href')
        if url and url[0]=='/' and url[:len(root)]!=root:
            url = root + url[1:]
            a['href'] = url


def burnInExtras(course, html, force_local, out_format):
    soup = BeautifulSoup(html, 'html.parser')
    filters = [embed_numbas, embed_vimeo, embed_youtube, oembed, fix_local_links]
    for f in filters:
        f(soup, course=course)
    return str(soup)
