import re

from anytree import Node

from bs4 import BeautifulSoup

import requests


def champion_gg_scraper(champion: str, role: str, matchup: str, verbose: bool) -> Node:
    if role.startswith("m"):
        role = "Middle"
    if matchup != "":
        url = f"https://champion.gg/champion/{champion}/{role}/overview/{matchup}"
        root = Node(
            f"{champion.title()} {role.title()} vs {matchup.title()} from Champion.gg"
        )
    else:
        url = f"https://champion.gg/champion/{champion}/{role}/"
        root = Node(f"{champion.title()} {role.title()} from Champion.gg")
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    # Parse the webpage
    # Divide webpage into relevant pieces
    if matchup != "":
        relevant_tags = soup.find_all(class_="Inner-sc-7vmxjm-0 cpZSJT")
        items = relevant_tags[2].contents[0].contents[0]
        runes_webpage = relevant_tags[2].contents[0].contents[1]
    else:
        relevant_tags = soup.find_all(class_="Inner-sc-7vmxjm-0 cpZSJT")
        items = relevant_tags[1].contents[0].contents[0]
        runes_webpage = relevant_tags[1].contents[0].contents[1]
    # Create tree nodes
    summoners = Node("Summoner Spells", parent=root)
    build = Node("Build", root)
    starters = Node("Starter Items", build)
    core = Node("Build Path", build)
    final = Node("Final Build", build)
    tree_runes = Node("Runes", root)
    tree_shards = Node("Shards", root)
    # Summoner Spells
    spells = list(
        set(
            re.findall(
                r"Summoner(.*).png", str(items.find_all(class_="sc-fONwsr bsxfkk"))
            )
        )
    )
    for cycle, entry in enumerate(spells):
        # Ignite is referred to as Dot
        if entry == "Dot":
            Node("Ignite", summoners)
            spells[cycle] = "Ignite"
        else:
            Node(entry, summoners)
    # Starting items
    for entry in items.contents[0].find_all("img"):
        if entry.attrs["alt"] != "":
            Node(entry.attrs["alt"], starters)
    # Core build path
    for entry in items.contents[1].find_all("img"):
        Node(entry.attrs["alt"], core)
    # Final build
    for entry in items.contents[2].find_all("img"):
        Node(entry.attrs["alt"], final)
    # Runes and shards
    runes = runes_webpage.find_all(champion_gg_runes)
    for entry in runes[:6]:
        Node(entry.contents[0], tree_runes)
    for entry in runes[6:]:
        Node(entry.contents[0], tree_shards)
    return root


def champion_gg_runes(tag):
    """Filter function that returns true for tags with the names of Runes in Champion.gg"""
    if "class" in tag.attrs:
        if "ChampionRuneSmallCHGG__RuneName-sc-1vubct9-5" in tag.attrs[
            "class"
        ] and not re.compile("sc-").search(tag.attrs["class"][1]):
            return tag
