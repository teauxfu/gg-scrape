import re

from anytree import Node

from bs4 import BeautifulSoup

import requests


def mobalytics_scraper(champion: str, role: str, matchup: str, verbose: bool) -> Node:
    """Scrapes a build from Mobalytics.gg."""

    url = f"https://app.mobalytics.gg/lol/champions/{champion}/build?role={role}"
    # make soup from the URL
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    c = soup.find("p", class_="css-1yvcufn eo6ba8g4").text
    r = soup.find("div", class_="css-p3pzap eo6ba8g5").text

    # create tree entries for default output
    title = f"{c} {r} from Mobalytics"
    root = Node(title)

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
    if verbose:
        shards = Node("Shards", parent=root)
    for entry in matches:
        shard_id = entry["src"].split(".png")[0][-4:]  # was blah/####.png
        shard = conversion.get(shard_id)
        if verbose:
            Node(shard, parent=shards)
        else:
            Node(shard, parent=runes)
    
    # get the build
    build = Node("Build", parent=root)

    # get time targets
    if verbose:
        time_targets = []
        matches = soup.find_all("p", class_="css-1ofmdln ehobrmq7")
        for entry in matches:
            time_targets.append(entry.text)
        print(time_targets)

    # add all relevant entries
    for cycle, entry in enumerate(soup.find_all("div", class_="ednsys62 css-1taoj5l ehobrmq2")):
        # Starter items
        if cycle == 0 and verbose:
            starter = Node(f"Starter Items {time_targets[cycle]}", parent=build)
            for content in entry.contents:
                Node(re.findall(r"alt=\"(.*)\" c", str(content))[0], starter)
        # Early items
        if cycle == 1 and verbose:
            early = Node(f"Early Items {time_targets[cycle]}", parent=build)
            for content in entry.contents:
                Node(re.findall(r"alt=\"(.*)\" c", str(content))[0], early)
        # Core Build
        if cycle == 2 and verbose:
            core = Node(f"Core Items {time_targets[cycle]}", parent=build)
            for content in entry.contents:
                Node(re.findall(r"alt=\"(.*)\" c", str(content))[0], core)
        # Full Build
        if cycle == 3:
            if verbose:
                full = Node(f"Final Items", parent=build)
                for content in entry.contents:
                    Node(re.findall(r"alt=\"(.*)\" c", str(content))[0], full)
            else:
                for content in entry.contents:
                    Node(re.findall(r"alt=\"(.*)\" c", str(content))[0], build)
    
    # Situational items
    if verbose:
        situational = Node("Situational Items", parent=build)
        for entry in soup.find_all("div", class_="css-143dzw8 es5thxd2"):
            Node(re.findall(r"alt=\"(.*)\" c", str(entry.contents[0]))[0], situational)

        # Skill Learn Order
    # for entry in soup.find_all("div", class_="css-70qvj9 ek7zqkr0")[0].contents:
    #     if entry.name == "p":
    #         Node(entry.text, skill)

    # Skill Max Order
    skill = Node("Skill Priority", parent=root)
    # this makes a list of the skill taken at each level
    sequence = []
    for entry in soup.find_all("div", class_="css-1dai7ia eaoplg14"):
        sequence.append(entry.text) 
    # this dict has Q W E keys and values of the level when they get maxed
    max_order = {}
    for ability in ["Q", "W", "E"]:
        max_order[ability] = [i for i, n in enumerate(sequence) if n == ability][3] # find the 4th occurrance of each
    # iterate over values and copy keys in order of value magnitude
    prio = []
    for i in range (19):
        if i in max_order.values():
            prio.append((list(max_order.keys())[list(max_order.values()).index(i)]))
    for item in prio:
        Node(item, skill)
        
    # return tree
    return root
