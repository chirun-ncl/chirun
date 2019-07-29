from pyoembed import oEmbed
import json

oembed_cache = {}
default_cache_filename = 'oembed-cache.json'

def load_cache(cache_filename=default_cache_filename):
    try:
        with open(str(cache_filename)) as f:
            oembed_cache.update(json.load(f))
    except FileNotFoundError:
        pass

def get_oembed_html(url):
    if url not in oembed_cache:
        res = oEmbed(url)
        oembed_cache[url] = res['html']
    return oembed_cache[url]

def save_cache(cache_filename=default_cache_filename):
    with open(str(cache_filename),'w') as f:
        json.dump(oembed_cache,f)
