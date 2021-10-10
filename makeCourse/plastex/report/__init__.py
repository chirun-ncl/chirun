from plasTeX.Packages.book import *  # noqa: F401, F403


def ProcessOptions(options, document):
    from plasTeX.Packages import book
    book.ProcessOptions(options, document)
    document.context['theequation'].format = '${chapter}.${equation}'
