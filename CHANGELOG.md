Install the latest
===================

To install the latest version of portray simply run:

`pip3 install portray`

OR

`poetry add portray`

OR

`pipenv install portray`

see the [Installation QuickStart](https://timothycrosley.github.io/portray/docs/quick_start/1.-installation/) for more instructions.

Changelog
=========
## 1.3.1 - September 22 2019
- Fixed [Issue 43](https://github.com/timothycrosley/portray/issues/43) - Automatically remap `-` to `_` when attempting to auto-determine module name.

## 1.3.0 - September 15 2019
- Potentially backward compatibility breaking performance optimization: portray now only renders root project files + the specified documentation directory + any specified extra_dirs.
  If a previously utilized file used to be auto included, but is no longer, you can force its inclusion by adding its directory to `extra_dirs.`
  For many projects, this change results in a significantly smaller output size and significantly faster documentation generation.
- Implemented [Issue 31](https://github.com/timothycrosley/portray/issues/31) - Improved repository auto-discovery and formatting.
- Fixed [Issue 33](https://github.com/timothycrosley/portray/issues/33) - Improving usability and documentation of nav customization.
- Added many additional test cases - Reaching 100% test coverage.
- Added indicators that let users know what step is occurring during documentation generation.

## 1.2.4 - September 5 2019
- Fixed [Issue 23](https://github.com/timothycrosley/portray/issues/23) - A confirmed regression from moving to `pdocs` that caused root modules to not be auto included.

## 1.2.3 - September 4 2019
- Fixed a bug specifying the output dir for `as_html` command from the command line.
- Updated to use Python3.6+ style variable annotations.

## 1.2.2 - September 4 2019
- Fixed a bug specifying modules from command line when no configuration file is present.

## 1.2.1 - September 3 2019
- General improvements to reference code documentation rendering

## 1.2.0 - September 3 2019
Potentially breaking dependency change release from pdoc3 to [pdocs](https://timothycrosley.github.io/pdocs/).

### Migration guide:

- `pyproject.toml` config section changes from `[tool.portray.pdoc3]` to `[tool.portray.pdocs]`
- Type annotations are no longer toggleable but are rather always on.

## 1.1.0 - August 29 2019
Minor Feature release w/ Bug Fixes

- Added support for specifying modules directly from the CLI and API.
- Added auto module detect for simple setup.py files.
- Improved CLI subcommand documentation.
- Implemented [Issue 12](https://github.com/timothycrosley/portray/issues/12) - Clarify what a "project" is in documentation.
- Fixed [Issue 2](https://github.com/timothycrosley/portray/issues/2) - UnicodeEncodeError except when running portray.
- Fixed [Issue 10](https://github.com/timothycrosley/portray/issues/10) - Class methods rendered incorrectly.
- Fixed [Issue 17](https://github.com/timothycrosley/portray/issues/17) - Portray silently requires README.md file.

## 1.0.5 - August 26 PM 2019
Bug fix release

- Fixed [Issue 6](https://github.com/timothycrosley/portray/issues/6) - Failed to open web-browser on startup.
- Fixed [Issue 5](https://github.com/timothycrosley/portray/issues/5) - Some links are missing a trailing slash.
- Fixed [Issue 4](https://github.com/timothycrosley/portray/issues/4) - Class references generate large code block.

Big thanks to Marcel Hellkamp ([@defnull](https://github.com/defnull)) for fixing these issues.

## 1.0.0 - August 26 AM 2019
Initial API stable release of portray
