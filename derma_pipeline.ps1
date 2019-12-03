#!/usr/bin/env pwsh

# $args[0] = folder with SVS files
# $args[1] = folder with label (.roi, .xml) files

If( $args[0] -eq $null )
{
  $svs_dir = "./slices/"
}
Else
{
  $svs_dir = $args[0]
}

If( $args[1] -eq $null )
{
  $lbl_dir = "./labels/"
}
Else
{
  $lbl_dir = $args[1]
}

$files = Get-ChildItem -Path $svs_dir -Filter *.svs

Foreach ( $f in $files )
{
  $svs_name = (Get-Item $f).Basename

  # split the svs large-image into a patch series
  python ./SlideSeg/splitter.py --image $svs_dir/$f --ann $lbl_dir

  # refine the mask patches according to the selected colors
  python ./SlideSeg/refine_mask.py --mask_folder $svs_dir/$svs_name"_output/image_mask/" --fmt png

  # count the mask files related to melanoma and save them into a .csv
  python ./SlideSeg/counting_mask.py --mask_folder $svs_dir/$svs_name"_output/image_mask/" --outfile $svs_dir/$svs_name"_output/"$svs_name".csv" --fmt png

  # create the melanoma DB with svs_file, patch_file, pickle_image
  Write-Host python create_db.py
}

exit 0