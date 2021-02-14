from anytree import Node, RenderTree
from bs4 import BeautifulSoup
import requests
import time
    
if __name__ == '__main__':
    print()
    q = input("champion -role >> ")

    start = time.time() # for funsies
    q = q.split(' -')
    champion = q[0]
    role = q[-1]

    if role == 'm' or role == "mid" : role = "MID"
    elif role == 'a' or role == 'b' or role == "bot" or role =="adc": role = "ADC"
    elif role == 's' or role == "sup": role = "SUPPORT"
    elif role == 't' or role == "top": role = "TOP"  
    elif role == 'j' or role == "jg": role = "JUNGLE"
    else: role = ""
    
    url = f"https://app.mobalytics.gg/lol/champions/{champion}/build?role={role}"
    # make soup from the URL 
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser') 
    c = soup.find('p', class_='css-1yvcufn eo6ba8g4').text
    r = soup.find('div', class_='css-p3pzap eo6ba8g5').text

    # make a tree to organize / render later
    root = Node(f"{c} {r}")

    # get the runes
    runes = Node("Runes", parent=root)
    bowl = soup.find_all('img', class_='css-1la33yl e16p94fx0')
    for spoonful in bowl:
        r = spoonful['alt']
        rune = Node(r, parent=runes)

    # get the shards
    bowl = soup.find_all('img', class_='css-1vgqbrs ed9gm2s1')
    conversion = {
        '5001': 'Health',
        '5002': 'Armor',
        '5003': 'Magic resist',
        '5005': 'Attack speed',
        '5007': 'Ability haste',
        '5008': 'Adaptive force',
    }
    for spoonful in bowl:
        i = spoonful['src'].split('.png')[0][-4:] # was blah/####.png
        s = conversion.get(i)
        shard = Node(s, parent=runes)

    # get the build 
    build = Node("Build", parent=root)
    bowl = soup.find_all('img', class_='ehobrmq6 css-1wpgt6j e14wqe2d0')[-6:] # only want final 6 items
    for spoonful in bowl:
        i = spoonful['alt']
        item = Node(i, parent=build)
    
    # from champion.gg instead ...
    if role == 'MID': role = 'Middle'
    url = f"https://champion.gg/champion/{champion}/{role}"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    skills = Node("Skill Priority", parent=root)
    bowl = soup.find_all('p', class_='typography__Caption-sc-1mpsx83-11 typography__CaptionBold-sc-1mpsx83-12 dwtPBh')[1:4] # the first is 'Passive' and the rest are redundant
    
    for spoonful in bowl:
        s = spoonful.text
        skill = Node(s, parent=skills)

    # print the thing
    print()
    for pre, _, node in RenderTree(root):
        print(f"{pre}{node.name}")
    print()
    print(f"Finished in {round(time.time() - start, 3)} s")
    input()
