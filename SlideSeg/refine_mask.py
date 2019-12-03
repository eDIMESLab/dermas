#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division

import os
import cv2
import tqdm
import argparse
import numpy as np
from glob import glob

__author__ = 'Nico Curti'
__email__ = 'nico.curti2@unibo.it'

COLORS = [(  0,   0,   0),
          (  0,   0, 255),
          (  0, 255,   0),
          (255,   0,   0)
         ]


def parse_args ():

  description = 'Histological masks refinement'

  parser = argparse.ArgumentParser(description=description)

  parser.add_argument('--mask_folder', required=True,  type=str, action='store', help='Path to the mask files')
  parser.add_argument('--fmt',         required=False, type=str, action='store', default='png', help='Output format of the image_chips and image_masks')

  args = parser.parse_args()

  params = {
              'mask'    : args.mask_folder,
              'format'  : args.fmt,
            }

  return params


def main ():

  params = parse_args()

  files = glob(os.path.join(params['mask'], '*.{}'.format(params['format'])))

  dist = lambda x, y: abs(x[0] - y[0]) + abs(x[1] - y[1]) + abs(x[2] - y[2])

  print('Found {} files to analyze'.format(len(files)))

  for file in tqdm.tqdm(files):

    # read the image
    img = cv2.imread(file, cv2.IMREAD_COLOR)
    w, h, c = img.shape
    # reshape the image into a series of 3D tuples
    img = img.reshape(np.prod(img.shape[:2]), 3)
    img = list(map(tuple, img))

    # refine the color list associating the nearest color (ref. color maps in COLORS)
    temp = []
    for color in img:
      d = [dist(color, k) for k in COLORS]
      nearest_color = np.argmin(d)
      temp.append(COLORS[nearest_color])

    # reshape to the image fmt
    img = np.reshape(temp, newshape=(w, h, c))

    # overwrite the image with its refined version
    cv2.imwrite(file, img)


if __name__ == '__main__':

  main()