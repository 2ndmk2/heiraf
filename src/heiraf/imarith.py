import sys
import argparse 
import glob
import os
from astropy.io import fits

"""
IRAF "imarith"
#python imarith.py "./test_data/KLS*_sub_1.fits" - bias0.fits .fits sub_1.fits (wildcard)
#python imarith.py "./test_data/KLS00207614_bias_sub_1.fits" - bias0.fits "result.fits"
"""

def make_list_from_dat(file_input_name):

    file_input = open(file_input_name,"r")
    lines = file_input.readlines()
    list_files = []
    for line in lines:
        list_files.append(line.replace("\n",""))
    file_input.close()

    return list_files

def imarith_core(fits_files, operation, fits_file2, out_file, replace_fitsname=".fits"):

    """
    Params:
        fits_files: list for fitsfile names or single fitsname
        operation: operation type for imarith (-, +, *, /)
        fits_file2: input filename for operation 
        out_file: output filename 
        Other parameters are similar to iraf "imcombine". 
    """

    with fits.open(fits_file2) as hdul:
        data_fits2 = hdul[0].data

    if type(fits_files) is list:
        for target_file in fits_files:
            out_file_glob = target_file.replace(out_file, replace_fitsname)
            os.system("cp %s %s" % (target_file, out_file_glob))
            hdu = fits.open(out_file_glob, mode='update')

            if operation =="-":
                hdu[0].data = hdu[0].data - data_fits2
            if operation =="+":
                hdu[0].data = hdu[0].data + data_fits2
            if operation =="*":
                hdu[0].data = hdu[0].data * data_fits2
            if operation =="/":
                hdu[0].data = hdu[0].data / data_fits2

            hdu.close()
    else:

        os.system("cp %s %s" % (fits_file, out_file))
        hdu = fits.open(out_file, mode='update')
        if operation =="-":
            hdu[0].data = hdu[0].data - data_fits2
        if operation =="+":
            hdu[0].data = hdu[0].data + data_fits2
        if operation =="*":
            hdu[0].data = hdu[0].data * data_fits2
        if operation =="/":
            hdu[0].data = hdu[0].data / data_fits2
        hdu.close()
        

if __name__ == '__main__':

    args = sys.argv
    fits_file = str(args[1])
    operation = args[2]
    fits_file2 = args[3]
    out_file = args[4] 

    if len(args)==6:
        replace_fitsname = args[5] 
    else:
        replace_fitsname= ""

    if ".fits" not in fits_file:
        list_files = make_list_from_dat(file_input_name)

    elif "*" in fits_file:
        list_files = glob.glob(fits_file)
    else:
        list_files = fits_file
    print(list_files)

    imarith_core(list_files, operation, fits_file2, out_file, replace_fitsname)
    