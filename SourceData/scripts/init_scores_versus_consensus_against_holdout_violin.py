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
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy

from fets_paper_figures import BINARY_DICE, DICE, my_violin_plot, prep_plots, other_font_size
from fets_paper_figures import save_at_dpi

def main(data_pardir, output_pardir):

    

    final_consensus_val_df = pd.read_csv(os.path.join(data_pardir, 'final_consensus_val_df.csv'))
    init_val_df = pd.read_csv(os.path.join(data_pardir, 'init_val_df.csv'))


    percent_increases = {}


    for binary_dice in ['Average', 'ET', 'TC', 'WT']:
        init_score = init_val_df.groupby([BINARY_DICE]).mean().loc[binary_dice][DICE]
        con_score = final_consensus_val_df.groupby([BINARY_DICE]).mean().loc[binary_dice][DICE]
        percent_increases[binary_dice] = 100 * (con_score/init_score - 1)
        
    prep_plots()    

    temp_df = final_consensus_val_df.sort_values(by=BINARY_DICE)

    temp_df = temp_df.replace(to_replace='binary_DICE_ET', value='ET')
    temp_df = temp_df.replace(to_replace='binary_DICE_TC', value='TC')
    temp_df = temp_df.replace(to_replace='binary_DICE_WT', value='WT')

    temp_df = temp_df.append(init_val_df)

    temp_df = temp_df.sort_values(BINARY_DICE)

    temp_df = temp_df.replace(to_replace='initial', value='Public Initial Model')
    temp_df = temp_df.replace(to_replace='singlet_0', value='Full Federation Consensus').sort_values(by=BINARY_DICE)

    my_pal = [(0.00392156862745098, 0.45098039215686275, 0.6980392156862745), 
            (0.8705882352941177, 0.5607843137254902, 0.0196078431372549)]

    box_shifts={0: 0.1273, 1: -0.1273}
    meanline_shifts = {0: 0.5, 1: -0.5 }

    # getting p values for comparisons
    pvalues = {}
    for metric in temp_df[BINARY_DICE].unique():
        samples_1 = temp_df[(temp_df["Model Type"] == "Public Initial Model") & (temp_df[BINARY_DICE] == metric)][DICE].values
        samples_2 = temp_df[(temp_df["Model Type"] == 'Full Federation Consensus') & (temp_df[BINARY_DICE] == metric)][DICE].values
        if len(samples_1) != len(samples_2):
            print("lengths of samples_1 and samples_2 are: ", len(samples_1), len(samples_2))
        stat, pvalue = scipy.stats.wilcoxon(samples_1, samples_2)
        m1, m2 = np.mean(samples_1), np.mean(samples_2)
        sd1, sd2 = np.std(samples_1), np.std(samples_2)
        pvalues[metric] = pvalue 


        
    ax = my_violin_plot(x_column=BINARY_DICE, 
                    y_column=DICE, 
                    data=temp_df, 
                    hue='Model Type', 
                    hatch='/', 
                    mean_marker_size=20, 
                    palette=my_pal,
                    sorting_key= lambda x: x.apply(lambda x: {"Public Initial Model": 0, 
                                                        "Full Federation Consensus": 1}[x]), 
                    order=['Average', 'ET', 'TC', 'WT'],
                    shrink_factor=0.3,
                    group_size=2, 
                    box_width=0.3,
                    shifts=box_shifts)

    ax.set(ylim=(0, 1.16))

    ax.legend(bbox_to_anchor= (.53, .10))

    ax.set_title("Out-Of-Sample Data")



    meanline_length = 0.35

    vert_text_loc = {'Average': 0.58, 'ET': 0.54, 'TC': 0.53, 'WT': 0.675}

    hor_text_loc = {'Average': 0.095, 'ET': 0.34, 'TC': 0.58, 'WT': 0.82}

    hor_arrow_loc = {'Average': 0.0, 'ET': 1.0, 'TC': 2.0, 'WT': 3.0}

    arrow_length = {'Average': 0.118, 'ET': 0.083, 'TC': 0.144, 'WT': 0.11}

    vert_arrow_loc = {'Average': 0.625, 'ET': 0.598, 'TC': 0.568, 'WT': 0.726}

    vert_meanline_loc = {'Average': {0: 0.631, 1: 0.7}, 
                        'ET': {0: 0.598, 1: 0.7}, 
                        'TC': {0: 0.568, 1: 0.7}, 
                        'WT': {0: 0.726, 1: 0.8}}
    hor_meanline_loc = {'Average': {0: (-0.73 + meanline_length), 1: (-0.3 + meanline_length)}, 
                        'ET': {0: 0.8, 1: 1.2}, 
                        'TC': {0: 1.8, 1: 2.2}, 
                        'WT': {0: 2.8, 1: 3.2}}


    for binary_dice in ['Average', 'ET', 'TC', 'WT']:
        text_insert = f'{percent_increases[binary_dice]:.0f}%\nGain'
        ax.text(hor_text_loc[binary_dice], 
                vert_text_loc[binary_dice], 
                text_insert, 
                transform=ax.transAxes, 
                fontsize=other_font_size, 
                color='red',
                verticalalignment='top')
        
    
        plt.arrow(x=hor_arrow_loc[binary_dice], 
                y=vert_arrow_loc[binary_dice], 
                dx=0, 
                dy=arrow_length[binary_dice],
                length_includes_head=True, 
                head_width=0.04, 
                head_length=0.03,
                color='red')

        ax.set_ylim(top=1.0, bottom=0.0)

    handles, labels = ax.get_legend_handles_labels()
    cut = int(len(handles)/2)
    ax.legend(handles=handles[:cut] + cut*[None], labels=labels[:cut]+cut*[None], loc='lower left')

    fpath = os.path.join(output_pardir, 'init_scores_versus_consensus_against_holdout_violin.png')

    print(f"\nThe p-values for each tumor region of the difference in the means between the public initial model and the final consensus are: {pvalues}\n\n")
    print("Saving output file at: ", fpath)
    save_at_dpi(fpath=fpath)



    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_pardir', '-dp', type=str, help='Absolute path to the data parent directory.', default="../data")
    parser.add_argument('--output_pardir', '-op', type=str, help='Absolute path to the output parent directory.', default="../output")
    args = parser.parse_args()
    main(**vars(args))

