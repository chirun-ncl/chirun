from bs4 import BeautifulSoup

from . import slugify

class HTMLFilter(object):
    filters = []

    def apply(self, item, html):
        # An empty comment at the start is added to avoid bs4's MarkupResemblesLocatorWarning
        soup = BeautifulSoup('<!-- -->' + html, 'html.parser')
        next(soup.children).extract()                        # and removed immediately, once the HTML is parsed.

        self.apply_filters(soup, item)

        headers = self.find_header_hierarchy(soup)

        return str(soup), headers

    def apply_filters(self, soup, item):
        for f in self.filters:
            f(soup, item=item)

    def find_header_hierarchy(self, soup):
        def id_for(element):
            try:
                return element['id']
            except KeyError:
                text = element.text
                n = 0
                while soup.find(id=slugify(text, n)) is not None:
                    n += 1
                slug = slugify(text, n)
                element['id'] = slug
                return slug

        def level_for(element):
            header_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
            try:
                return header_tags.index(element.name.lower())
            except ValueError:
                return len(header_tags)

        def make_hierarchy(items):
            i = 0
            out = []
            while i < len(items):
                level, e = items[i]
                i += 1
                start = i
                while i < len(items) and items[i][0] > level:
                    i += 1

                children = make_hierarchy(items[start:i])
                text = e.decode_contents()

                out.append({'text': text, 'id': id_for(e), 'children': children})

            return out

        flat_headers = [(level_for(h), h) for h in soup.select('h1,h2,h3,h4,h5,h6')]

        headers = make_hierarchy(flat_headers)

        return headers

