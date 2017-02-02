#!/bin/bash
find -E . -iregex ".*\.(jpg|gif|png|jpeg|bmp)" -type f -exec identify -format '%w %h %i\n' '{}' \; | awk '$1<500 && $2<500 {system("mv "substr($3,3)" LoRez/"substr($3,3)"")}'
