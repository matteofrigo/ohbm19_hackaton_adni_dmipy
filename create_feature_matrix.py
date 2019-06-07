#!/usr/bin/env python
from os import path as op

import numpy as np
import nibabel as nib

description=""" 
Script to generate the feature matrices
	
Usage : python create_feature_matrix.py --input_maps map1_path map2_path --atlas_rois atlas_label_path --o_feature_block o_feature_block_path --o_roi_block o_feature_block_path

Example :

cd <code folder>
python create_feature_matrix.py --input_maps './data/4d_FA.nii.gz' './data/4d_FA.nii.gz' --atlas_rois './data/JHU-ICBM-FSL/JHU-ICBM-labels-2mm.nii.gz' --o_feature_block './data/o_feature_block.csv' --o_roi_block './data/o_roi_block.csv'

Author : Sebastien Tourbier (sebastientourbier)

Date : June 07 2019  
"""

def get_parser():
    import argparse

    p = argparse.ArgumentParser(
        description=description)

    p.add_argument('--input_maps',
                   help='The input scalar features. 4th dimension corresponds to subjects',
                   nargs="+")

    p.add_argument('--o_feature_block',
                   help='Output feature matrix with structure\n'
                        '{[Feature1 : (roi1,roi2,...)], [Feature2 : (roi1,roi2,...)], [...]}')
    p.add_argument('--o_roi_block',
                   help='Output feature matrix with structure\n'
                        '{[roi1 : (f1, f2, ...)], [roi2 : (f1, f2, ...)], [...]}')

    p.add_argument('--atlas_rois', help='The Atlas labels (ROIs) image.')

    return p


def process(input_features, atlas_rois, o_feature_block, o_roi_block):
    print("Start process ...")

    print("Load ROIS file : {}".format(atlas_rois))
    labels = nib.load(atlas_rois).get_data()

    number_of_regions = labels.max()
    print('Number of regions: {}'.format(number_of_regions))

    number_of_features = len(input_features)
    print('Number of features : {}'.format(number_of_features))

    number_of_subjects = nib.load(input_features[0]).get_data().shape[3]
    print('Number of subjects : {}'.format(number_of_subjects))

    # Feature1 : {roi1,roi2,...}, Feature2 : {roi1,roi2,...}
    arr1 = np.zeros(
        (number_of_subjects, number_of_features * number_of_regions))

    # ROI1 : {feat1,feat2,...}, ROI2 : {feat1,feat2,...}
    arr2 = np.zeros(
        (number_of_subjects, number_of_features * number_of_regions))

    for subj in np.arange(1, number_of_subjects + 1, 1):
        print('Process subject {}...'.format(subj))

        feature_cnt = 0

        for file in input_features:
            feature = nib.load(file).get_data()[:, :, :, subj - 1]
            roi_cnt = 0

            for roi in np.arange(1, number_of_regions + 1, 1):
                idx = np.where(labels == roi)
                m = feature[idx].mean()

                # subj start from 1
                arr1[
                    (subj - 1), (roi_cnt + feature_cnt * number_of_regions)] = m
                arr2[(subj - 1), (
                            feature_cnt + roi_cnt * number_of_features)] = m

                roi_cnt += 1

            feature_cnt += 1

    print('Saving {}...'.format(op.abspath(o_feature_block)))
    np.savetxt(op.abspath(o_feature_block), arr1, delimiter=",")

    print('Saving {}...'.format(op.abspath(o_roi_block)))
    np.savetxt(op.abspath(o_roi_block), arr2, delimiter=",")

    print('[Done]')


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    print('Running script with args: {}'.format(args))
    process(args.input_maps, args.atlas_rois, args.o_feature_block,
            args.o_roi_block)
