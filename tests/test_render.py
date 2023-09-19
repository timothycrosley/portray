import pathlib

from hypothesis_auto import auto_test
from portray import render


def test_mkdocs_config():
    auto_test(
        render._mkdocs_config,
        auto_allow_exceptions_=(render._mkdocs_exceptions.ConfigurationError,),
    )


def test_document_sort(temporary_dir):
    temporary_dir = pathlib.Path(temporary_dir)

    # create dummy files: a.md, b.md, c.md, ..., z.md
    files = []
    for i in range(ord("a"), ord("z") + 1):
        file = temporary_dir.joinpath(f"{chr(i)}.md")
        file.touch()
        files.append(str(file))

    # sort files (no index.md)
    docs = render._sorted_docs(temporary_dir)
    assert docs == files

    # add index.md
    file = temporary_dir.joinpath("index.md")
    file.touch()
    files.insert(0, str(file))  # index.md have to be first!

    # sort files (with index.md)
    docs = render._sorted_docs(temporary_dir)
    assert docs == files
