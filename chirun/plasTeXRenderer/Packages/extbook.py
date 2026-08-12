def ProcessOptions(options, document):
    # Extend the book documentclass
    from plasTeX.Packages import book
    book.ProcessOptions(options, document)