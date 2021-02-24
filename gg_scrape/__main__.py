# this file exists to support calling the package as 'python -m ggs'
# https://typer.tiangolo.com/tutorial/package/#support-python-m-optional

from gg_scrape.argsparse import ggs

ggs(prog_name="ggs")
