from pprint import pprint

import hug

from portray import api

cli = hug.cli(api=hug.API(__name__))
cli(api.html)
cli.output(pprint)(api.read_config)
