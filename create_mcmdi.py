import argparse

from os import path

import nibabel as nib


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compute ICVF and ECVF for the MCDMI model.'
                                                 'The maps are saved in "datafolder/subject/subject_<map>.nii.gz" .')

    parser.add_argument('datafolder', type=str,
                        help='Path to the folder NODDI_Watson')
    parser.add_argument('subject', type=str,
                        help='Subject id')
    args = parser.parse_args()
    datafolder = args.datafolder
    subject = args.subject

    pv0 = nib.load(path.join(datafolder, subject, subject+'_BundleModel_1_partial_volume_0.nii.gz'))

    file_icvf = path.join(datafolder, subject, subject+'_icvf.nii.gz')
    file_ecvf = path.join(datafolder, subject, subject+'_ecvf.nii.gz')

    data_pv0 = pv0.get_data()

    # Compute ICVF
    data_icvf = data_pv0
    image_icvf = nib.Nifti1Image(data_icvf, affine=pv0.affine, header=pv0.header)
    nib.save(image_icvf, file_icvf)
    print('Saved '+file_icvf)

    # Compute ECVF
    data_ecvf = 1.0 - data_pv0
    image_ecvf = nib.Nifti1Image(data_ecvf, affine=pv0.affine, header=pv0.header)
    nib.save(image_ecvf, file_ecvf)
    print('Saved '+file_ecvf)