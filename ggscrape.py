import re
import time

from anytree import Node, RenderTree

from bs4 import BeautifulSoup

import click

import requests


@click.command()
@click.argument("champion")
@click.option("-r", "--role", default="", help="The role you're playing")
@click.option("-m", "--matchup", default="", help="Who you're playing against")
@click.option("-s", "--source", default="", help="Which site to scrape")
def clickparser(champion: str, role: str, matchup: str, source: str):
    start = time.time()  # for funsies
    if role.startswith("m"):
        role = "mid"
    elif role.startswith(("a", "b")):
        role = "adc"
    elif role.startswith("s"):
        role = "support"
    elif role.startswith("t"):
        role = "top"
    elif role.startswith("j"):
        role = "jungle"
    if source.startswith("m"):
        root = mobalytics_scraper(champion, role)
    if source.startswith("c"):
        root = champion_gg_scraper(champion, role, matchup)
        # print the thing
    for pre, _, node in RenderTree(root):
        print(f"{pre}{node.name}")
    print(f"\nFinished in {round(time.time() - start, 3)} s")
    input()


def mobalytics_scraper(champion: str, role: str) -> Node:
    url = f"https://app.mobalytics.gg/lol/champions/{champion}/build?role={role}"
    # make soup from the URL
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    c = soup.find("p", class_="css-1yvcufn eo6ba8g4").text
    r = soup.find("div", class_="css-p3pzap eo6ba8g5").text
    # make a tree to organize / render later
    root = Node(f"{c} {r} from Mobalytics")
    # get the runes
    runes = Node("Runes", parent=root)
    matches = soup.find_all("img", class_="css-1la33yl e16p94fx0")
    for entry in matches:
        r = entry["alt"]
        Node(r, parent=runes)
    # get the shards
    matches = soup.find_all("img", class_="css-1vgqbrs ed9gm2s1")
    conversion = {
        "5001": "Health",
        "5002": "Armor",
        "5003": "Magic Resist",
        "5005": "Attack Speed",
        "5007": "Ability Haste",
        "5008": "Adaptive Force",
    }
    shards = Node("Shards", parent=root)
    for entry in matches:
        shard_id = entry["src"].split(".png")[0][-4:]  # was blah/####.png
        shard = conversion.get(shard_id)
        Node(shard, parent=shards)
    # create tree entries
    build = Node("Build", parent=root)
    skill = Node("Skill Priority", parent=root)
    starter = Node("Starter Items", parent=build)
    early = Node("Early Items", parent=build)
    core = Node("Core Items", parent=build)
    full = Node("Full Build", parent=build)
    situational = Node("Situational Items", parent=build)
    # add all relevant entries
    for cycle, entry in enumerate(
        soup.find_all("div", class_="ednsys62 css-1taoj5l ehobrmq2")
    ):
        # Starter items
        if cycle == 0:
            for content in entry.contents:
                Node(re.findall(r"alt=\"(.*)\" c", str(content))[0], starter)
        # Early items
        if cycle == 1:
            for content in entry.contents:
                Node(re.findall(r"alt=\"(.*)\" c", str(content))[0], early)
        # Core Build
        if cycle == 2:
            for content in entry.contents:
                Node(re.findall(r"alt=\"(.*)\" c", str(content))[0], core)
        # Full Build
        if cycle == 3:
            for content in entry.contents:
                Node(re.findall(r"alt=\"(.*)\" c", str(content))[0], full)
    # Situational items
    for entry in soup.find_all("div", class_="css-143dzw8 es5thxd2"):
        Node(re.findall(r"alt=\"(.*)\" c", str(entry.contents[0]))[0], situational)
    # Skill Order
    for entry in soup.find_all("div", class_="css-70qvj9 ek7zqkr0")[0].contents:
        if entry.name == "p":
            Node(entry.text, skill)
    # return tree
    return root


def champion_gg_scraper(champion: str, role: str, matchup: str) -> Node:
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


clickparser()
