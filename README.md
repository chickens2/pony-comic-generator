This is a program for generating comics from chat text, inspired by Microsoft Comic Chat and [Jerkcity](https://www.jerkcity.com).

##Installation

1. Install Python 2.7
2. Install dependencies (listed in `requirements.txt`). 
  * You can do this by installing `pip` and navigating to this directory in the command line and doing the command: `pip3 install -r requirement.txt`

N.B. If typing `python` or `pip` in the command line gives an error even after installing and you're using Windows, you might have to add them to the path. Look up 'how add to windows path'.


##Usage

1. Copy IRC text. Lines should be formatted like `<Username> Comments are here` or `* Username does a thing`
2. Run `generateComic.py`

The comic should now be the new `comic.jpg` and should also be uploaded to Imgur.  The Imgur link replaces the text in your clipboard.

When run from the command line you can specify a file containing IRC text instead with `-f`, specify the title with `-t`, and specify the background image file to use with `-b`.


## Technical Notes

* Images in the backgrounds folder really don't need to be any larger than 500px in any dimension.  Install `ImageMagick` and use `convert <imagename> -resize "500^>" <newname>` to scale the images down a bit.  Further optimisation may be used with the `jpegoptim` and `optipng` commands.
* Symlinks *do* work in the backgrounds folder.  Please don't send in a PR containing symlinks.
* Options for `shuffle_mode`:
	* `0`: pony is procedurally-chosen from the username, except for the ones defined in the config file
	* `1`: users without a defined pony will have their pony procedurally-chosen based a seed other than their username
	* `2`: all users receive a procedurally-chosen pony
* `closeup_zoom` affects both the characters and the background
* In the Backgrounds section of the config file, you may use subfolders, such as `Custom/Test12`.  Put all the backgrounds that you like into the custom folder if you don't want them to be committed back to the repository.
* If you are having problems with "Not a real JPEG" on symlinked files, make sure they are real soft links and not Mac aliases.  [This automator workflow](http://blog.poynton.ca/?p=281) lets you select all your aliased files in Finder and then batch-convert them in a right-click menu.
* `generateComic.py` is the driver for the comic generation, the actual heavy lifting is done in `makeComic.py`
* If you use emoji in your output, please use [Symbolia](http://users.teilar.gr/%7Eg1951d/) for the best results

## [Future Plans](./roadmap.md)

See [`roadmap.md`](./roadmap.md)
