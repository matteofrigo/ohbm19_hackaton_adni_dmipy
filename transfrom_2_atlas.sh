#!/bin/bash

cd /media/amr/HDD/ohbm/data_ohbm/Ball_Stick/

for subject in *;do
antsApplyTransforms \
--default-value 0 \
--dimensionality 3 \
--float 1 \
--input ${subject}/${subject}_partial_volume_0.nii.gz \
--input-image-type 3 \
--interpolation Linear \
--output /media/amr/HDD/ohbm/data_ohbm/Ball_Stick/${subject}/${subject}_partial_volume_0_atlas.nii.gz \
--reference-image /usr/share/fsl/5.0/data/atlases/JHU/JHU-ICBM-FA-2mm.nii.gz \
--transform /media/amr/HDD/ohbm/data_ohbm/adni_2_JHU_Composite.h5 \
--transform /media/amr/HDD/ohbm/ohbm_reg_workingdir/ohbm_reg/_subject_id_${subject}/reg_FA_2_temp/transformComposite.h5
done



fslmerge \
-t /media/amr/HDD/ohbm/ball_stick_partial_volume_0_all_subjects  \
/media/amr/HDD/ohbm/data_ohbm/Ball_Stick/*/*_partial_volume_0_atlas.nii.gz