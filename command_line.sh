#!/bin/bash
# command line examples of datamoshing

# ------------------------------------------------------------------------------
# utilities for file conversion
# https://www.ffmpeg.org/

# convert mpg to avi
ffmpeg -i file.mpg -c:v copy -c:a copy file.avi

# batch convert mpg to avi
while IFS= read -d $'\0' -r file ; do
  ffmpeg -i "$file" -c:v copy -c:a copy ${file%%.mpg}.avi
done < <(find . -iname '*.mpg' -print0)

# avidemux likes mkv files
ffmpeg -i file.mpg file.mkv

# ------------------------------------------------------------------------------
# utilities for automatically generating file names below

dir="$HOME/projects/videos"

# outputs unix timestamp
timestamp () {
  date +"%s"
}

# adds "output" and a timestamp to an input filename
output () {
  echo "${input%.*}_output_$(timestamp).${input##*.}"
}

# ------------------------------------------------------------------------------
# byebyte
# https://github.com/wayspurrchen/byebyte

input="$dir/stills30secs/stills30secs.mpg"

min=0.1
max=1
times=2500
continuous=true
continous_chance=0.5
chunk_min=5
chunk_max=20

byebyte destroy -i $input -o $(output) --min $min --max $max

byebyte destroy -i $input -o $(output) --min $min --max $max -t $times

byebyte destroy -i $input -o $(output) --min $min --max $max -t $times \
                -c $continuous

byebyte destroy -i $input -o $(output) --min $min --max $max -t $times \
                -c $continuous -C $continous_chance

byebyte shuffle -i $input -o $(output) --min $min --max $max \
                --chunk-min $chunk_min --chunk-max $chunk_max

# ------------------------------------------------------------------------------
# AviGlitch
# https://github.com/fand/node-aviglitch

# input="$dir/motorcycle/motorcycle.avi"
input="$dir/PXL/PXL.avi"

datamosh $input -o $(output)

# ------------------------------------------------------------------------------
# automosh.py
# adapted from https://github.com/thisisparker/automosh
#
# I recommend running this in a virtual environment using pipenv
# https://pipenv.readthedocs.io/en/latest/

input="$dir/motorcycle/motorcycle.mpg"
replace="$dir/stills30secs/stills30secs.mpg"

pipenv shell
python -m automosh $input $(output)
python -m automosh $input $(output) -r $replace


# ------------------------------------------------------------------------------
# do_the_mosh.py
# adapted from https://github.com/happyhorseskull/you-can-datamosh-on-linux
#
# I recommend running this in a virtual environment using pipenv
# https://pipenv.readthedocs.io/en/latest/

input="$dir/motorcycle/motorcycle.mpg"

pipenv shell
python -m do_the_mosh $input
