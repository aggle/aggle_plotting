"""
Use ipywidgets to scroll through a datacube
Use with %matplotlib notebook
"""
from pathlib import Path
import numpy as np
import pandas as pd

import functools

import yaml
import bokeh
import bokeh.transform as bktrans
import bokeh.layouts as bklyts
import bokeh.plotting as bkplt
import bokeh.io as bkio
import bokeh.models as bkmdls

#from bokeh.models import ColumnDataSource, Slider, ColorBar, LogColorMapper
from bokeh.plotting import figure
from bokeh.themes import Theme
from bokeh.themes import built_in_themes
from bokeh.io import show, output_notebook, output_file

import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output


def standalone_app(func):
    """
    Take a method that returns a bokeh layout and return it as an app that can be displayed with bkplt.show()
    """
    @functools.wraps(func)
    def appwrap(*args, **kwargs):
        # wrap the layout-producing func in a bokeh app
        def app(doc):
            layout = func(*args, **kwargs)

            doc.add_root(layout)

            doc.theme = Theme(json=yaml.load("""
                attrs:
                    figure:
                        background_fill_color: white
                        outline_line_color: white
                        toolbar_location: above
                        height: 500
                        width: 800
                    Grid:
                        grid_line_dash: [6, 4]
                        grid_line_color: white
            """, Loader=yaml.FullLoader))
        return app
    return appwrap

def cube_scroller_plot_slider(
        cube : pd.Series,
        title : str = '',
        scroll_title='',
        cmap_class=bkmdls.LinearColorMapper,
        info_col : pd.Series | None = None,
        plot_size : int = 400
):
    """
    This is called by cube_scroller_app()
    Generate the plot and scroller objects for a cube_scroller application.
    Separating it out this way makes it easier to add multiple cube scrollers
    to the same figure.

    Parameters
    ----------
    cube : pd.Series
      pandas.Series object whose entries are arrays
    title : str
      title to put on the plot
    scroll_title : str ['']
      title for the scroll bar
    cmap_class : bokeh.models.ColorMapper class [bkmdls.LinearColorMapper]
      a color mapper for scaling the images
    info_col : pd.Series | None
      extra info to add to plot. Must have same index as `cube`
    Output
    ------
    bokeh figure, slider widget, and the that stores the data
    """
    TOOLS='save'

    if not isinstance(cube, pd.Series):
        cube = pd.Series({i: j for i, j in enumerate(cube)})

    data = cube[cube.map(lambda el: ~np.isnan(el).all())].copy()
    # initialize image
    img = data[data.index[0]]
    cds = bkmdls.ColumnDataSource(data={'image':[img],
                                        'x': [-0.5], 'y': [-0.5],
                                        'dw': [img.shape[0]], 'dh': [img.shape[1]]
                                        }
                                  )
    low, high = np.nanmin(img), np.nanmax(img)
    color_mapper = cmap_class(palette='Magma256',
                              low=low,
                              high=high)

    plot = figure(title=f"{title}",
                  min_height=plot_size, min_width=plot_size,
                  # aspect_ratio=1,
                  tools=TOOLS)
    g = plot.image(image='image',
                   x='x', y='y',
                   dw='dw', dh='dh',
                   color_mapper=color_mapper,
                   source=cds)
    # Hover tool
    hover_tool = bkmdls.HoverTool()
    hover_tool.tooltips=[("value", "@image"),
                         ("(x,y)", "($x{0}, $y{0})")]
    plot.add_tools(hover_tool)
    plot.toolbar.active_inspect = None

    # color bar
    color_bar = bkmdls.ColorBar(color_mapper=color_mapper, label_standoff=12)
    plot.add_layout(color_bar, 'right')

    # slider
    # lambda function to generate the extra information string
    info_str = lambda index: '' if info_col is None else f"{info_col.name} = {info_col.iloc[index]}"
    slider_title = lambda title, index, info='': f"{title} :: {index} / {info}"
    slider = bkmdls.Slider(start=0, end=data.index.size-1, value=0, step=1,
                           title=slider_title(scroll_title, data.index[0], info_str(0)),
                           show_value = False,
                           # default_size=plot_size,
                           orientation='horizontal')
    def callback(attr, old, new):
        # update the image
        img = data[data.index[new]]
        cds.data['image'] = [img]
        color_mapper.update(low=np.nanmin(img), high=np.nanmax(img))
        slider.title = slider_title(scroll_title, data.index[new], info_str(new))
    slider.on_change('value', callback)

    # Switch color map
    menu = {"Linear": bkmdls.LinearColorMapper, "Log": bkmdls.LogColorMapper}
    cmap_switcher = bkmdls.Select(title='Switch color map',
                                  value=sorted(menu.keys())[0],
                                  width=plot_size,
                                  options=sorted(menu.keys()))
    def cmap_switcher_callback(attr, old, new):
        cmap_class = menu[new]
        color_mapper = cmap_class(palette='Magma256',
                                  low=np.nanmin(img),
                                  high=np.nanmax(img))
        # update the color mapper on image
        g.glyph.color_mapper=color_mapper
    cmap_switcher.on_change('value', cmap_switcher_callback)

    widgets = bklyts.column(slider, cmap_switcher, sizing_mode='scale_width')
    return bklyts.column(plot, widgets)

# standalone version
cube_scroller_app = standalone_app(cube_scroller_plot_slider)

# first, let's make a generic helper function to generate figures that scroll through cubes
# version without bokeh
def cube_scroller_nobokeh(cube, fig, ax):
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
        print('fart')
        index = change['new']
        print(index)
        new_img = cube[index]
        ax_img.set_data(new_img)
        ax.set_title(f"Img #{index}")
        fig.canvas.draw_idle()
    slider.observe(update, names='value')

    scroller = widgets.HBox((out, play, slider))
    return scroller
