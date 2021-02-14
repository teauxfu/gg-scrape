# gg-scrape

I made a little Python script that provides a League champion runes/build from mobalytics.gg and the recommended skill order from champion.gg
The goal was to not have to open a browser tab to check a build.
The interface emulates optional command line arguments, so you can specify a role with a flag
- -m or -mid
- -a or -adc  OR  -b or -bot
- -t or -top
- -j or -jg
- -s or -sup

![screenshot of the app in use](/Capture.PNG)


Depends on the anytree, beautifulsoup4, and requests Python libraries.
The HTML is requested and parsed sequentially, so it's rather slow.I may or may not make it async later.
