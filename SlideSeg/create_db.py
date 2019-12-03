#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import cv2
import pickle
import argparse
import pandas as pd
from glob import glob

__author__ = 'Nico Curti'
__email__ = 'nico.curti2@unibo.it'

def parse_args ():

  description = 'Histological DB creator'

  parser = argparse.ArgumentParser(description=description)

  parser.add_argument('--svs_folder', required=True, type=str, action='store', help='Path to the SVS files')

  args = parser.parse_args()

  params = {
              'svs'    : args.svs_folder,
              'format' : '{0}_output/{0}.csv'
            }

  return params

if __name__ == '__main__':

  params = parse_args()

  # list all the SVS files into the given folder
  svs = glob(os.path.join(params['svs'], '*.{}'.format('svs')))
  # extract the file name (without extension) from the file list
  files = [os.path.splitext(os.path.basename(x))[0] for x in svs]

  # final DB obj
  db = []

  for file in files:

    # fill the format string with the current infos
    fmt = params['format'].format(file)
    # re-create the counter filename
    counter_file = os.path.join(params['svs'], fmt)

    # read the csv counter filen
    data = pd.read_csv(counter_file, sep=',', header=0)
    # filter the counter accordin to the following query
    melanoma = data[(data['extra-tissue']     == 0) &
                    (data['background']       == 0) &
                    (data['nevo-benigno']     == 0) &
                    (data['melanoma-maligno'] == 1)
                    ]
    print('Found {} pure-melanoma patches in {}.svs'.format(len(melanoma), file))

    # for each filename extracted from the counter db
    for f in melanoma['Filename']:

      # re-create the right filename location
      filename = os.path.join(params['svs'],
                              '{}_output'.format(file),
                              'image_chips', f)
      # import the image into RGB fmt
      img = cv2.imread(filename, cv2.IMREAD_COLOR)
      img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

      # append to the final DB some infos and the pickle version of the current image
      db.append(('{}.svs'.format(file), f, pickle.dumps(img)))

  # convert the dataset into a Pandas DB
  db = pd.DataFrame(db, columns=['svs', 'file', 'patch'])

  # dump the DB for next processing steps
  db.to_csv('Melanoma_db.csv', sep=',', header=True, index=False)

