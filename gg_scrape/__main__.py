# this file exists to support calling the package as 'python -m pip ggs'
# https://typer.tiangolo.com/tutorial/package/#support-python-m-optional

from gg_scrape.main import ggs
ggs(prog_name='ggs')
