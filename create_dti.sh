#!/usr/bin/env bash

DATAFOLDER=${1}
SUBJECT=${2}

L2=${DATAFOLDER}/${SUBJECT}/${SUBJECT}_model_DTI_L2.nii.gz
L3=${DATAFOLDER}/${SUBJECT}/${SUBJECT}_model_DTI_L3.nii.gz

SUM=/tmp/sum.nii.gz

RD_FILE=${DATAFOLDER}/${SUBJECT}/${SUBJECT}_RD.nii.gz

fslmaths \
    ${L2} \
    -add \
    ${L3} \
    ${SUM}

fslmaths \
    ${SUM} \
    -div \
    2.0 \
    ${RD_FILE}