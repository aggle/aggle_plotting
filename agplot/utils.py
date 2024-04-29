import numpy as np
from matplotlib import pyplot as plt

def set_up_multifig(nimgs, ncols, scalesize, kwargs={}):
    """
    Wrapper for the usual things I do to set up a multiple axes figure

    Parameters
    ----------
    nimgs: int
      the number of images
    ncols: int
      the number of columns (the number of rows will be computed)
    scalesize: float
      use this to scale the figure size; will be proportional to fig dimensions
    kwargs: dict (default: {})
      any other arguments to pass to plt.subplots()

    Output
    ------
    tuple of (fig, axes)

    """
    nrows = np.ceil(nimgs/ncols).astype(int)
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols,
                             figsize=(scalesize*ncols, scalesize*nrows),
                             squeeze=False,
                             **kwargs)
    for ax in axes.ravel()[nimgs:]:
        ax.set_visible(False)
    return (fig, axes)
