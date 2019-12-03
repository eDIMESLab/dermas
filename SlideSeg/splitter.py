#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division

import os
import argparse
import SlideSeg

__author__ = 'Nico Curti'
__email__ = 'nico.curti2@unibo.it'


def parse_args ():

  description = 'Histological Slide Annotation Splitter'

  parser = argparse.ArgumentParser(description=description)

  booleans = { 'yes': True, 'true': True,   't': True,  'y': True,  '1': True,
               'no': False, 'false': False, 'f': False, 'n': False, '0': False
             }
  str2bool = lambda x : booleans[x]

  parser.add_argument('--image',    required=True,  type=str,      action='store',                help='.SVS image filename')
  parser.add_argument('--ann',      required=True,  type=str,      action='store',                help='Path to the annotation file')
  parser.add_argument('--fmt',      required=False, type=str,      action='store', default='png', help='Output format of the image_chips and image_masks')
  parser.add_argument('--quality',  required=False, type=int,      action='store', default=95,    help='Output quality: JPEG compression if output format is "jpg" (100 recommended, jpg compression artifacts will distort image segmentation)')
  parser.add_argument('--size',     required=False, type=int,      action='store', default=128,   help='Size of image_chips and image_masks')
  parser.add_argument('--overlap',  required=False, type=int,      action='store', default=1,     help='Pixel overlap between image chips')
  parser.add_argument('--save_all', required=False, type=str2bool, action='store', default=True,  help='True saves every image_chip, False only saves chips containing an annotated pixel')
  # parser.add_argument('--verbose',  required=False, type=str2bool, action='store', default=False, help='Suppress print output for chips/textfiles (1 = print, 0 = suppress output)')
  parser.add_argument('--tags',     required=False, type=str2bool, action='store', default=True,  help='Label images with key tags for sorting (1 = tags, 0 = no tags)')

  args = parser.parse_args()

  img_dir = os.path.dirname(args.image)
  name, _ = os.path.splitext(os.path.basename(args.image))

  out_dir  = os.path.join(img_dir, '_'.join([name, 'output']))
  key_file = os.path.join(out_dir, '_'.join([name, 'keys.txt']))

  save_ratio = 'inf' if args.save_all is False else '0'

  params = {
              'slide_path' : args.image,
              'xml_path'   : args.ann,
              'output_dir' : out_dir,
              'format'     : args.fmt,
              'quality'    : args.quality,
              'size'       : args.size,
              'overlap'    : args.overlap,
              'key'        : key_file,
              'save_all'   : args.save_all,
              'save_ratio' : save_ratio,
  #             'print'      : args.verbose,
              'tags'       : args.tags,
            }

  return params



def main ():
  '''
  Runs SlideSeg with the parameters specified in command line
  :return: image chips and masks
  '''

  params = parse_args()

  print('running SlideSeg with parameters:')
  print('  SVS filename         : {}'.format(params['slide_path']))
  print('  Annotation Directory : {}'.format(params['xml_path']))
  print('  Output Directory     : {}'.format(params['output_dir']))
  print('  Output image fmt     : {}'.format(params['format']))
  print('  Output image quality : {}'.format(params['quality']))
  print('  Output image size    : {}'.format(params['size']))
  print('  Output image overlap : {}'.format(params['overlap']))
  print('  Annotation Legend    : {}'.format(params['key']))
  print('  Save all files       : {}'.format(params['save_all']))

  filename = os.path.basename(params['slide_path'])
  os.makedirs(params['output_dir'], exist_ok=True)
  SlideSeg.run(params, filename)


if __name__ == '__main__':

  main()
