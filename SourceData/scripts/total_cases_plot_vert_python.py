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


import argparse
import os

import scipy
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.pyplot import figure

from fets_paper_figures import save_at_dpi, font_scale


def main(data_pardir, output_pardir):

    total_cases_df = pd.read_csv(os.path.join(data_pardir, 'total_cases_df.csv'))

    cases_name = 'Cases(total=6,314)'

    BLUE = (0.00392156862745098, 0.45098039215686275, 0.6980392156862745)  # for initial model data holders          
    ORANGE = (0.8705882352941177, 0.5607843137254902, 0.0196078431372549)  # for full federation
    GREEN = (120/255, 1, 0)
    

    ids_for_init_insts = [47, 51, 55, 57, 58, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71]
    ids_for_testing_insts = [8, 11, 19, 20, 21, 43]

    # start by setting all to ORANGE
    id_to_color = {num: ORANGE for num in range(1, 72)}

    # Now define the sites that were used in each role 

    for inst in range(1, 72):
        if inst in ids_for_testing_insts:
            id_to_color[inst] = GREEN
        elif inst in ids_for_init_insts:
            id_to_color[inst] = BLUE



    def show_values(axs, fontsize, shift_x_vals, orient="v", space=.01):
        def _single(ax):
            if orient == "v":
                for p in ax.patches:
                    _x = p.get_x() + p.get_width() / 2
                    _y = p.get_y() + p.get_height() + (p.get_height()*0.01)
                    value = '{}'.format(int(p.get_height()))
                    ax.text(_x, _y, value, ha="center", fontdict={'fontsize': fontsize}) 
            elif orient == "h":
                for p in ax.patches:
                    _x = p.get_x() + p.get_width() + float(space)
                    _y = p.get_y() + p.get_height() - (p.get_height()*0.5)
                    value = '{}'.format(int(p.get_width()))
                    ax.text(_x, _y, str(int(value) + shift_x_vals), ha="left", fontdict={'fontsize': fontsize})

        if isinstance(axs, np.ndarray):
            for idx, ax in np.ndenumerate(axs):
                _single(ax)
        else:
            _single(axs)

            
            
            
    orient='h'
    
    x_shift = 25

    scale_factor=0.00204
    figure(figsize=(1819*scale_factor,9473*scale_factor))

    sns.set(font_scale = font_scale)

    sns.color_palette("colorblind")

    sns.set_style("whitegrid")

    temp_df = total_cases_df.copy()
    temp_df['Cases'] = temp_df['Cases'] + x_shift

    temp_df = temp_df.rename({'Cases': cases_name}, axis=1)

    ax = sns.barplot(y='Site ID', 
                    x=cases_name, 
                    data=temp_df.rename({'Site ID (for paper)': 'Site ID'}, axis=1), 
                    palette=id_to_color.values(), 
                    orient=orient)
    ax.tick_params(labelsize=12)

    ax.xaxis.label.set_size(18)
    ax.yaxis.label.set_size(18)

    show_values(ax, orient=orient, fontsize=12, shift_x_vals=-x_shift)

    fpath = os.path.join(output_pardir, 'total_cases_plot_vert_python.pdf')

    print(f"Saving output file at: {fpath}\n")

    save_at_dpi(fpath=fpath) 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_pardir', '-dp', type=str, help='Absolute path to the data parent directory.', default="../")
    parser.add_argument('--output_pardir', '-op', type=str, help='Absolute path to the output parent directory.', default="../../output")
    args = parser.parse_args()
    main(**vars(args))