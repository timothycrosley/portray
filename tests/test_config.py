import mkdocs.config
import mkdocs.exceptions
import pytest

from portray import config


def test_mkdocs():
    """Test to ensure we are able to create a mkdocs config object with the expected values"""
    mkdocs_config = config.mkdocs()
    assert isinstance(mkdocs_config, mkdocs.config.base.Config)
    for key, value in config.MKDOCS_DEFAULTS.items():
        if type(value) == dict:
            for nested_key, nested_value in value.items():
                if type(nested_value) == dict:
                    continue

                assert getattr(mkdocs_config[key], nested_key) == nested_value
        else:
            assert mkdocs_config[key] == value

    # Test a simple failure case
    with pytest.raises(mkdocs.exceptions.ConfigurationError):  # Can't set . as doc directory
        assert config.mkdocs(docs_dir=".") == config.MKDOCS_DEFAULTS

    # Test overriding config values
    mkdocs_config = config.mkdocs(custom="value", custom_2=1)
    assert isinstance(mkdocs_config, mkdocs.config.base.Config)
    assert mkdocs_config["custom"] == "value"
    assert mkdocs_config["custom_2"] == 1
