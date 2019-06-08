import argparse

from os import path

import nibabel as nib


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compute ICVF, ECVF and ISOVF for the NODDI WATSON model.'
                                                 'The maps are saved in "datafolder/subject/subject_<map>.nii.gz" .')

    parser.add_argument('datafolder', type=str,
                        help='Path to the folder NODDI_Watson')
    parser.add_argument('subject', type=str,
                        help='Subject id')
    args = parser.parse_args()
    datafolder = args.datafolder
    subject = args.subject

    pv0 = nib.load(path.join(datafolder, subject, subject+'_partial_volume_0.nii.gz'))
    pv1 = nib.load(path.join(datafolder, subject, subject+'_partial_volume_1.nii.gz'))
    wpv0 = nib.load(path.join(datafolder, subject, subject+'_SD1WatsonDistributed_1_partial_volume_0.nii.gz'))

    file_icvf = path.join(datafolder, subject, subject+'_icvf.nii.gz')
    file_ecvf = path.join(datafolder, subject, subject+'_ecvf.nii.gz')
    file_isovf = path.join(datafolder, subject, subject+'_isovf.nii.gz')

    data_pv0 = pv0.get_data()
    data_pv1 = pv1.get_data()
    data_wpv0 = wpv0.get_data()

    # Compute ICVF
    data_icvf = data_pv1 * data_wpv0
    image_icvf = nib.Nifti1Image(data_icvf, affine=pv1.affine, header=pv1.header)
    nib.save(image_icvf, file_icvf)
    print('Saved '+file_icvf)

    # Compute ECVF
    data_ecvf = data_pv1 * (1.0 - data_wpv0)
    image_ecvf = nib.Nifti1Image(data_ecvf, affine=pv1.affine, header=pv1.header)
    nib.save(image_ecvf, file_ecvf)
    print('Saved '+file_ecvf)

    # Compute ISOVF
    data_isovf = data_pv0
    image_isovf = nib.Nifti1Image(data_isovf, affine=pv0.affine, header=pv0.header)
    nib.save(image_isovf, file_isovf)
    print('Saved '+file_isovf)
