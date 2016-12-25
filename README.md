This is a program for generating comics from chat text.

INSTALLATION:

1. install Python 2.7

2. install dependencies (listed in requirements.txt). 
You can do this by installing pip and navigating to this directory in the command line and doing the command:

pip install -r requirement.txt

if typing python or pip in the command line gives an error even after installing and you're using windows, you might have to add them to the path. Look up 'how add to windows path'.




USAGE:

1. Copy irc text. Lines should be formatted like 

<Username> Comments are here

or

* Username does a thing

(github messes these up view in text editor to see)

2.  Run generateComic.py

The comic should now be the new 'comic.jpg' and also it should be uploaded to imgur, the link replaces the text in your clipboard.