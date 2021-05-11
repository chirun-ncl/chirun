Outline extension for Python-Markdown
=====================================

Wraps the document logical sections (as implied by h1-h6 headings).

By default, the wrapper element is a section tag having a class attribute
"sectionN", where N is the header level being wrapped. Also, the header
attributes get moved to the wrapper.


Installation
------------

    pip install git+git://github.com/aleray/mdx_outline.git


Usage
-----

    >>> import markdown
    >>> src = """
    ... # 1
    ... Section 1
    ... ## 1.1
    ... Subsection 1.1
    ... ## 1.2
    ... Subsection 1.2
    ... ### 1.2.1
    ... Hey 1.2.1 Special section
    ... ### 1.2.2
    ... #### 1.2.2.1
    ... # 2
    ... Section 2
    ... """.strip()
    >>> html = markdown.markdown(src, ['outline'])
    >>> print(html)
    <section class="section1"><h1>1</h1>
    <p>Section 1</p>
    <section class="section2"><h2>1.1</h2>
    <p>Subsection 1.1</p>
    </section><section class="section2"><h2>1.2</h2>
    <p>Subsection 1.2</p>
    <section class="section3"><h3>1.2.1</h3>
    <p>Hey 1.2.1 Special section</p>
    </section><section class="section3"><h3>1.2.2</h3>
    <section class="section4"><h4>1.2.2.1</h4>
    </section></section></section></section><section class="section1"><h1>2</h1>
    <p>Section 2</p>
    </section>

Divs instead of sections, custom class names:

    >>> src = """
    ... # Introduction
    ... # Body
    ... ## Subsection
    ... # Bibliography
    ... """.strip()
    >>> html = markdown.markdown(src, extensions=['outline(wrapper_tag=div, wrapper_cls=s%(LEVEL)d)'])
    >>> print(html)
    <div class="s1"><h1>Introduction</h1>
    </div><div class="s1"><h1>Body</h1>
    <div class="s2"><h2>Subsection</h2>
    </div></div><div class="s1"><h1>Bibliography</h1>
    </div>


By default, the header attributes are moved to the wrappers

    >>> src = """
    ... # Introduction {: foo=bar }
    ... """.strip()
    >>> html = markdown.markdown(src, extensions=['attr_list', 'outline'])
    >>> print(html)
    <section class="section1" foo="bar"><h1>Introduction</h1>
    </section>


Non consecutive headers shouldn't be a problem:

    >>> src="""
    ... # ONE
    ... ### TOO Deep
    ... ## Level 2
    ... # TWO
    ... """.strip()
    >>> html = markdown.markdown(src, extensions=['attr_list', 'outline'])
    >>> print(html)
    <section class="section1"><h1>ONE</h1>
    <section class="section3"><h3>TOO Deep</h3>
    </section><section class="section2"><h2>Level 2</h2>
    </section></section><section class="section1"><h1>TWO</h1>
    </section>


Dependencies
------------

* [Markdown 2.0+](http://www.freewisdom.org/projects/python-markdown/)


Copyright
---------

- 2011, 2012 [The active archives contributors](http://activearchives.org/)
- 2011, 2012 [Michael Murtaugh](http://automatist.org/)
- 2011, 2012 [Alexandre Leray](http://stdin.fr/)

All rights reserved.

This software is released under the modified BSD License. 
See LICENSE.md for details.


Further credits
---------------

This is a rewrite of the 
[mdx_addsection extension](http://git.constantvzw.org/?p=aa.core.git;a=blob;f=aacore/mdx_addsections.py;h=969e520a42b0018a2c4b74889fecc83a7dd7704a;hb=HEAD) 
we've written for [active archives](http://activearchives.org). The first
version had a bug with non hierachical heading structures. This is no longer a
problem: a couple of weeks ago, Jesse Dhillon pushed to github a similar plugin
which fixes the problem. Thanks to him, mdx\_outline no longer has the problem.


See also
--------

- <https://github.com/jessedhillon/mdx_sections>
- <http://html5doctor.com/outlines/>
