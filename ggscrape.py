from anytree import Node, RenderTree
from bs4 import BeautifulSoup
import click
from click import core
import requests
import time
import re


@click.command()
@click.argument("champion")
@click.option("-r", "--role", default="", help="The role you're playing")
@click.option("-m", "--matchup", default="", help="Who you're playing against")
@click.option("-s", "--source", default="", help="Which site to scrape")
def clickparser(champion, role, matchup, source):
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
    else:
        root = None
        # print the thing
    for pre, _, node in RenderTree(root):
        print(f"{pre}{node.name}")
    print(f"\nFinished in {round(time.time() - start, 3)} s")
    input()


def mobalytics_scraper(champion, role):
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
        "5008": "Adaptive Force"
    }
    shards = Node("Shards", parent=root)
    for entry in matches:
        shard_id = entry["src"].split(".png")[0][-4:]  # was blah/####.png
        shard = conversion.get(shard_id)
        Node(shard, parent=shards)
    build = Node("Build", parent=root)
    skill = Node("Skill Priority", parent=root)
    starter = Node("Starter Items", parent=build)
    early = Node("Early Items", parent=build)
    core = Node("Core Items", parent=build)
    full = Node("Full Build", parent=build)
    situational = Node("Situational Items", parent=build)
    for cycle, entry in enumerate(soup.find_all("div", class_="ednsys62 css-1taoj5l ehobrmq2")):
        if cycle == 0:
            for content in entry.contents:
                Node(re.findall(r"alt=\"(.*)\" c", str(content))[0], starter)
        if cycle == 1:
            for content in entry.contents:
                Node(re.findall(r"alt=\"(.*)\" c", str(content))[0], early)
        if cycle == 2:
            for content in entry.contents:
                Node(re.findall(r"alt=\"(.*)\" c", str(content))[0], core)
        if cycle == 3:
            for content in entry.contents:
                Node(re.findall(r"alt=\"(.*)\" c", str(content))[0], full)
    for entry in soup.find_all("div", class_="css-143dzw8 es5thxd2"):
        Node(re.findall(r"alt=\"(.*)\" c", str(entry.contents[0]))[0], situational)
    for entry in soup.find_all("div", class_="css-70qvj9 ek7zqkr0")[0].contents:
        if entry.name == "p":
            Node(entry.text, skill)
    return root


def champion_gg_scraper(champion, role, matchup):
    # from champion.gg instead ...
    if role.startswith("m"):
        role = "Middle"
    if matchup != "":
        url = f"https://champion.gg/champion/{champion}/{role}/overview/{matchup}"
    else:
        url = f"https://champion.gg/champion/{champion}/{role}/"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    skills = Node("Skill Priority", parent=root)
    bowl = soup.find_all("p", class_="typography__Caption-sc-1mpsx83-11 typography__CaptionBold-sc-1mpsx83-12 dwtPBh")[1:4]  # the first is 'Passive' and the rest are redundant

    for spoonful in bowl:
        s = spoonful.text
        Node(s, parent=skills)




clickparser()
