# In[1]:

from nipype import config
cfg = dict(execution={'remove_unnecessary_outputs': False})
config.update_config(cfg)

import nipype.interfaces.fsl as fsl
import nipype.interfaces.afni as afni
import nipype.interfaces.ants as ants
import nipype.interfaces.spm as spm

from nipype.interfaces.utility import IdentityInterface, Function, Select, Merge
from os.path import join as opj
from nipype.interfaces.io import SelectFiles, DataSink
from nipype.pipeline.engine import Workflow, Node, MapNode

import numpy as np
import os, re
import matplotlib.pyplot as plt
from nipype.interfaces.matlab import MatlabCommand
MatlabCommand.set_default_paths('/Users/amr/Downloads/spm12')
MatlabCommand.set_default_matlab_cmd("matlab -nodesktop -nosplash")

# import nipype.interfaces.matlab as mlab
# mlab.MatlabCommand.set_default_matlab_cmd("matlab -nodesktop -nosplash")
# mlab.MatlabCommand.set_default_paths('/home/amr/Documents/MATLAB/toolbox/spm8')

#========================================================================================================
# In[2]:

experiment_dir = '/home/in/aeed/ohbm/data_ohbm' 
#288 -> hydrocephaly
#271, 272 -> medtomidine and died

# subject_list = ['002_S_6652_1']
subject_list = ['002_S_6652_1',
'007_S_1222_1',
'007_S_2394_10',
'007_S_2394_9',
'007_S_4272_10',
'007_S_4272_9',
'007_S_4387_10',
'007_S_4387_9',
'007_S_4488_10',
'007_S_4488_9',
'007_S_4620_10',
'007_S_4620_9',
'007_S_4637_10',
'007_S_4637_9',
'007_S_5265_7',
'007_S_5265_8',
'007_S_6120_1',
'007_S_6120_4',
'007_S_6255_1',
'007_S_6310_1',
'007_S_6323_1',
'007_S_6341_1',
'007_S_6421_1',
'007_S_6515_1',
'007_S_6521_1',
'023_S_4115_1',
'023_S_4164_1',
'023_S_4448_1',
'023_S_6334_1',
'023_S_6346_1',
'023_S_6356_1',
'023_S_6369_1',
'023_S_6374_1',
'023_S_6399_1',
'023_S_6400_1',
'023_S_6535_1',
'023_S_6547_1',
'023_S_6661_1',
'024_S_5290_4',
'024_S_6472_1',
'036_S_2380_1',
'036_S_4491_1',
'036_S_6189_1',
'036_S_6231_1',
'037_S_0377_1',
'037_S_4030_4',
'037_S_4214_5',
'037_S_6083_4',
'037_S_6187_1',
'037_S_6204_1',
'037_S_6216_1',
'037_S_6222_1',
'037_S_6230_1',
'037_S_6271_1',
'037_S_6377_1',
'037_S_6620_1',
'037_S_6627_1',
'051_S_5285_1',
'052_S_4944_8',
'067_S_0056_1',
'067_S_0059_1',
'067_S_2301_1',
'067_S_2304_1',
'067_S_4072_1',
'067_S_4184_1',
'067_S_4767_1',
'067_S_4767_4',
'067_S_4782_4',
'067_S_6045_1',
'067_S_6117_1',
'067_S_6138_1',
'067_S_6442_1',
'067_S_6443_1',
'067_S_6474_1',
'067_S_6529_1',
'094_S_6485_1',
'128_S_0205_1',
'128_S_4742_1',
'341_S_6494_1',
'341_S_6605_1',
'341_S_6653_1',
'941_S_1195_1',
'941_S_4376_1',
'941_S_5124_1',
'941_S_6052_4',
'941_S_6068_4',
'941_S_6333_1',
'941_S_6345_1',
'941_S_6384_1',
'941_S_6392_1',
'941_S_6422_1',
'941_S_6454_1',
'941_S_6471_1',
'941_S_6495_1',
'941_S_6496_1',
'941_S_6499_1',
'941_S_6546_1',
'941_S_6570_1',
'941_S_6574_1',
'941_S_6575_1',
'941_S_6580_1',
'941_S_6581_1',]


# subject_list = ['229']


output_dir  = 'ohbm_reg_outputdir'
working_dir = 'ohbm_reg_workingdir'

ohbm_reg = Workflow (name = 'ohbm_reg')
ohbm_reg.base_dir = opj(experiment_dir, working_dir)

#=====================================================================================================
# In[3]:
#to prevent nipype from iterating over the anat image with each func run, you need seperate
#nodes to select the files
#and this will solve the problem I have for almost 6 months
#but notice that in the sessions, you have to iterate also over subject_id to get the {subject_id} var



# Infosource - a function free node to iterate over the list of subject names
infosource = Node(IdentityInterface(fields=['subject_id']),
                  name="infosource")
infosource.iterables = [('subject_id', subject_list)]

#-----------------------------------------------------------------------------------------------------
# In[21]:

templates = {
             'FA_map'     : '/home/in/aeed/ohbm/data_ohbm/DTI_FSL/{subject_id}/{subject_id}_model_DTI_FA.nii.gz',
##############################################DTI##########################################################
             'dti_md' : '/home/in/aeed/ohbm/data_ohbm/DTI_FSL/{subject_id}/{subject_id}_model_DTI_MD.nii.gz',
             'dti_ad' : '/home/in/aeed/ohbm/data_ohbm/DTI_FSL/{subject_id}/{subject_id}_model_DTI_L1.nii.gz',
             'dti_rd' : '/home/in/aeed/ohbm/data_ohbm/DTI_FSL/{subject_id}/{subject_id}_RD.nii.gz',
##############################################ball and stick##########################################################
             'ball_stick_ICVF' : '/home/in/aeed/ohbm/data_ohbm/Ball_Stick/{subject_id}/{subject_id}_partial_volume_0.nii.gz',
             'ball_stick_ECVF' : '/home/in/aeed/ohbm/data_ohbm/Ball_Stick/{subject_id}/{subject_id}_partial_volume_1.nii.gz',
##############################################NODDI##########################################################
             'noddi_mu' : '/home/in/aeed/ohbm/data_ohbm/NODDI_Watson/{subject_id}/{subject_id}_SD1WatsonDistributed_1_SD1Watson_1_mu.nii.gz',
             'noddi_odi' : '/home/in/aeed/ohbm/data_ohbm/NODDI_Watson/{subject_id}/{subject_id}_SD1WatsonDistributed_1_SD1Watson_1_odi.nii.gz',
             'noddi_ICVF' : '/home/in/aeed/ohbm/data_ohbm/NODDI_Watson/{subject_id}/{subject_id}_icvf.nii.gz',
             'noddi_ECVF' : '/home/in/aeed/ohbm/data_ohbm/NODDI_Watson/{subject_id}/{subject_id}_ecvf.nii.gz',
             'noddi_ISOVF' : '/home/in/aeed/ohbm/data_ohbm/NODDI_Watson/{subject_id}/{subject_id}_isovf.nii.gz',
##############################################MCDMI##########################################################
             'mcmdi_lambda' : '/home/in/aeed/ohbm/data_ohbm/MCMDI/{subject_id}/{subject_id}_BundleModel_1_G2Zeppelin_1_lambda_par.nii.gz',
             'mcmdi_ICVF' : '/home/in/aeed/ohbm/data_ohbm/MCMDI/{subject_id}/{subject_id}_icvf.nii.gz',
             'mcmdi_ECVF' : '/home/in/aeed/ohbm/data_ohbm/MCMDI/{subject_id}/{subject_id}_ecvf.nii.gz',
##############################################MAPMRI##########################################################
             'mapmri_lap' : '/home/in/aeed/ohbm/data_ohbm/MAPMRI/{subject_id}/{subject_id}_laplacian_norm.nii.gz',
             'mapmri_msd' : '/home/in/aeed/ohbm/data_ohbm/MAPMRI/{subject_id}/{subject_id}_msd.nii.gz',
             'mapmri_qiv' : '/home/in/aeed/ohbm/data_ohbm/MAPMRI/{subject_id}/{subject_id}_qiv.nii.gz',
             'mapmri_rtap' : '/home/in/aeed/ohbm/data_ohbm/MAPMRI/{subject_id}/{subject_id}_rtap.nii.gz',
             'mapmri_rtop' : '/home/in/aeed/ohbm/data_ohbm/MAPMRI/{subject_id}/{subject_id}_rtop.nii.gz',
             'mapmri_rtpp' : '/home/in/aeed/ohbm/data_ohbm/MAPMRI/{subject_id}/{subject_id}_rtpp.nii.gz',

             


             }

selectfiles = Node(SelectFiles(templates,
                               base_directory=experiment_dir),
                   name="selectfiles")
#-----------------------------------------------------------------------------------------------------

#========================================================================================================
# In[5]:

datasink = Node(DataSink(), name = 'datasink')
datasink.inputs.container = output_dir
datasink.inputs.base_directory = experiment_dir

substitutions = [('_subject_id_', ''),('_fwhm_', 'fwhm-')]
#substitutions = [('_subject_id_', '')]
datasink.inputs.substitutions = substitutions


# fsl.FSLCommand.set_default_output_type('NIFTI')


#========================================================================================================
# In[6]:

template_brain = '/home/in/aeed/ohbm/FA_template/adni_FAtemplate.nii.gz'
template_2_atlas_trans = '/home/in/aeed/ohbm/data_ohbm/adni_2_JHU_Composite.h5'
#========================================================================================================


## normalizing the anatomical_bias_corrected image to the common anatomical template
## Here only we are calculating the paramters, we apply them later.

reg_FA_2_temp = Node(ants.Registration(), name = 'reg_FA_2_temp')
reg_FA_2_temp.inputs.args='--float'
reg_FA_2_temp.inputs.collapse_output_transforms=True
reg_FA_2_temp.inputs.fixed_image=template_brain
reg_FA_2_temp.inputs.initial_moving_transform_com=True
reg_FA_2_temp.inputs.num_threads=8
reg_FA_2_temp.inputs.output_inverse_warped_image=True
reg_FA_2_temp.inputs.output_warped_image=True
reg_FA_2_temp.inputs.sigma_units=['vox']*3
reg_FA_2_temp.inputs.transforms= ['Rigid', 'Affine', 'SyN']
reg_FA_2_temp.inputs.winsorize_lower_quantile=0.005
reg_FA_2_temp.inputs.winsorize_upper_quantile=0.995
reg_FA_2_temp.inputs.convergence_threshold=[1e-06]
reg_FA_2_temp.inputs.convergence_window_size=[10]
reg_FA_2_temp.inputs.metric=['MI', 'MI', 'CC']
reg_FA_2_temp.inputs.metric_weight=[1.0]*3
reg_FA_2_temp.inputs.number_of_iterations=[[1000, 500, 250, 100],
                                                 [1000, 500, 250, 100],
                                                 [100, 70, 50, 20]]
reg_FA_2_temp.inputs.radius_or_number_of_bins=[32, 32, 4]
reg_FA_2_temp.inputs.sampling_percentage=[0.25, 0.25, 1]
reg_FA_2_temp.inputs.sampling_strategy=['Regular',
                                        'Regular',
                                        'None']
reg_FA_2_temp.inputs.shrink_factors=[[8, 4, 2, 1]]*3
reg_FA_2_temp.inputs.smoothing_sigmas=[[3, 2, 1, 0]]*3
reg_FA_2_temp.inputs.transform_parameters=[(0.1,),
                                           (0.1,),
                                           (0.1, 3.0, 0.0)]
reg_FA_2_temp.inputs.use_histogram_matching=True
reg_FA_2_temp.inputs.write_composite_transform=True
reg_FA_2_temp.inputs.verbose=True
reg_FA_2_temp.inputs.output_warped_image=True
reg_FA_2_temp.inputs.float=True



#========================================================================================================

merge_transformations = Node(Merge(2), name = 'Merge_Transformations')
merge_transformations.inputs.in1 = template_2_atlas_trans


#========================================================================================================
# In[14]:

# apply the trasnfromation to all the EPI volumes

fa_2_atlas = Node(ants.ApplyTransforms(), name = 'fa_2_atlas')
fa_2_atlas.inputs.dimension = 3

fa_2_atlas.inputs.input_image_type = 3
fa_2_atlas.inputs.num_threads = 1
fa_2_atlas.inputs.float = True
fa_2_atlas.inputs.reference_image = '/home/in/aeed/fsl/fsl/data/atlases/JHU/JHU-ICBM-FA-2mm.nii.gz'
#========================================================================================================
md_2_atlas = fa_2_atlas.clone(name = 'md_2_atlas')
rd_2_atlas = fa_2_atlas.clone(name = 'rd_2_atlas')
ad_2_atlas = fa_2_atlas.clone(name = 'ad_2_atlas')


ball_stick_ICVF_2_atlas = fa_2_atlas.clone(name = 'ball_stick_ICVF_2_atlas')
ball_stick_ECVF_2_atlas = fa_2_atlas.clone(name = 'ball_stick_ECVF_2_atlas')

noddi_mu_2_atlas = fa_2_atlas.clone(name = 'noddi_mu_2_atlas')
noddi_odi_2_atlas = fa_2_atlas.clone(name = 'noddi_odi_2_atlas')
noddi_ICVF_2_atlas = fa_2_atlas.clone(name = 'noddi_ICVF_2_atlas')
noddi_ECVF_2_atlas = fa_2_atlas.clone(name = 'noddi_ECVF_2_atlas')
noddi_ISOVF_2_atlas = fa_2_atlas.clone(name = 'noddi_ISOVF_2_atlas')


mcmdi_lambda_2_atlas = fa_2_atlas.clone(name = 'mcmdi_lambda_2_atlas')
mcmdi_ICVF_2_atlas = fa_2_atlas.clone(name = 'mcmdi_ICVF_2_atlas')
mcmdi_ECVF_2_atlas = fa_2_atlas.clone(name = 'mcmdi_ECVF_2_atlas')


mapmri_lap_2_atlas = fa_2_atlas.clone(name = 'mapmri_lap_2_atlas')
mapmri_msd_2_atlas = fa_2_atlas.clone(name = 'mapmri_msd_2_atlas')
mapmri_qiv_2_atlas = fa_2_atlas.clone(name = 'mapmri_qiv_2_atlas')
mapmri_rtap_2_atlas = fa_2_atlas.clone(name = 'mapmri_rtap_2_atlas')
mapmri_rtop_2_atlas = fa_2_atlas.clone(name = 'mapmri_rtop_2_atlas')
mapmri_rtpp_2_atlas = fa_2_atlas.clone(name = 'mapmri_rtpp_2_atlas')
#========================================================================================================
# In[21]:

ohbm_reg.connect([


              (infosource, selectfiles,[('subject_id','subject_id')]),
              (selectfiles, reg_FA_2_temp, [('FA_map','moving_image')]),

              (reg_FA_2_temp, merge_transformations, [('composite_transform','in2')]),

              (selectfiles, fa_2_atlas, [('FA_map','input_image')]),
              (merge_transformations, fa_2_atlas, [('out','transforms')]),


###########################
              (fa_2_atlas, datasink, [('output_image','fa_2_atlas')]),


              (selectfiles, md_2_atlas, [('dti_md','input_image')]),
              (md_2_atlas, datasink, [('output_image','md_2_atlas')]),
              (merge_transformations, md_2_atlas, [('out','transforms')]),


              (selectfiles, rd_2_atlas, [('dti_rd','input_image')]),
              (rd_2_atlas, datasink, [('output_image','rd_2_atlas')]),
              (merge_transformations, rd_2_atlas, [('out','transforms')]),

              (selectfiles, ad_2_atlas, [('dti_ad','input_image')]),
              (ad_2_atlas, datasink, [('output_image','ad_2_atlas')]),
              (merge_transformations, ad_2_atlas, [('out','transforms')]),
#############################
              
              (selectfiles, ball_stick_ICVF_2_atlas, [('ball_stick_ICVF','input_image')]),
              (ball_stick_ICVF_2_atlas, datasink, [('output_image','ball_stick_ICVF_2_atlas')]),
              (merge_transformations, ball_stick_ICVF_2_atlas, [('out','transforms')]),

              
              (selectfiles, ball_stick_ECVF_2_atlas, [('ball_stick_ECVF','input_image')]),
              (ball_stick_ECVF_2_atlas, datasink, [('output_image','ball_stick_ECVF_2_atlas')]),
              (merge_transformations, ball_stick_ECVF_2_atlas, [('out','transforms')]),
############################
              
              (selectfiles, noddi_mu_2_atlas, [('noddi_mu','input_image')]),
              (noddi_mu_2_atlas, datasink, [('output_image','noddi_mu_2_atlas')]),
              (merge_transformations, noddi_mu_2_atlas, [('out','transforms')]),

              (selectfiles, noddi_odi_2_atlas, [('noddi_odi','input_image')]),
              (noddi_odi_2_atlas, datasink, [('output_image','noddi_odi_2_atlas')]),
              (merge_transformations, noddi_odi_2_atlas, [('out','transforms')]),
              
              (selectfiles, noddi_ICVF_2_atlas, [('noddi_ICVF','input_image')]),
              (noddi_ICVF_2_atlas, datasink, [('output_image','noddi_ICVF_2_atlas')]),
              (merge_transformations, noddi_ICVF_2_atlas, [('out','transforms')]),

              (selectfiles, noddi_ECVF_2_atlas, [('noddi_ECVF','input_image')]),
              (noddi_ECVF_2_atlas, datasink, [('output_image','noddi_ECVF_2_atlas')]),
              (merge_transformations, noddi_ECVF_2_atlas, [('out','transforms')]),
              
              (selectfiles, noddi_ISOVF_2_atlas, [('noddi_ISOVF','input_image')]),
              (noddi_ISOVF_2_atlas, datasink, [('output_image','noddi_ISOVF_2_atlas')]),
              (merge_transformations, noddi_ISOVF_2_atlas, [('out','transforms')]),
##############################
              (selectfiles, mcmdi_lambda_2_atlas, [('mcmdi_lambda','input_image')]),
              (mcmdi_lambda_2_atlas, datasink, [('output_image','mcmdi_lambda_2_atlas')]),
              (merge_transformations, mcmdi_lambda_2_atlas, [('out','transforms')]),

              (selectfiles, mcmdi_ICVF_2_atlas, [('mcmdi_ICVF','input_image')]),
              (mcmdi_ICVF_2_atlas, datasink, [('output_image','mcmdi_ICVF_2_atlas')]),
              (merge_transformations, mcmdi_ICVF_2_atlas, [('out','transforms')]),

              (selectfiles, mcmdi_ECVF_2_atlas, [('mcmdi_ECVF','input_image')]),
              (mcmdi_ECVF_2_atlas, datasink, [('output_image','mcmdi_ECVF_2_atlas')]),
              (merge_transformations, mcmdi_ECVF_2_atlas, [('out','transforms')]),
##############################
              (selectfiles, mapmri_lap_2_atlas, [('mapmri_lap','input_image')]),
              (mapmri_lap_2_atlas, datasink, [('output_image','mapmri_lap_2_atlas')]),
              (merge_transformations, mapmri_lap_2_atlas, [('out','transforms')]),


              (selectfiles, mapmri_msd_2_atlas, [('mapmri_msd','input_image')]),
              (mapmri_msd_2_atlas, datasink, [('output_image','mapmri_msd_2_atlas')]),
              (merge_transformations, mapmri_msd_2_atlas, [('out','transforms')]),

              (selectfiles, mapmri_qiv_2_atlas, [('mapmri_qiv','input_image')]),
              (mapmri_qiv_2_atlas, datasink, [('output_image','mapmri_qiv_2_atlas')]),
              (merge_transformations, mapmri_qiv_2_atlas, [('out','transforms')]),

              (selectfiles, mapmri_rtap_2_atlas, [('mapmri_rtap','input_image')]),
              (mapmri_rtap_2_atlas, datasink, [('output_image','mapmri_rtap_2_atlas')]),
              (merge_transformations, mapmri_rtap_2_atlas, [('out','transforms')]),

              (selectfiles, mapmri_rtop_2_atlas, [('mapmri_rtop','input_image')]),
              (mapmri_rtop_2_atlas, datasink, [('output_image','mapmri_rtop_2_atlas')]),
              (merge_transformations, mapmri_rtop_2_atlas, [('out','transforms')]),

              (selectfiles, mapmri_rtpp_2_atlas, [('mapmri_rtpp','input_image')]),
              (mapmri_rtpp_2_atlas, datasink, [('output_image','mapmri_rtpp_2_atlas')]),
              (merge_transformations, mapmri_rtpp_2_atlas, [('out','transforms')]),


              #======================================datasink============================================

              ])


ohbm_reg.write_graph(graph2use='colored', format='png', simple_form=True)

ohbm_reg.run(plugin='SLURM',plugin_args={'dont_resubmit_completed_jobs': True, 'max_jobs':50})
# ohbm_reg.run('MultiProc', plugin_args={'no_procs' : 8})
