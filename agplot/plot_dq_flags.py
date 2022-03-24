"""
Plot the physical distribution of data quality flags on your data
"""
import matplotlib as mpl
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

from pysiaf import Siaf
from jwst import datamodels
from jwst.datamodels import dqflags




def load_model(fname):
    model = datamodels.open(str(fname))
    return model

def make_dqflag_dataframe(datamodel):
    # linearize the array and pull out any pixels with flags
    dq_shape = datamodel.dq.shape  # for putting the pixel coords back in 2-D
    dq_ravel = datamodel.dq.ravel()
    bad_pix_id = np.arange(dq_ravel.size)[dq_ravel != 0]
    bad_pix = dq_ravel[bad_pix_id]
    # make the dataframe
    flag_cols = list(dqflags.pixel.keys())
    dq_df = pd.DataFrame(data=0,
                         index=bad_pix_id,
                         columns=['val', 'pix_id', 'pix_coord'] + flag_cols,
                         dtype=int)

    # select the bad pixels and their positions
    # initialize the val, x, and y columns
    dq_df['val'] = bad_pix
    dq_df['pix_id'] = bad_pix_id
    dq_df['pix_coord'] = list(zip(*np.unravel_index(bad_pix_id, dq_shape)))

    # get all the flags fast!
    all_flags = dq_df['val'].apply(lambda val: dqflags.dqflags_to_mnemonics(val, dqflags.pixel))
    # assign the flag presence to the dataframe
    for i, pix_flags in all_flags.items():
        dq_df.loc[i, pix_flags] = 1
    return dq_df


def make_plots(dq_df, instr_name=None, aper_name=None):
    """
    Plot the locations of all the data quality flags in the DQ image. For now,
    we just collapse all exposures into a single 2-D plane.

    Parameters
    ----------
    dq_df: dataframe with the dq flags and pixels
    instr_name [None]: SIAF name of the instrument
    aper_name [None]: SIAF aperture name, if you want to plot an aperture

    Output
    ------
    creates and returns a figure with a separate axis per flag

    """
    flag_cols = dq_df.columns[3:]
    present_flags = dq_df[flag_cols].sum()[dq_df[flag_cols].sum() > 0].index
    # use SIAF to get the corner of the subarray in detector pixels, 
    # so you can plot the SIAF shapes with the pixels in detector coordinates
    plot_apers = False
    shiftx, shifty = 0, 0
    if (instr_name is not None) and (aper_name is not None):
        instr = Siaf(instr_name)
        aper = instr[aper_name]
        plot_apers = True
        shiftx, shifty = np.min(aper.corners('det'), axis=1) 
    # for each flag, plot the subarray and the position of the flagged pixels
    ncols = 4
    nrows = np.ceil(len(present_flags)/ncols).astype(int)
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(5*ncols, 5*nrows))
    colors = mpl.cm.tab20(np.linspace(0, 1, len(present_flags)))
    for i, (ax, flag, color) in enumerate(zip(axes.ravel(), present_flags, colors)):
        ax.set_title(flag, size='x-large')
        if plot_apers == True:
            aper.plot(frame='det', ax=ax, fill=False, mark_ref=True, c='C1')
        pixels = dq_df.query(f"{flag} == 1")['pix_coord'].apply(lambda el: el[-2:])
        xpix = pixels.apply(lambda el: el[1]) + shiftx
        ypix = pixels.apply(lambda el: el[0]) + shifty
        ax.scatter(xpix, ypix,
                   marker='x', color=color, label='flagged pixels')
        ax.set_aspect('equal')
    # turn off the remaining axes
    for ax in axes.ravel()[i+1:]:
        ax.set_visible(False)
    return fig


def plot_dq_flags(filename, instr_name, aper_name):
    """
    plot the locations of all the data quality flags in the DQ image. For now,
    we just collapse all exposures into a single 2-D plane.

    Parameters
    ----------
    filename: name of the file containing the datamodel
    instr_name [None]: SIAF name of the instrument
    aper_name [None]: SIAF aperture name, if you want to plot an aperture

    Output
    ------
    creates and returns a figure with a separate axis per flag

    """
    dm = plot_dq_flags.load_model(filename)
    df = plot_dq_flags.make_dqflag_dataframe(dm)
    fig = plot_dq_flags.plot_dq_flags(df, instr_name, aper_name)
    return fig
