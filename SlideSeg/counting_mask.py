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
from collections import Counter

__author__ = 'Nico Curti'
__email__ = 'nico.curti2@unibo.it'

COLORS = {
           (  0,   0,   0) : 0,
           (  0,   0, 255) : 0,
           (  0, 255,   0) : 0,
           (255,   0,   0) : 0
         }


def parse_args ():

  description = 'Histological masks counting'

  parser = argparse.ArgumentParser(description=description)

  parser.add_argument('--mask_folder', required=True,  type=str, action='store', help='Path to the mask files')
  parser.add_argument('--fmt',         required=False, type=str, action='store', default='png', help='Output format of the image_chips and image_masks')
  parser.add_argument('--outfile',     required=False, type=str, action='store', default='output', help='Output filename with count infos')

  args = parser.parse_args()

  params = {
              'mask'    : args.mask_folder,
              'outfile' : args.outfile,
              'format'  : args.fmt,
            }

  return params


def main ():

  params = parse_args()

  files = glob(os.path.join(params['mask'], '*.{}'.format(params['format'])))

  dist = lambda x, y: abs(x[0] - y[0]) + abs(x[1] - y[1]) + abs(x[2] - y[2])

  print('Found {} files to analyze'.format(len(files)))

  with open(params['outfile'], 'w', encoding='utf-8') as out:

    out.write('Filename,background,malignant-melanoma,benign-nevus,extra-tissue\n')

    for file in tqdm.tqdm(files):

      # read image and convert to RGB
      img = cv2.imread(file, cv2.IMREAD_COLOR)
      img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
      # split the image into a series of 3D tuples
      img = img.reshape(np.prod(img.shape[:2]), 3)

      img = list(map(tuple, img))
      # count the unique colors
      cnt = Counter(img)
      tags = COLORS.copy()

      # check for only 4 colors
      if len(cnt) > len(COLORS):
        temp = []
        colors = list(tags.keys())
        for c, v in cnt.items():
          d = [dist(c, k) for k in colors]
          nearest_color = np.argmin(d)
          temp.append((colors[nearest_color], v))
        cnt = dict(temp)


      tags.update(cnt)
      # print on file the corresponding areas as boolean mask
      tags = ','.join(['1' if v != 0 else '0' for v in tags.values()])
      assert len(tags) == 7

      out.write('{},{}\n'.format(os.path.basename(file), tags))



if __name__ == '__main__':

  main()

