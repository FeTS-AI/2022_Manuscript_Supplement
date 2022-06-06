# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import pickle as pkl
import os
import pandas as pd
import numpy as np

from numpy import mean

import seaborn as sns
import scipy

from matplotlib.pyplot import figure
import matplotlib.pyplot as plt
import matplotlib

from matplotlib.patches import PathPatch

font_scale = 2.5
scatter_plot_pointsize = 160
mean_marker_edge_color='red'
mean_marker_fill_color='red'
mean_marker_size = 30

other_font_size = 28

# Naming
BINARY_DICE = 'Tumor Sub-Compartment'
DICE = 'DSC'

value_label = 'Total Cases(train and val)'

interp_MBD_best_round = 52




def adjust_boxes(ax, shrink_factor, shifts, group_size):
    """
    Adjust the widths of a seaborn-generated boxplot.
    """
    
    for num in range(group_size):
        if num not in shifts.keys():
            raise ValueError("The shifts dictionary must contain keys for all residuals in range(group_size).")
    
    count = 0

    # iterating through axes artists:
    for c in ax.get_children():

        # searching for PathPatches
        if isinstance(c, PathPatch):
            
            count += 1
            
            residual = count % group_size
            shift = shifts[residual]
            
            # getting current width of box:
            p = c.get_path()
            verts = p.vertices
            verts_sub = verts[:-1]
            xmin = np.min(verts_sub[:, 0])
            xmax = np.max(verts_sub[:, 0])
            xmid = 0.5*(xmin+xmax)
            xhalf = 0.5*(xmax - xmin)
            
            # print(f"\nGot an xmid of: {xmid}\n")
            
            # setting new width of box
            xmin_new = xmid-shrink_factor*xhalf + shift
            xmax_new = xmid+shrink_factor*xhalf + shift
            verts_sub[verts_sub[:, 0] == xmin, 0] = xmin_new
            verts_sub[verts_sub[:, 0] == xmax, 0] = xmax_new

            # setting new width of median line
            for l in ax.lines:
                l_pos = l.get_xdata()
                if (len(l_pos) == 2) and ((l_pos[0] + l_pos[1]) / 2.0 == xmid):
                    if l_pos[0] == xmin:
                        l.set_xdata([xmin_new, xmax_new])
                    else:
                        l.set_xdata([l_pos[0] + shift, l_pos[1] + shift])
                elif np.all(l_pos == [xmid]):
                    l.set_xdata([xmid + shift])
                    
    return ax
                    

def prep_plots(font_scale=font_scale, scatter_plot_pointsize=scatter_plot_pointsize):
    
    figure(figsize=(16.1,10))

    sns.set(font_scale = font_scale)

    sns.color_palette("colorblind")
    
    sns.set_style("whitegrid")
    
    plt.tight_layout()
    
    
def my_violin_plot(x_column, 
                   y_column, 
                   data,
                   group_size,
                   shrink_factor,
                   shifts, 
                   box_width,
                   hatch=None, 
                   mean_marker_size=mean_marker_size, 
                   hue=None, 
                   sorting_key= lambda x: x.apply(lambda x: x), 
                   **kwargs):
    
    prep_plots()
    
    if hue == None:
        groups = [x_column]
    else:
        groups = [x_column, hue]
        kwargs.update({'hue': hue})
        
    data = data.sort_values(by=hue, key=sorting_key)
    
    ax = sns.violinplot(x=x_column, 
                        y=y_column, 
                        data=data,
                        inner=None, 
                        linewidth=0, 
                        saturation=0.5,
                        cut=0,
                        **kwargs)
    
    handles, labels = ax.get_legend_handles_labels()
    
    
    for _item in ax.get_children():
        if isinstance(_item, matplotlib.collections.PolyCollection):
            if hatch is not None:
                _item.set_hatch(hatch)
            _item.set_alpha(0.5)
    for patch in handles:
        patch.set(hatch = hatch)
        patch.set_alpha(0.5)
    
    ax = sns.boxplot(data=data, 
                x=x_column, 
                y=y_column,
                showmeans=True,
                width=box_width,
                meanprops=dict(marker='x',
                               markeredgecolor='red',
                               markersize=mean_marker_size, 
                               markeredgewidth=4),
                medianprops=dict(color="w", linewidth=4),
                ax=ax, 
                **kwargs)
    
            
    ax = adjust_boxes(ax, 
                      shrink_factor=shrink_factor, 
                      group_size=group_size, 
                      shifts=shifts)


    return ax


def curvepermetric_value_over_rounds(df, 
                                     metric_names,
                                     task,
                                     xmin=0,
                                     ymin=0.0, 
                                     ymax=1.0, 
                                     fpath=None, 
                                     custom_title=None, 
                                     no_title=False, 
                                     metric_value_column_name=None, 
                                     metric_name_column_name=None):
    """
    Lineplot metric value for a given task over rounds, a separate curve for each of a list of metrics sharing 
    a common range (hue for each). 
    ASSUMPTIONS:
    -All metrics (in metric_names) are columns of df
    """

    temp_df = df[df['TaskName']==task].copy()
    max_rounds = temp_df['ModelVersion'].max()
    
    if metric_value_column_name is not None:
        new_value_column_name = metric_value_column_name
    else:
        new_value_column_name = 'MetricValue'
        
    if metric_name_column_name is not None:
        new_name_column_name = metric_name_column_name
    else:
        new_name_column_name = 'MetricType'

    # sanity check assumptions listed above
    if not set(metric_names).issubset(set(list(temp_df.columns))):
        raise ValueError('Some of the provided metric names are not columns of the provided dataferame.')
    
    # restrict to only metric names columns, with model version as the index
    temp_df = temp_df[['ModelVersion'] + metric_names].set_index(['ModelVersion'])

    # create two level of columns to put all columns (metrics) under a top level : 'MetricValue'
    temp_df.columns = pd.MultiIndex.from_tuples([(new_value_column_name, metric_name) for metric_name in metric_names])

    # now stack the dataframe
    final_df = temp_df.stack()
    # Move the model version back out of the index
    final_df = final_df.reset_index()

    # At this point, final_df should have exactly three columns 'ModelVersion', 'level_1', and 'MetricValue'.
    # The level_1 column will contain the string of which metric applies, and the MetricValue holds the value.

    # renaming the level_1 column
    final_df = final_df.rename(mapper={'level_1': new_name_column_name}, axis=1)
    
    final_df = final_df.rename({'ModelVersion': 'FL Training Round'}, axis=1)
    
    
    # now ready to plot
    g = sns.lineplot(x='FL Training Round',
                     y=new_value_column_name,
                     hue=new_name_column_name,
                     data=final_df)
    g.set(xlim=(xmin,max_rounds), ylim=(ymin, ymax))
    if custom_title is None:
        title = "{} Value over Rounds for each ".format(task) + new_name_column_name
    else:
        title = custom_title
        
    if not no_title:
        plt.title(title)
    print("Saving output file at: ", fpath)
    save_at_dpi(fpath)


    



def save_at_dpi(fpath, dpi=600, **kwargs):
    plt.savefig(fpath, dpi=dpi, bbox_inches='tight', **kwargs)




