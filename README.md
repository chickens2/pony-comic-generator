This is a program for generating comics from chat text, inspired by Microsoft Comic Chat and [Jerkcity](https://www.jerkcity.com).

##Installation

1. Install Python 2.7
2. Install dependencies (listed in `requirements.txt`). 
  * You can do this by installing `pip` and navigating to this directory in the command line and doing the command: `pip install -r requirement.txt`

N.B. If typing `python` or `pip` in the command line gives an error even after installing and you're using Windows, you might have to add them to the path. Look up 'how add to windows path'.




##Usage

1. Copy IRC text. Lines should be formatted like `<Username> Comments are here` or `* Username does a thing`
2.  Run `generateComic.py`

The comic should now be the new `comic.jpg` and should also be uploaded to Imgur.  The Imgur link replaces the text in your clipboard.

When run from the command line you can specify a file containing irc text instead with -f, specify the title with -t, and specify the background image file to use with -b.

## Technical Notes

* Images in the backgrounds folder really don't need to be any larger than 500px in any dimension.  Install `ImageMagick` and use `convert <imagename> -resize "500^>" <newname>` to scale the images down a bit.  Further optimisation may be used with the `jpegoptim` and `optipng` commands.
* The program currently completely chokes up if there are any non-image entities in the backgrounds folder.  This means:
	1. Mac users need to make sure there aren't any `.DS_Store` or `.trashes` files there.  Use `rm backgrounds/.DS_Store` if you receive complaints about that file.
	2. You can't put subfolders in the backgrounds directory or else the program poops its pants. 💩
* Symlinks *do* work in the backgrounds folder.  Please don't send in a PR containing symlinks.