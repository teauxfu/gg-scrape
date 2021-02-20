import time

import typer

from .champion_gg_scraper import champion_gg_scraper
from .mobalytics_scraper import mobalytics_scraper
# from .vanilla_scraper import vanilla_scraper
from .print_tree import print_tree

ggs = typer.Typer()


@ggs.command()
def main(
    champion: str = typer.Argument(..., help="The champion you're playing"),
    role: str = typer.Argument("", help="The role you're playing", show_default=False),
    matchup: str = typer.Argument("", help="Your opposing matchup", show_default=False),
    scraper: str = typer.Argument("m", help="Which site to scrape", show_default=False),
    verbose: str = typer.Option(False, help="Show more verbose output"),
):
    args = champion, role, matchup, verbose
    start = time.time() # for funsies

    if role.startswith("m"):
        role = "mid"
    elif role.startswith(("a", "b")):
        role = "adc"
    elif role.startswith("j"):
        role = "jungle"
    elif role.startswith("t"):
        role = "top"
    elif role.startswith("s"):
        role = "support"

#    if scraper.startswith("v"):
#        print_tree(vanilla_scraper(*args))
    if scraper.startswith("m"):
        print_tree(mobalytics_scraper(*args))
    elif scraper.startswith("c"):
        print_tree(champion_gg_scraper(*args))

    print(f"\nFinished in {round(time.time() - start, 3)} s     ✨ glhf ✨")
    input()