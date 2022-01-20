"""
Overlay MIRI apertures on your plots
"""

import matplotlit.pyplot as plt
import numpy as np

from pysiaf import Siaf


# helper plotting function
def plot_with_aper(img, aper_name='MIRIM_MASK1065', ax=None, fig_kws={}, plot_kws={}):
    """
    Plot an image with the aperture outline and reference point overlaid
    img: 2-D image
    aper_name: SIAF-searchable MIRI aperture name. Must match the image footprint.
    ax [None]: axis to draw on. If None, creates new figure
    fig_kws [{}]: figure arguments to pass to plt.subplots()
    plot_kws [{}]: arguments to pass to the plotting function (e.g. ax.imshow(img, **plot_kws))
    Output:
    returns the current fig and ax as a tuple (fig, ax)
    """
    if ax == None:
        fig, ax = plt.subplots(1, 1, **fig_kws)
    else:
        fig = ax.get_figure()
    ax.set_xlabel("subarray pixel")
    ax.set_ylabel("subarray pixel")
    
    aper = Siaf("MIRI")[aper_name]
    aper.plot(frame='sci', ax=ax, fill=False, mark_ref=True, c='C1')

    # using the aperture corner definitions to set the plot coordinates
    # ensures that the plotted image will match up with the aperture's 
    # features, e.g. the reference point
    corners = aper.corners('sci')
    x, y = np.meshgrid(np.arange(corners[0].min(), corners[0].max()+1, 1),
                       np.arange(corners[1].min(), corners[1].max()+1, 1))
    
    ax.pcolor(x, y, img, zorder=-1, **plot_kws)
    
    lolim, hilim = np.min(corners, axis=1), np.max(corners, axis=1)
    ax.set_xlim(lolim[0]-5, hilim[0]+5)
    ax.set_ylim(lolim[1]-5, hilim[1]+5)
    return fig, ax
