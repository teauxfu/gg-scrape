"""Scrapes a build from Mobalytics.gg"""

import re

import requests
from anytree import Node
from bs4 import BeautifulSoup


def mobalytics_scraper(champion: str, role: str, matchup: str, verbose: bool) -> Node:
    """Scrapes a build from Mobalytics.gg and returns a tree."""
    soup = get_soup(champion, role)
    # mobalytics won't show build info for certain roles
    # when this happens, just redirect to the most popular allowed role ?
    # check if valid
    matches = soup.find_all("div", class_="css-jboygh e3vq2as0")
    not_allowed = [entry.find("img")["alt"].lower() for entry in matches]

    if role in not_allowed:
        print(f"Mobalytics doesn't have a build for {role}. \nHere's the default build instead.")
        role = ""
        soup = get_soup(champion, role)

    actual_role = soup.find("div", class_="css-p3pzap eo6ba8g5").text
    # create tree entries for default output
    root = Node(f"{champion} {actual_role} from Mobalytics")

    # get the runes
    runes = Node("Runes", parent=root)
    matches = soup.find_all("img", class_="css-1la33yl e16p94fx0")
    for entry in matches:
        Node(entry["alt"], parent=runes)

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
        if verbose:
            Node(conversion.get(shard_id), parent=shards)
        else:
            Node(conversion.get(shard_id), parent=runes)

    # get the build
    build = Node("Build", parent=root)

    # get time targets
    if verbose:
        time_targets = [entry.text for entry in soup.find_all("p", class_="css-1ofmdln ehobrmq7")]

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
                full = Node("Final Items", parent=build)
                for content in entry.contents[-3:]:  # only want the last 3
                    Node(re.findall(r"alt=\"(.*)\" c", str(content))[0], full)
            else:
                for content in entry.contents:
                    Node(re.findall(r"alt=\"(.*)\" c", str(content))[0], build)

    # Situational items
    if verbose:
        situational = Node("Situational Items", parent=build)
        for entry in soup.find_all("div", class_="css-143dzw8 es5thxd2"):
            Node(re.findall(r"alt=\"(.*)\" c", str(entry.contents[0]))[0], situational)

    summoners = Node("Summoner Spells", parent=root)
    matches = soup.find_all("img", class_="css-1xsdwvo edxc7l62")
    for entry in matches:
        spell = entry["src"].split(".png")[0].split("Summoner")[1]  # was blah/SummonerFoo.png
        # todo #5 come find the others and add them 
        if spell == "Dot":
            spell = "Ignite"
        if spell == "Haste":
            spell = "Ghost"
        Node(spell, parent=summoners)

    # Skill Learn Order
    if verbose:
        learn_order = Node("Skill Learn Order", parent=root)
        for entry in soup.find_all("div", class_="css-70qvj9 ek7zqkr0")[0].contents:
            if entry.name == "p":
                Node(entry.text, parent=learn_order)

    # Skill Max Order
    skills = Node("Skill Priority", parent=root)
    # this makes a list of the skill taken at each level
    sequence = [entry.text for entry in soup.find_all("div", class_="css-1dai7ia eaoplg14")]
    sequence.reverse()
    max_order = []
    for skill in sequence:
        if not skill in max_order:
            max_order.append(skill)
    max_order.reverse()
    max_order.remove("R")
    for skill in max_order:
        Node(skill, parent=skills)

    return root


def get_soup(champion: str, role: str) -> BeautifulSoup:
    """Returns a BeautifulSoup of Mobalytics HTML for the passed args."""
    url = f"https://app.mobalytics.gg/lol/champions/{champion}/build?role={role}"
    page = requests.get(url)
    return BeautifulSoup(page.content, "html.parser")
