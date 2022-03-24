"""
Use ipywidgets to scroll through a datacube
Use with %matplotlib notebook
"""

import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display,clear_output

# first, let's make a generic helper function to generate figures that scroll through cubes
def cube_scroller(cube, fig, ax):
    """
    This function spits out a widget that will scroll through a cube. 
    You need to pass it the 3-D cube of images, and an initialized figure and axis
    (e.g. created with fig, ax = plt.subplots(1,1)).
    Example usage displaying the image cube `ref_images`:
        fig, ax = plt.subplots(1, 1, figsize=(5,5))
        imshow_args = {'vmin':0, 'vmax': 20, 
                       'interpolation': 'nearest',
                       'origin':'lower', #'norm':colors.LogNorm()
                      }
        ax_img = ax.imshow(ref_images[0], **imshow_args)
        ax.set_title(f"Ref Img {0:2d}")

        scroller = cube_scroller(ref_images, fig, ax)
        display(scroller)
    
    Parameters
    ----------
    cube : 3-D numpy array of images
    fig: matplotlib Figure objet
    ax: matplotlib Axis object
    
    Output
    ------
    scroller widget that you can display with `display(scroller)`
    """
    # create the wigdets
    out=widgets.Output()
    play = widgets.Play(
        interval=200, # milliseconds
        value=0,
        min=0,
        max=len(cube)-1,
        step=1,
        description="Img #:",
        disabled=False
    )
    slider = widgets.IntSlider(0, 0, len(cube)-1, description='Img #')
    widgets.jslink((play, 'value'), (slider, 'value'))
    widgets.HBox([play, slider])

    # update the image when the slider changes value
    ax_img = ax.images[0]
    def update(change):
        index = change['new']
        new_img = cube[index]
        ax_img.set_data(new_img)
        ax.set_title(f"Img #{index}")
        fig.canvas.draw_idle()
    slider.observe(update, names='value')

    scroller = widgets.HBox((out, play, slider))
    return scroller
