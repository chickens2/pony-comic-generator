#!/bin/bash
find -E . -iregex ".*\.(jpg|gif|png|jpeg)" -print0 | xargs -0 mogrify -resize "500^>"
