# aggle_plotting
Matplotlib styles for plotting

## Installation
From the directory `aggle_plotting`, you can run `pip install .`. This will install a package named `agplot` into your current python environment. You can then import it as `import agplot`. 

## Usage
The `styles/` folder contains `*.mplstyle` files that are basically stripped-down `.matplotlibrc` files containing only the changes from default values. 
The `styles` module contains functions that call one of the files to set the matplotlib environment. For example, `agplot.styles.notebook_style()` calls the function `plt.style.use("styles/notebook.mplstyle")`, setting the matplotlib RC parameters. 

## Development
To extend this package, modify an exisiting `.mplstyle` file or create a new one, and a corresponding calling function in `styles.py`
