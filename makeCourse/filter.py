import logging
import itertools
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
    numbas_div = html_fragment("""<div class="numbas_container">
            <div class="feedback_bar" id="{id}_feedback">
                <button class="btn btn-danger" data-target="#{id}_collapse" data-toggle="collapse">
                    Test Yourself
                </button>
                <div class="feedback_right" id="{id}_info">
                    Best score:
                    <span class="mr-1" id="{id}_score">0</span>/<span class="mr-3 ml-1" id="{id}_marks">0</span>
                    Completed:
                    <span class="complete" id="{id}_complete" style="display: none;">✔</span>
                    <span class="incomplete" id="{id}_incomplete">✕</span>
                </div>
            </div>
            <div class="collapse-content collapse" id="{id}_collapse">
                <iframe height="200px" id="{id}" src="{url}" width="100%">
                </iframe>
            </div>
            <script>
                document.getElementById("{id}").addEventListener("load", function(){{
                    setTimeout(function(){{
                        loadNumbasFeedback("{id}");
                    }},200);
                }});
                window.addEventListener('message', function(event) {{
                    var data = JSON.parse(event.data);
                    if('message' in data) {{
                        switch(data['message']){{
			                case 'exam_ready':
                                setTimeout(function(){{
                                    postToFrames(
                                        document.getElementById("{id}").contentWindow.frames,
                                        JSON.stringify({{"message":"send_id","id":"{id}"}}),
                                        "*"
                                    );
                                }},0);
                            break;
                        }}
                    }}
                }});
            </script>
        </div>""".format(id=embed['data-id'], url=embed['data-url']))
    return numbas_div

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

@replace_tag('recap-embed')
def embed_recap(embed):
    div = html_fragment('<div class="recap-aspect-ratio"><iframe class="recap" \
                            frameborder="0" allowfullscreen></iframe></div>')
    div.iframe['src'] = "https://campus.recap.ncl.ac.uk/Panopto/Pages/Embed.aspx?id={code}&v=1".format(code=embed['data-id'])
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

def fix_local_links(soup, item):
    """
        Rewrite URLs relative to the top level, i.e. those starting with a /,
        to use the course's root URL or into paths relative to the item.
    """
    root = item.course.get_web_root()
    tags = {
        'a': ['href'],
        'img':['src'],
        'source':['src'],
        'section': ['data-background','data-background-video'],
    }

    for tag, attrs in tags.items():
        for el in soup.find_all(tag):
            for attr in attrs:
                url = el.get(attr)
                if url and url[0]=='/':
                    el[attr] = item.course.make_relative_url(item,url[1:])

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
            el.parent.next_sibling['class'] = el.parent.next_sibling['class']+['fragment']
            el.decompose()

def list_fragment(soup, item):
    for li in soup.find_all("li"):
        li['class'] = li.get('class', []) + ['fragment']

def burnInExtras(item, html, out_format):
    soup = BeautifulSoup(html, 'html.parser')
    filters = [embed_recap, embed_numbas, embed_vimeo, embed_youtube,
            oembed, fix_local_links, dots_pause]
    for f in filters:
        f(soup, item=item)
    return str(soup)
