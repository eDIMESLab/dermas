#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division

# Import necessary packages
import os
import cv2
import tqdm
import numpy as np
from openslide import OpenSlide
import xml.etree.ElementTree as ET
from collections import defaultdict


__author__ = 'Nico Curti'
__email__ = 'nico.curti2@unibo.it'


def load_parameters (parameters):
  '''
  Loads parameters from text file

  Parameters
  ----------
    parameters : dict
      The name of the parameters file

  Returns
  -------
    params : dict
      Parameters for slideseg
  '''
  params = {}

  with open(parameters, "r") as fp:
    for line in fp:
      option, _, value = line.partition(':')
      value = value.partition('#')[0].strip()
      params[option] = value

  return params


def makemask (annotation_key, size, xml_path):
  '''
  Reads xml file and makes annotation mask for entire slide image

  Parameters
  ----------
    annotation_key : str
      Name of the annotation key file

    size : tuple
      Size of the whole slide image

    xml_path : str
      Path to the xml file

  Returns
  -------
    (mat, annotations) : tuple
      numpy array with mask annotation and dictionary of annotation keys and color codes
  '''

  # Import xml file and get root
  tree = ET.parse(xml_path)
  root = tree.getroot()

  # Generate annotation array and key dictionary
  mat = np.zeros(shape=(*size[::-1], 3), dtype='uint8')
  annotations = dict()
  # contours = []

  # Find data in xml file
  if not os.path.isfile(annotation_key):
    print('Could not find {0}, generating new file...'.format(annotation_key))
    generatekey('{0}'.format(annotation_key), os.path.split(xml_path)[0])
    print('{0} generated.'.format(annotation_key))

  color_codes = loadkeys(annotation_key)

  for reg in root.iter('contour'):
    key = reg.get('name').upper()
    if key in color_codes:
      color_code = color_codes[key]
    else:
      addkeys(annotation_key, key)
      color_codes = loadkeys(annotation_key)
      color_code  = color_codes[key]

    points = []
    for child in reg.iter('contour'):
      for vert in child.iter('point'):
        x, y = tuple(map(round, eval(vert.text)))
        points.append((x, y))

    cnt = np.array(points).reshape((-1, 1, 2)).astype(np.int32)
    cv2.fillPoly(mat, [cnt], color_code)
    # contours.append(cnt)

    # annotations and colors
    if key not in annotations:
      annotations['{0}'.format(key)] = color_code
  print('annotations loaded successfully')
  # print(len(mat[mat!=0]))
  return (mat, annotations)


def writekeys (filename, annotations):
  '''
  Writes each annotation key to the output text file

  Parameters
  ----------
    filename : str
      Filename of image chip

    annotations : dict
      Dictionary of annotation keys

  Returns
  -------
  None

  Notes
  ----
  This function just updates text file (filename)
  '''

  dest = 'output/textfiles/'
  path = os.path.dirname(dest)
  os.makedirs(path, exist_ok=True)

  name = '{0}_{1}'.format(os.path.splitext(filename)[0], 'Details.txt')

  with open(os.path.join(dest, name), 'w+') as fp:

    for key, value in annotations.items():
      keyline = 'Key: {0}'.format(key)
      fp.write(keyline)
      fp.write(('Mask_Color: {0}\n'.format(value).rjust(50 - len(keyline))))


def writeimagelist (filename, image_dictionary):
  '''
  Writes list of images containing each annotation key

  Parameters
  ----------
    filename : str
      The name of the slide image

    image_dictionary : dict
      Dictionary of images with each key

  Returns
  -------
  None

  Notes
  -----
    Update the Details text file given by {$filename*_Details.txt}
  '''
  dest = 'output/textfiles/'
  name = '{0}_{1}'.format(os.path.splitext(filename)[0], 'Details.txt')

  with open(os.path.join(dest, name), 'a') as fp:

    for key, value in image_dictionary.items():
      keyline = '\nKey: {0}\n'.format(key)
      fp.write(keyline)
      for name in value:
        fp.write('   {0}\n'.format(name))


def loadkeys (annotation_key):
  '''
  Opens annotation_key file and loads keys and color codes

  Parameters
  ----------
    annotation_key : dict
      The filename of the annotation key

  Returns
  -------
    color_codes : dict
      Color codes for each region (region_key : color)
  '''

  color_codes = dict()

  with open(annotation_key, 'r') as fp:
    # Load keys and color codes from Annotation_Key.txt
    for line in fp:
      line = line.split('  ') # double space for split
      region_key, *_, color = line
      region_key = region_key.split(':')[1].strip()
      color = color.split(':')[1].strip()
      assert color != '' and region_key != ''
      color_codes[region_key] = eval(color)

  return color_codes


def addkeys (annotation_key, key):
  '''
  Adds new key and color_code to annotation key

  Parameters
  ----------
    annotation_key : dict
      The filename of the annotation key

    key : str
      The annotation to be added

  Returns
  -------
  None

  Notes
  -----
    Updated annotation key file
  '''

  color_codes = loadkeys(annotation_key)
  min_color = min(color_codes.items(), key = lambda x: x[1])[1]
  new_color = int(min_color[0]) - 1
  color_codes[key.upper()].append(new_color)
  writeannotations(annotation_key, color_codes)


def writeannotations (annotation_key, annotations):
  '''
  Writes annotation keys and color codes to annotation key text file

  Parameters
  ----------
    annotation_key : str
      Filename of annotation key

    annotations : dict
      Dictionary of annotation keys and color codes

  Returns
  -------
  None

  Notes
  -----
  Append to .txt file with annotation keys
  '''
  with open(annotation_key, 'w+') as fp:

    for key, value in sorted(annotations.items()):
      keyline = 'Key: {0}'.format(key)
      rgb_color = value.lstrip('#')
      rgb_color = tuple(int(rgb_color[i : i + 2], 16) for i in (0, 2, 4))
      fp.write(keyline)
      fp.write(('Mask_Color: {0}\n'.format(rgb_color).rjust(65 - len(keyline))))


def generatekey (annotation_key, path):
  '''
  Generates annotation_key from folder of xml files

  Parameters
  ----------
    annotation_key : str
      The name of the annotation key file

    path : str
      Directory containing xml (roi) files

  Returns
  -------
  None

  Notes
  -----
  Write the annotation_key file
  '''

  annotations = dict()
  for filename in os.listdir(path):
    # Import xml file and get root
    tree = ET.parse(os.path.join(path, filename))
    root = tree.getroot()

    # Find data in xml file
    for reg in root.iter('contour'):
      key = reg.get('name').upper()
      annotations['{0}'.format(key)] = reg.get('color')
      # if key in annotations:
      #   continue
      # else:
      #   color -= 1
      #   color_code = color
      #
      # if key not in annotations:
      #   annotations['{0}'.format(key)].append(color_code)

  # print annotations to text file
  writeannotations(annotation_key, annotations)


def attachtags (path, keys):
  '''
  Attaches image tags to metadata of chips and masks

  Parameters
  ----------
    path: str
      File to attach tags to.

    keys : str
      keys to attach as tags

  Returns
  -------
  None

  Notes
  -----
  JPG with metadata tags
  '''

  if os.path.splitext(path)[1] == '.png':
    pass
  else:
    import pexif

    metadata = pexif.JpegFile.fromFile(path)
    str = ' '.join(keys)
    metadata.exif.primary.ImageDescription = str

    with open(path, 'wb') as out:
      metadata.writeFd(out)


def savechip (chip, path, quality, keys):
  '''
  Saves the image chip

  Parameters
  ----------
    chip : array_like
      The slide image chip to save

    path : str
      The full path to the chip

    quality : str
      The output quality

    keys : str
      Keys associated with the chip

  Returns
  -------
  None

  Notes
  -----
  Save the image chip
  '''

  # Ensure directories
  directory, filename = os.path.split(path)
  os.makedirs(directory, exist_ok=True)
  format, suffix = formatcheck(os.path.splitext(filename)[1].strip('.'))

  if suffix == 'jpg':
    # Save image chip
    chip.save(path, quality=quality)

    # Attach image tags
    attachtags(path, keys)

  else:
    # Save image chip
    chip.save(path)

    # Attach image tags
    attachtags(path, keys)


def savemask (mask, path, keys):
  '''
  Saves the image masks

  Parameters
  ----------
    mask : array_like
      The image mask to save

    path : str
      The complete path for the mask

    keys : str
      keys associated with the chip

  Returns
  -------
  None
  '''

  # Ensure directories
  directory, filename = os.path.split(path)
  os.makedirs(directory, exist_ok=True)
  format, suffix = formatcheck(os.path.splitext(filename)[1].strip('.'))

  if suffix == 'jpg':
    # Save the image mask
    cv2.imwrite(path, mask, [cv2.IMWRITE_JPEG_QUALITY, 100])

    # Attach image tags
    attachtags(path, keys)

  else:
    # Save the image mask
    cv2.imwrite(path, mask)

    # Attach image tags
    attachtags(path, keys)


def checksave (save_all, pix_list, save_ratio, save_count_annotated, save_count_blank):
  '''
  Checks whether or not an image chip should be saved

  Parameters
  ----------
    save_all : bool
      saves all chips if true

    pix_list : list
      list of pixel values in image mask

    save_ratio : float
      Ratio of annotated chips to unannotated chips

    save_count_annotated : int
      Total annotated chips saved

    save_count_blank : int
      Total blank chips saved

  Returns
  -------
    save : bool
      True if the current image has to be saved
  '''

  if save_all and len(list(filter(lambda x: x > 0, pix_list))) > 0:
    save = True
  elif save_count_annotated / save_count_blank > save_ratio:
    save = True
  elif len(list(filter(lambda x: x > 0, pix_list))) > 0:
    save = True
  else:
    save = False

  return save


def formatcheck (format):
  '''
  Assures correct format parameter was defined correctly

  Parameters
  ----------
    format: str
      The output format parameter

  Returns
  -------
    format : str
      image fmt

    suffix : str
      image suffix (e.g 'jpg')
  '''
  if format.lower() == 'jpg':
    suffix = format
    format = 'JPEG'

  elif format.lower() == 'jpeg':
    format = format.upper()
    suffix = 'jpg'

  else:
    format = format.upper()
    suffix = format.lower()

  return (format, suffix)


def openwholeslide (path):
  '''
  Opens a whole slide image

  Parameters
  ----------
    path : str
      Slide image path.

  Returns
  -------
    osr : OpenSlide
      openslide obj
  '''

  directory, filename = os.path.split(path)
  print('loading {0} ...'.format(filename), end='')

  # Open Slide Image
  osr = OpenSlide(path)

  print('[done]')
  return osr


def curatemask (mask, scale_width, scale_height, chip_size):
  '''
  Resize and pad annotation mask if necessary

  Parameters
  ----------
    mask : array_like
      An image mask

    scale_width : int
      Scaling for higher magnification levels

    scale_height : int
      Scaling for higher magnification levels

  Returns
  -------
    mask : array_like
      The resized mask (annotated) matrix
  '''
  # Resize and pad annotation mask if necessary
  mask = cv2.resize(mask, dsize=None, fx=1. / scale_width, fy=1. / scale_height,
                    interpolation=cv2.INTER_CUBIC)

  mask_width, mask_height, mask_color = mask.shape
  if mask_height < chip_size or mask_width < chip_size:
    mask = np.pad(mask, ((0, chip_size - mask_width),
                         (0, chip_size - mask_height),
                         (0, 0)), 'constant')

  if mask_height > chip_size or mask_width > chip_size:
    mask = mask[:chip_size, :chip_size, ...]

  return mask


def getchips (levels, dims, chip_size, overlap, mask, annotations, filename, suffix, save_all, save_ratio):
  '''
  Finds chip locations that should be loaded and saved

  Parameters
  ----------
    levels : int
      Levels in whole slide image

    dims : tuple
      Dimension of whole slide image

    chip_size : int
      The size of the image chips

    overlap : int
      Overlap between image chips (stride)

    mask : array_like
      Annotation mask for slide image

    annotations : dict
      Dictionary of annotations in image

    filename : str
      Slide image filename

    suffix : str
      Output format for saving.

    save_all : bool
      Whether or not to save every image chip

    save_ratio : float
      Ratio of annotated to unannotated chips

  Returns
  -------
    chip_dict : dict
      Dictionary of chip names, level, col, row, and scale

    image_dict : dict
      Dictionary of annotations and chips with those annotations
  '''

  # Image dictionary of keys and save variables
  image_dict = defaultdict(list)
  chip_dict = defaultdict(list)
  save_count_blank = 1.
  save_count_annotated = 1.

  for i in range(levels):
    width, height = dims[i]
    scale_factor_width = dims[0][0] / width
    scale_factor_height = dims[0][1] / height
    print('Scanning slide level {0} of {1}'.format(i + 1, levels))

    # Generate the image chip coordinates and save information
    for col in tqdm.tqdm(range(0, width, chip_size - overlap)):
      for row in range(0, height, chip_size - overlap):
        img_mask = mask[int(row * scale_factor_height) : int((row + chip_size) * scale_factor_height),
                        int(col * scale_factor_width)  : int((col + chip_size) * scale_factor_width)]
        pix_list = np.unique(img_mask)

        # Check whether or not to save the region
        if save_all and len(list(filter(lambda x: x != 0, pix_list))) > 0:
          save = True
        else:
          save = False
        #save = checksave(save_all, pix_list, save_ratio, save_count_annotated, save_count_blank)

        # Save image and assign keys.
        if save is True:
          chip_name = '{0}_{1}_{2}_{3}.{4}'.format(filename.rstrip('.svs'), i, row, col, suffix)
          keys = []

          # Make sure annotation key contains value
          for key, value in annotations.items():
            for pixel in pix_list:
              if int(pixel) == int(value[0]):
                keys.append(key)
                image_dict[key].append(chip_name)

          if len(keys) == 0:
            save_count_blank += 1.
            keys.append('NONE')
          else:
            save_count_annotated += 1.

          chip_dict[chip_name] = [keys]
          chip_dict[chip_name].append(i)
          chip_dict[chip_name].append(col)
          chip_dict[chip_name].append(row)
          chip_dict[chip_name].append(scale_factor_width)
          chip_dict[chip_name].append(scale_factor_height)

  return chip_dict, image_dict


def run (parameters, filename):
  '''
  Runs SlideSeg: Generates image chips from a whole slide image.

  Parameters
  ----------
    parameters : dict
      Processing parameters

    filename : str
      Filename of whole slide image

  Returns
  -------
  None

  Notes
  -----
  Create and save image chips and masks
  '''

  # Open slide
  osr = openwholeslide(parameters['slide_path'])
  size = osr.level_dimensions[0] # max size

  # Annotation Mask
  xml_file = filename.replace('svs', 'roi') # .roi become .xml in the new version of Seeden Viewer

  print('loading annotation data from {0}{1}'.format(parameters['xml_path'], xml_file))
  mask, annotations = makemask(parameters['key'], size, os.path.join(parameters['xml_path'], xml_file))

  # Define output directory
  output_directory_chip = '{0}/image_chips/'.format(parameters['output_dir'])
  output_directory_mask = '{0}/image_mask/'.format(parameters['output_dir'])

  # Output formatting check
  format, suffix = formatcheck(parameters['format'])

  # Find chip data/locations to be saved
  chip_dictionary, image_dict = getchips(osr.level_count, osr.level_dimensions, int(parameters['size']), int(parameters['overlap']),
                                         mask, annotations, filename, suffix, parameters['save_all'], float(parameters['save_ratio']))

  # Save chips and masks
  print('Saving chips... {0} total chips'.format(len(chip_dictionary)))

  for filename, (keys, i, col, row, scale_factor_width, scale_factor_height) in tqdm.tqdm(chip_dictionary.items()):

    # load chip region from slide image
    img = osr.read_region([int(col * scale_factor_width), int(row * scale_factor_height)], i,
                          [int(parameters['size']), int(parameters['size'])]).convert('RGB')

    # load image mask and curate
    img_mask = mask[int(row * scale_factor_height) : int((row + int(parameters['size'])) * scale_factor_height),
                    int(col * scale_factor_width)  : int((col + int(parameters['size'])) * scale_factor_width)]

    img_mask = curatemask(img_mask, scale_factor_width, scale_factor_height, int(parameters['size']))

    # save the image chip and image mask
    path_chip = output_directory_chip + filename
    path_mask = output_directory_mask + filename

    savechip(img, path_chip, int(parameters['quality']), keys)
    savemask(img_mask, path_mask, keys)

  # Make text output of Annotation Data
  print('Updating txt file details...')

  writekeys(xml_file, annotations)
  writeimagelist(xml_file, image_dict)

  print('txt file details updated')
