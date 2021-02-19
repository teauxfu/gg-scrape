# gg-scrape
A little Python CLI app that provides a League of Legends champion build by scraping the web.

The goal was to not have to open a browser tab (or be advertised to) to quickly check a build before a match.
The HTML is requested and parsed sequentially, so it's somewhat slow (but still faster than opening a browser).

## Installation
```
python -m pip install gg-scrape
```

## Usage
```
ggs CHAMPION [ROLE]
```

![screenshot of the app in use](img/Capture.PNG)

## Requirements
Depends on the anytree, beautifulsoup4, typer, and requests Python libraries.

## Contributions
Thanks to @Mycsina for feedback and helping to improve and expand this package's functionality!

Pull requests are welcome. 