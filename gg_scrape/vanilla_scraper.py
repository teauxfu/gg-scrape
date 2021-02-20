import time

from anytree import Node, RenderTree
from bs4 import BeautifulSoup
import requests

def vanilla_scraper(champion: str, role:str, matchup:str, verbose: bool, *args):
    start = time.time() # for funsies
    url = f"https://app.mobalytics.gg/lol/champions/{champion}/build?role={role}"
    # make soup from the URL 
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser') 
    c = soup.find('p', class_='css-1yvcufn eo6ba8g4').text # string with champ name
    r = soup.find('div', class_='css-p3pzap eo6ba8g5').text # string with role and patch # 

    # make a tree to organize / render later
    root = Node(f"{c} {r}")

    # get the runes
    runes = Node("Runes", parent=root)
    results = soup.find_all('img', class_='css-1la33yl e16p94fx0')
    for entry in results:
        r = entry['alt']
        Node(r, parent=runes)

    # get the shards
    results = soup.find_all('img', class_='css-1vgqbrs ed9gm2s1')
    conversion = {
        '5001': 'Health',
        '5002': 'Armor',
        '5003': 'Magic resist',
        '5005': 'Attack speed',
        '5007': 'Ability haste',
        '5008': 'Adaptive force',
    }
    for entry in results:
        i = entry['src'].split('.png')[0][-4:] # was blah/####.png
        s = conversion.get(i)
        Node(s, parent=runes)

    # get the build 
    build = Node("Build", parent=root)
    results = soup.find_all('img', class_='ehobrmq6 css-1wpgt6j e14wqe2d0')[-6:] # only want final 6 items
    for entry in results:
        i = entry['alt']
        Node(i, parent=build)
    
    # from champion.gg instead ...
    if role.startswith('m'): role = 'Middle'
    
    url = f"https://champion.gg/champion/{champion}/{role}"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    skills = Node("Skill Priority", parent=root)
    results = soup.find_all('p', class_='typography__Caption-sc-1mpsx83-11 typography__CaptionBold-sc-1mpsx83-12 dwtPBh')[1:4] # the first is 'Passive' and the rest are redundant
    for entry in results:
        s = entry.text
        Node(s, parent=skills)

    # print the thing
    for pre, _, node in RenderTree(root):
        print(f"{pre}{node.name}")

    print(f"\nFinished in {round(time.time() - start, 3)} s     ✨ glhf ✨")
    input()