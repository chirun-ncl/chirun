window.MathJax = {
  tex: {
    macros: {
      mathsterling: '{\\unicode{xA3}}',
      pounds: '{\\unicode{xA3}}',
      euro: '\\unicode{x20AC}',
      bm: ["\\boldsymbol{ #1 }",1],
      lefteqn: ["\\rlap{ #1 }\\quad",1],
      qedhere: "\\tag*{$\\blacksquare$}",
      pause: ''
    },
    inlineMath: [['\\(','\\)']],
    autoload: {},
    packages: {'[+]': [
        'noerrors',
        'mhchem',
        'textmacros',
        'mathtools'
    ]},
    textmacros: {
      packages: {'[+]': ['bbox']}
    }
  },
  startup: {
    typeset: true,
    ready: () => {
      MathJax.startup.defaultReady();
      MathJax.startup.promise.then(() => {
        window.mathjax_is_loaded = 1;
      });
    }
  },
  options: {
    ignoreHtmlClass: 'tex2jax_ignore',
    processHtmlClass: 'tex2jax_process',
    renderActions: {
      findScript: [10, function (doc) {
        for (const node of document.querySelectorAll('script[type^="math/tex"]')) {
          const display = !!node.type.match(/; *mode=display/);
          const math = new doc.options.MathItem(node.textContent, doc.inputJax[0], display);
          const text = document.createTextNode('');
          node.parentNode.replaceChild(text, node);
          math.start = {node: text, delim: '', n: 0};
          math.end = {node: text, delim: '', n: 0};
          doc.math.push(math);
        }
      }, '']
    }
  },
  loader: {
    load: [
        '[tex]/noerrors',
        '[tex]/mhchem',
        '[tex]/textmacros',
        '[tex]/bbox',
        '[tex]/mathtools'
    ]
  }
};
