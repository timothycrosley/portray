from hypothesis_auto import auto_test

from portray import render


def test_mkdocs_config():
    auto_test(
        render._mkdocs_config,
        _auto_allow_exceptions=(render._mkdocs_exceptions.ConfigurationError,),
    )
