#!/bin/bash

# $1 = folder with SVS files
# $2 = folder with label (.roi, .xml) files

svs_dir=$1
lbl_dir=$2

if [ "$1" == "" ]; then
  svs_dir="./slices/"
else
  svs_dir=$1
fi

if [ "$2" == "" ]; then
  lbl_dir="./labels/"
else
  lbl_dir=$2
fi

files=$(ls $svs_dir\*.svs)

for f in $files; do

  svs_name=$(echo $(basename $f) | cut -d'.' -f 1)

  # split the svs large-image into a patch series
  python ./SlideSeg/splitter.py --image $svs_dir/$f --ann $lbl_dir

  # refine the mask patches according to the selected colors
  python ./SlideSeg/refine_mask.py --mask_folder $svs_dir/$(svs_name)_output/image_mask/ --fmt png

  # count the mask files related to melanoma and save them into a .csv
  python ./SlideSeg/counting_mask.py --mask_folder $svs_dir/$(svs_name)_output/image_mask/ --outfile $svs_dir/$(svs_name)_output/$(svs_name).csv --fmt png

  # create the melanoma DB with svs_file, patch_file, pickle_image
  echo python create_db.py

done;
