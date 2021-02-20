import re

from anytree import Node

from bs4 import BeautifulSoup

import requests


def mobalytics_scraper(champion: str, role: str, *args) -> Node:
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
    for cycle, entry in enumerate(soup.find_all("div", class_="ednsys62 css-1taoj5l ehobrmq2")):
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
