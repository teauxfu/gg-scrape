"""Parses the CLI arguments."""

import time

import typer

from gg_scrape.champion_gg_scraper import champion_gg_scraper
from gg_scrape.mobalytics_scraper import mobalytics_scraper
from gg_scrape.lolalytics_scraper import lolalytics_scraper
from gg_scrape.print_tree import print_tree


ggs = typer.Typer()


@ggs.command()
def main(
    champion: str = typer.Argument(..., help="The champion you're playing"),
    role: str = typer.Argument("", help="The role you're playing", show_default=False),
    matchup: str = typer.Option("", "--matchup", "-m", help="Your opposing matchup", show_default=False),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show more verbose output"),
    scraper: str = typer.Option("champion.gg", "--scraper", "-s", help="Which site to scrape"),
):
    """Parses CLI arguments, makes some requests, then tries to print a tree."""
    
    if champion == "j4":
        champion = "jarvaniv"

    args = champion, role, matchup, verbose
    start = time.time()  # for funsies

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

    if scraper.startswith("m"):
        print_tree(mobalytics_scraper(*args))
    elif scraper.startswith("c"):
        print_tree(champion_gg_scraper(*args))
    elif scraper.startswith("lola"):
        print_tree(lolalytics_scraper(*args))

    print(f"\nFinished in {round(time.time() - start, 3)} s     ✨ glhf ✨")
    input()
