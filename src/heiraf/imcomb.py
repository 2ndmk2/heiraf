import sys
import argparse 
import glob
import os
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy import units as u
from astropy.nddata import CCDData
from ccdproc import Combiner
import numpy as np

"""
IRAF "imcomb"

# python imcomb.py flat_list_blue.dat test.fits --reject sigma --lsigma 2 --hsigma 2 --scaling

"""


def make_copy_from_head_of_input_file(fits_file, file_out_fits ):
    
    os.system("cp %s %s" % (fits_file, file_out_fits))   

def update_fits_with_new_image(fitsfile, new_image):

    hdu = fits.open(fitsfile, mode='update')
    hdu[0].data = new_image
    hdu.close()

def make_list_from_dat(file_input_name):
    file_input = open(file_input_name,"r")
    lines = file_input.readlines()
    list_files = []
    for line in lines:
        list_files.append(line.replace("\n",""))
    file_input.close()
    return list_files

def make_ccds_for_combiner_from_list(fits_files):

    ccds = []
    for fits_file in fits_files:
        with fits.open(fits_file) as hdul:
            image = hdul[0].data
            ccd = CCDData(image, unit=u.adu)
            ccds.append(ccd)
    combiner = Combiner(ccds)

    return combiner 

def clipping(combiner, clip_method, low_thresh=2, high_thresh=5, nlow=1, nhigh=2,min_clip=-0.3, max_clip=0.1):
    """
    Clipping with Combiner from ccdproc. Copy from following site: 
    https://ccdproc.readthedocs.io/en/latest/image_combination.html#
    """
    
    #The sigma_clipping method is very flexible: you can specify both the function for calculating the 
    #central value and the function for calculating the deviation. The default is to use the mean 
    #(ignoring any masked pixels) for the central value and the standard deviation 
    #(again ignoring any masked values) for the deviation.
    
    #You can mask pixels more than "high_thresh" standard deviations above or "low_thresh" standard deviations below the median with
    if clip_method=="sigma":
        combiner.sigma_clipping(low_thresh=low_thresh, high_thresh=high_thresh, func=np.ma.median)
    

    # minmax_clipping: masks all pixels above or below user-specified levels. 
    #For example, to mask all values above the value "max_clip"  and below the value "min_clip":
    if clip_method=="minmax_with_value":
        combiner.minmax_clipping(min_clip=min_clip, max_clip=max_clip)    
    
    #For each pixel position in the input arrays, the algorithm will mask the highest nhigh 
    #and lowest nlow pixel values. The resulting image will be a combination of Nimages-nlow-nhigh pixel 
    #values instead of the combination of Nimages worth of pixel values.
    if clip_method=="minmax":
        combiner.clip_extrema(nlow=nlow, nhigh=nhigh)
    return combiner

def combine(combiner, combine_method, scaling =False):

    if scaling:
        scaling_func = lambda arr: 1/np.ma.average(arr)
        combiner.scaling = scaling_func 
        
    if combine_method=="average":
        combined_image = combiner.average_combine()  
        
    if combine_method=="median":
        combined_image  = combiner.median_combine()  
    return combined_image

def imcombine_core(fits_files, file_out_fits, combine_method, clip_method, scaling =False, \
    low_thresh=2, high_thresh=5, nlow=1, nhigh=2,min_clip=-0.3, max_clip=0.1):
    """
    Params:
        fits_files: list for fitsfile names
        file_out_fits: name for output fits
        scaling: If True, flux is normalized. 
        Other parameters are similar to iraf imcocmbine. 
    """

    make_copy_from_head_of_input_file(fits_files[0], file_out_fits )
    combiner = make_ccds_for_combiner_from_list(fits_files)
    clipping(combiner, clip_method, low_thresh, high_thresh, nlow, nhigh, min_clip, max_clip)
    combined_image = combine(combiner,combine_method, scaling)
    update_fits_with_new_image(file_out_fits, combined_image)

    return combined_image

if __name__ == '__main__':

    parser = argparse.ArgumentParser('')

    ## Basic params
    parser.add_argument('input')   
    parser.add_argument('output')
    parser.add_argument('--reject', type =str, default="sigma")
    parser.add_argument('--combine', type =str,default="median")  
    parser.add_argument('--scaling', action='store_true')    

    ## Other params
    parser.add_argument('--lsigma', type =float, default=2)   
    parser.add_argument('--hsigma', type =float,default=2)  
    parser.add_argument('--nlow', type =int,default=1)     
    parser.add_argument('--nhigh',type =int, default=1)   

    args = parser.parse_args()
    inputlist_name = args.input
    outputfit_name = args.output
    combine_method = args.combine
    clipping_method = args.reject
    scaling = args.scaling
    lsigma = args.lsigma
    hsigma = args.hsigma
    nlow = args.nlow
    nhigh = args.nhigh

    fits_files = make_list_from_dat(inputlist_name)
    combined_median = imcombine_core(fits_files, outputfit_name, combine_method, clipping_method , scaling =scaling, \
    low_thresh=lsigma, high_thresh=hsigma, nlow=nlow, nhigh=nhigh,min_clip=-0.3, max_clip=0.1)
    plt.imshow(combined_median)
    plt.show()

