import logging
import itertools
import re
from bs4 import BeautifulSoup
from pathlib import Path
from base64 import b64encode
from .oembed import get_oembed_html
from urllib.parse import urlparse
from .render import Renderer

logger = logging.getLogger(__name__)


def html_fragment(source):
    """
        Parse an HTML string representing a single element, and return that element
    """
    return BeautifulSoup(source, 'html.parser').contents[0]


def replace_tag(name):
    def dec(fn):
        def wrapper(soup, **kwargs):
            for t in soup.find_all(name):
                t.replace_with(fn(t, **kwargs))
        return wrapper
    return dec


@replace_tag('numbas-embed')
def embed_numbas(embed, **kwargs):
    item = kwargs['item']
    renderer = Renderer(item.course)
    context = {
        'id': embed['data-id'],
        'url': embed['data-url'],
        'cta': embed.get('data-cta', None),
        'item': item,
    }
    numbas_div = html_fragment(renderer.render_template('filter/embed_numbas.html', context))
    return numbas_div


@replace_tag('vimeo-embed')
def embed_vimeo(embed, **kwargs):
    div = html_fragment('<div class="vimeo-aspect-ratio"><iframe class="vimeo" frameborder="0" \
                            webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe></div>')
    div.iframe['src'] = "https://player.vimeo.com/video/" + embed['data-id']
    return div


@replace_tag('youtube-embed')
def embed_youtube(embed, **kwargs):
    div = html_fragment('<div class="youtube-aspect-ratio"><iframe class="youtube" \
                            frameborder="0" allowfullscreen></iframe></div>')
    div.iframe['src'] = "https://www.youtube.com/embed/{code}?ecver=1".format(code=embed['data-id'])
    return div


@replace_tag('recap-embed')
def embed_recap(embed, **kwargs):
    div = html_fragment('<div class="recap-aspect-ratio"><iframe class="recap" \
                            frameborder="0" allowfullscreen></iframe></div>')
    div.iframe['src'] = ("https://campus.recap.ncl.ac.uk/Panopto/Pages/Embed.aspx?id={code}&v=1"
                         .format(code=embed['data-id']))
    return div


@replace_tag('numbas-embed')
def link_numbas(embed, **kwargs):
    div = (html_fragment('<div><p><a href="{}" target="_blank">{}</a></p></div>'
           .format(embed['data-url'], embed.get('data-cta', "Test Yourself"))))
    return div


@replace_tag('youtube-embed')
def link_youtube(embed, **kwargs):
    div = (html_fragment('<div><p><a href="{}" target="_blank">{}</a></p></div>'
           .format(embed['data-id'], "Click to go to Youtube")))
    return div


@replace_tag('oembed')
def oembed(embed, **kwargs):
    url = embed['data-url']
    html = get_oembed_html(url)
    embed_code = BeautifulSoup(html, 'html.parser')
    d = html_fragment('<div class="oembed"></div>')
    o = urlparse(url)
    d['data-embed-domain'] = o.netloc
    for t in embed_code.contents:
        d.append(t)
    return d


def fix_local_links(soup, item):
    """
        Rewrite URLs relative to the top level, i.e. those starting with a /,
        to use the course's root URL or into paths relative to the item.
    """
    tags = {
        'a': ['href'],
        'img': ['src'],
        'source': ['src'],
        'section': ['data-background', 'data-background-video'],
    }

    for tag, attrs in tags.items():
        for el in soup.find_all(tag):
            for attr in attrs:
                url = el.get(attr)
                if url and url[0] == '/':
                    el[attr] = item.course.make_relative_url(item, url[1:])


def dots_pause(soup, item):
    """
        Rewrite three dots on thier own paragraph into a set of divs with
        class "fragment" applied. This is used in slideshows to create pauses
    """
    pauses = soup.find_all("p", string=re.compile(r"\. \. \."))
    for el in pauses:
        next_els = list(el.next_siblings)
        next_els.remove('\n')
        if len(next_els) > 0:
            # There are some elements after this one within the <section>.
            els = [i for i in itertools.takewhile(
                lambda x: x.name != 'hr' and x not in pauses, el.next_siblings)]
            fragment = soup.new_tag('div', attrs={"class": "fragment"})
            el.wrap(fragment)
            el.decompose()
            for tag in els:
                fragment.append(tag)
        else:
            # There are no other elements, so fragment the entire next section
            el.parent.next_sibling['class'] = el.parent.next_sibling['class'] + ['fragment']
            el.decompose()


def list_fragment(soup, item):
    for li in soup.find_all("li"):
        li['class'] = li.get('class', []) + ['fragment']


def mathjax_script_dollar(soup, item):
    """
        Rewrite MathJax math/tex scripts to use dollars instead.
        Useful for notebooks where we have less control over MathJax.
    """
    for el in soup.find_all('script'):
        if 'math/tex' in el.attrs['type']:
            el.name = 'span'
            del el.attrs['type']
            el.string = '${}$'.format(el.string)


def links_to_data_uri(soup, item):
    """
        Rewrite links into to embedded data-uri streams
        Useful for jupyter notebooks where'd like things to be self contained
    """
    tags = {
        'a': ['href'],
        'img': ['src'],
        'source': ['src'],
    }
    filetypes = {
        '.png': 'data/png',
        ".jpg": 'data/jpeg',
        ".jpeg": 'data/jpeg'
    }

    for tag, attrs in tags.items():
        for el in soup.find_all(tag):
            for attr in attrs:
                url = el.get(attr)
                if not url.startswith(('http://', 'https://', 'ftp://')):
                    for ft in filetypes.keys():
                        if ft in url:
                            src_path = item.course.get_build_dir() / item.out_path / Path(url)
                            with open(str(src_path), 'rb') as f:
                                data = b64encode(f.read()).decode('ascii')
                                el[attr] = 'data:{};base64,{}'.format(filetypes[ft], data)
                            break

def remove_output_cells(nb, item):
    nb.cells = list(filter(lambda cell: cell.get('cell_type','') != 'code' or
                       'output' not in cell.get('metadata', {}).get('attributes', {}).get('classes',[]), nb.cells))

class HTMLFilter(object):
    filters = [embed_recap, embed_numbas, embed_vimeo, embed_youtube,
               oembed, fix_local_links, dots_pause]

    def apply(self, item, html, out_format):
        soup = BeautifulSoup(html, 'html.parser')
        for f in self.filters:
            f(soup, item=item)
        return str(soup)

class CellHTMLFilter(HTMLFilter):
    filters = [link_numbas, link_youtube, mathjax_script_dollar, fix_local_links, links_to_data_uri]

class CellFilter(object):
    filters = [remove_output_cells]

    def apply(self, item, nb):
        for f in self.filters:
            f(nb, item=item)
        return nb
