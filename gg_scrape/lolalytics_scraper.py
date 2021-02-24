import asyncio
from collections import OrderedDict

from anytree import Node

from bs4 import BeautifulSoup

from pyppeteer import launch

import requests
from requests.exceptions import ConnectionError

# from selenium import webdriver
# from selenium.common.exceptions import TimeoutException
# from selenium.webdriver.common.by import By
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait


def lolalytics_scraper(champion: str, role: str, matchup: str, verbose: bool) -> Node:
    """Parses through lolalytics.com and returns a full build according to given parameters"""
    if role.startswith("m"):
        role = "Middle"
    # Get the webpage HTML
    soup = asyncio.get_event_loop().run_until_complete(get_soup(champion, role, matchup))
    # Create tree
    if matchup != "":
        title = f"{champion.title()} {role.title()} vs {matchup.title()} from Lolalytics.com"
    else:
        title = f"{champion.title()} {role.title()} from Lolalytics.com"
    root = Node(title)
    # Workaround to get the summoner, item and rune names
    summs_dict: dict = {
        "1": "Cleanse",
        "3": "Exhaust",
        "4": "Flash",
        "6": "Ghost",
        "7": "Heal",
        "11": "Smite",
        "12": "Teleport",
        "9": "Clarity",
        "14": "Ignite",
        "21": "Barrier",
    }

    try:
        # todo find a way to fetch most recent patch in url
        item_dict: dict = requests.get("http://ddragon.leagueoflegends.com/cdn/11.4.1/data/en_US/item.json").json()
    except ConnectionError:
        print("Unable to talk to ddragon right now, please try again later.")
        return root

    try:
        runes_list: list = requests.get(
            "http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/perks.json"
        ).json()
    except ConnectionError:
        print("Unable to talk to ddragon right now, please try again later.")
        return root

    runes_dict: dict = {runes_list[runes_list.index(entry)]["id"]: entry for entry in runes_list}
    # Get all relevant elements from the page and make tree entries
    spells = soup.find_all("div", class_="Image_spell32br__Rns3F")
    # Replace tags with names
    spells = [summs_dict[spell.attrs["data-id"]] for spell in spells]
    tree_spells = Node("Summoner Spells", root)
    items = soup.find_all("div", class_="Image_item32br__aAG8C")
    # Replace item tags with names and remove duplicates
    items = list(OrderedDict.fromkeys([item_dict["data"][item.attrs["data-id"]]["name"] for item in items]))
    tree_items = Node("Items", root)
    skill_order = soup.find_all(attrs={"data-type": "skill"})[:3]
    tree_skill_order = Node("Skill Priority", root)
    runes = soup.find_all(lolalytics_runes)[:9]
    tree_runes = Node("Runes", root)
    # Add them into tree
    for item in items:
        Node(item, tree_items)
    for spell in spells:
        Node(spell, tree_spells)
    for skill in skill_order:
        Node(skill.attrs["alt"], tree_skill_order)
    for rune in runes:
        # There's a rune id with the f letter so to make sure this doesn't raise a KeyError I have to strip the letter
        Node(runes_dict[int(rune.attrs["data-id"].strip("f"))]["name"], tree_runes)
    return root


async def get_soup(champion: str, role: str, matchup: str) -> BeautifulSoup:
    """Returns a BeautifulSoup of Lolalytics.com HTML for the passed args."""
    if matchup != "":
        url = f"https://lolalytics.com/lol/{champion.lower()}/vs/{matchup.lower()}/build/?lane={role.lower()}"
    else:
        url = f"https://lolalytics.com/lol/{champion.lower()}/build/?lane={role.lower()}"
    # pyppeteer is the superior solution, but if you dont want to use it uncomment this and comment the uncommented part
    # driver = webdriver.Firefox(options=Options())
    # driver.maximize_window()
    # driver.get(url)
    # # Wait for the javascript to load
    # timeout = 3
    # try:
    #     element_present = EC.presence_of_element_located((By.ID, 'main'))
    #     WebDriverWait(driver, timeout).until(element_present)
    # except TimeoutException:
    #     pass
    # page = driver.execute_script("return document.body.innerHTML;")
    browser = await launch()
    page = await browser.newPage()
    await page.goto(url)
    # Wait for page to load
    await page.waitForSelector(
        "#root > div > div.Wrapper_content__1wGv- > div.Wrapper_wrapper__3izJT > div.Summary_quick__3le_e > div.Summary_row1__3rZk8 > div:nth-child(1)"
    )
    content = await page.content()
    await page.close()
    await browser.close()
    return BeautifulSoup(content, "html.parser")


def lolalytics_runes(tag):
    """Function to get all tags with active runes from lolalytics.com"""
    if "data-type" in tag.attrs:
        if "rune" in tag.attrs["data-type"]:
            return "class" in tag.attrs
