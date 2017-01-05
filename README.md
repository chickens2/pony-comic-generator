This is a program for generating comics from chat text.

##Installation

1. Install Python 2.7

2. Install dependencies (listed in `requirements.txt`). 
You can do this by installing `pip` and navigating to this directory in the command line and doing the command:

    `pip install -r requirement.txt`

N.B. If typing `python` or `pip` in the command line gives an error even after installing and you're using windows, you might have to add them to the path. Look up 'how add to windows path'.




##Usage

1. Copy IRC text. Lines should be formatted like `<Username> Comments are here` or `* Username does a thing`
2.  Run `generateComic.py`

The comic should now be the new `comic.jpg` and should also be uploaded to Imgur.  The Imgur link replaces the text in your clipboard.