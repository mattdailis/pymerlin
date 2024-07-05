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