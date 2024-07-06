# Documentation

Contributions to this documentation are welcome!

This documentation lives in the `docs` directory, and is built
by running the following:

```shell
cd docs
make clean html
```

This documentation is built using [sphinx](https://www.sphinx-doc.org/en/master/) with the [MyST](https://mystmd.org/)
plugin, using the [Furo](https://pradyunsg.me/furo/) theme. Python docstrings are automatically parsed and included in
this documentation using the [sphinx-autodoc2](https://sphinx-autodoc2.readthedocs.io) extension.

## Style

Refer to [https://developers.google.com/style](https://developers.google.com/style) for guidance. Any particularly salient points should be reproduced in this document.

pymerlin is always lowercase. It may be styled as regular text or in a code block like this: `pymerlin` depending on the
context.

## Referencing Aerie

pymerlin documentation should be self-contained for users who are not using an Aerie deployment - this means that
some concepts will be repeated across pymerlin and Aerie documentation. In these scenarios, the relevant Aerie
documentation page should be linked in a "Further reading" section at the bottom of the page. 