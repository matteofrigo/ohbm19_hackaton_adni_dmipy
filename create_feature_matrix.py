#!/usr/bin/env python

""" 
Script to generate the feature matrices
	
Usage : python create_feature_matrix.py --input_maps map1_path map2_path --atlas_labels atlas_label_path --output_matrix1 output_matrix1_path --output_matrix2 output_matrix1_path

Example :

cd <code folder>
python create_feature_matrix.py --input_maps './data/4d_FA.nii.gz' './data/4d_FA.nii.gz' --atlas_labels './data/JHU-ICBM-FSL/JHU-ICBM-labels-2mm.nii.gz' --output_matrix1 './data/output_matrix1.csv' --output_matrix2 './data/output_matrix2.csv'

Author : Sebastien Tourbier (sebastientourbier)

Date : June 07 2019  
"""

import os
import sys
from os import path as op
from glob import glob

import numpy as np
import nibabel as nib

def get_parser():
	import argparse

	p = argparse.ArgumentParser(description='Script to generate features matrix')

	p.add_argument('--input_maps', help='The input scalar features. 4th dimension corresponds to subjects',
		nargs="+")

	p.add_argument('--output_matrix1', help='Output feature matrix')
	p.add_argument('--output_matrix2', help='Output feature matrix')

	p.add_argument('--atlas_labels', help='The Atlas labels (ROIs) image.')

	return p

def process(input_features,atlas_labels,output_matrix1,output_matrix2):
	print("Start process ...")

	print("Load ROIS file : {}".format(atlas_labels))
	labels = nib.load(atlas_labels).get_data()

	number_of_regions = labels.max()
	print('Number of regions: {}'.format(number_of_regions))

	number_of_features = len(input_features)
	print('Number of features : {}'.format(number_of_features))

	number_of_subjects = nib.load(input_features[0]).get_data().shape[3]
	print('Number of subjects : {}'.format(number_of_subjects))

	# Feature1 : {roi1,roi2,...}, Feature2 : {roi1,roi2,...}
	arr1 = np.zeros((number_of_subjects,number_of_features*number_of_regions))

	# ROI1 : {feat1,feat2,...}, ROI2 : {feat1,feat2,...}
	arr2 = np.zeros((number_of_subjects,number_of_features*number_of_regions))

	for subj in np.arange(1,number_of_subjects+1,1):
		print('Process subject {}...'.format(subj))

		feature_cnt = 0

		for file in input_features: 
			#print("  >  Load feature: {}".format(file))
			feature = nib.load(file).get_data()[:,:,:,subj-1]

			#print('Size of feature: {}'.format(feature.shape))

			roi_cnt = 0

			for roi in np.arange(1,number_of_regions+1,1):
				#print('    >  Process roi {}...'.format(roi))	
				idx = np.where(labels==roi)
				#print('idx: {}'.format(idx))
				m = feature[idx].mean()
				#print('Mean: {}'.format(m))

				#subj start from 1	
				arr1[(subj-1),(roi_cnt + feature_cnt * number_of_regions) ] = m	
				arr2[(subj-1),(feature_cnt + roi_cnt * number_of_features)] = m
			
				roi_cnt+=1

			feature_cnt+=1

	print('Saving {}...'.format(op.abspath(output_matrix1)))
	np.savetxt(op.abspath(output_matrix1), arr1, delimiter=",")

	print('Saving {}...'.format(op.abspath(output_matrix2)))
	np.savetxt(op.abspath(output_matrix2), arr2, delimiter=",")

	print('[Done]')


if __name__ == '__main__':

	parser = get_parser()
	args = parser.parse_args()

	print('Running script with args: {}'.format(args))
	process(args.input_maps,args.atlas_labels,args.output_matrix1,args.output_matrix2)