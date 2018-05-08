# -*- coding: utf-8 -*-
"""
Created on Thu Jul 07 14:24:04 2016

@author: Mic
"""

import numpy as np

#def GridMinor()
#ax2.yaxis.set_minor_locator(minorLocator)

def DataWrite (FileName, Data, Format = '%0.2f'):
    #here is your data, in two numpy arrays
    datafile_id = open(FileName, 'w+')
    data = np.array(Data)
    data = data.T
    #here you transpose your data, so to have it in two columns

    fmt = []
    for i in range(0,len(Data)):
        fmt.append(Format)
    np.savetxt(datafile_id, data, fmt)
    #here the ascii file is populated.
    datafile_id.close()