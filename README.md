# gg-scrape
A little Python CLI app that provides a League champion runes/build from mobalytics.gg and the recommended skill order from champion.gg

The goal was to not have to open a browser tab to check a build.
The HTML is requested and parsed sequentially, so it's rather slow.

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