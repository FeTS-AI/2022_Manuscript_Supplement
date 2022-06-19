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
import scipy 
import matplotlib.pyplot as plt
import pandas as pd   

from fets_paper_figures import prep_plots, get_comparison_df_detailed, my_violin_plot, interp_MBD_best_round, save_at_dpi
from fets_paper_figures import other_font_size, compute_increases

def main(data_pardir, output_pardir):    
    
    prep_plots()

    df = pd.read_csv(os.path.join(data_pardir, 'val_df_final__.csv'))

    vmodel_score, init_score, restricted_init_score, percent_increase_restricted = compute_increases(model_round=interp_MBD_best_round, df=df)

    spread_version_df, spread_init_df = get_comparison_df_detailed(model_round=interp_MBD_best_round, df=df)

    spread_version_df['Model'] = 'Full Federation Consensus'
    spread_init_df['Model'] = 'Public Initial Model'

    print(spread_version_df)
    print(f"length of spread init df is: {len(spread_init_df)}")
    print(spread_init_df)

    compare_with_restriced_inits_df_details = spread_init_df.append(spread_version_df)

    compare_with_restriced_inits_df_details = compare_with_restriced_inits_df_details.rename({"Binary DICE": "Region Of Interest", 
                                                                                            "DICE": "DSC"}, axis=1)


    my_pal = [(0.00392156862745098, 0.45098039215686275, 0.6980392156862745), 
            (0.8705882352941177, 0.5607843137254902, 0.0196078431372549)]

    # getting p values for comparisons
    pvalues = {}
    for metric in compare_with_restriced_inits_df_details["Region Of Interest"].unique():
        samples_1 = compare_with_restriced_inits_df_details[(compare_with_restriced_inits_df_details["Model"] == "Public Initial Model") & (compare_with_restriced_inits_df_details["Region Of Interest"] == metric)]["DSC"].values
        samples_2 = compare_with_restriced_inits_df_details[(compare_with_restriced_inits_df_details["Model"] == 'Full Federation Consensus') & (compare_with_restriced_inits_df_details["Region Of Interest"] == metric)]["DSC"].values
        min_length = min(len(samples_1), len(samples_2))
        samples_1 = samples_1[:min_length]
        samples_2 = samples_2[:min_length]
        stat, pvalue = scipy.stats.wilcoxon(samples_1, samples_2)
        m1, m2 = np.mean(samples_1), np.mean(samples_2)
        sd1, sd2 = np.std(samples_1), np.std(samples_2)
        pvalues[metric] = pvalue
        
    # get the PIM to appear first
    sorting_key = lambda x: x.apply(lambda x: {'Full Federation Consensus': 1,
                                            'Public Initial Model': 0}[x]
                                )
    compare_with_restriced_inits_df_details = compare_with_restriced_inits_df_details.rename({'Region Of Interest': 'Tumor Sub-Compartment'}, axis=1)                   



    ax = my_violin_plot(x_column='Tumor Sub-Compartment', 
                    y_column='DSC', 
                    hue='Model', 
                    data=compare_with_restriced_inits_df_details, 
                    mean_marker_size=20,
                    palette=my_pal,
                    sorting_key=sorting_key, 
                    order=['Average', 'ET', 'TC', 'WT'], 
                    group_size=2,
                    box_width=0.3,
                    shrink_factor=0.3,
                    shifts={0: 0.1273, 1: -0.1273})

    ax.set(ylim=(0, 1.16))

    ax.set_title('Local Validation Data')

    ax.legend(bbox_to_anchor= (.45, .15))



    vert_text_loc = {'Average': 0.613, 'ET': 0.582, 'TC': 0.578, 'WT': 0.7}

    hor_text_loc = {'Average': 0.105, 'ET': 0.345, 'TC': 0.59, 'WT': 0.825}

    hor_arrow_loc = {'Average': 0.0, 'ET': 1.0, 'TC': 2.0, 'WT': 3.0}

    arrow_length = {'Average': 0.157, 'ET': 0.162, 'TC': 0.198, 'WT': 0.116}

    vert_arrow_loc = {'Average': 0.671, 'ET': 0.638, 'TC': 0.62, 'WT': 0.753}


    # place text boxes
    text_insert = f'{percent_increase_restricted["MeanBinaryDICE"]:.0f}%\nGain'
    print("\nThe percent increase of " + text_insert + " should go with MBD")
    ax.text(hor_text_loc['Average'], vert_text_loc['Average'], text_insert, transform=ax.transAxes, 
            fontsize=other_font_size, 
            color='red',
            verticalalignment='top')
    plt.arrow(x=hor_arrow_loc['Average'], 
                y=vert_arrow_loc['Average'], 
                dx=0, 
                dy=arrow_length['Average'],
                length_includes_head=True, 
                head_width=0.04, 
                head_length=0.03,
                color='red')

    text_insert = f'{percent_increase_restricted["binary_DICE_ET"]:.0f}%\nGain'
    ax.text(hor_text_loc['ET'], vert_text_loc['ET'], text_insert, transform=ax.transAxes, fontsize=other_font_size, color='red',
            verticalalignment='top')
    print("\nThe percent increase of " + text_insert + " should go with ET")
    plt.arrow(x=hor_arrow_loc['ET'], 
                y=vert_arrow_loc['ET'], 
                dx=0, 
                dy=arrow_length['ET'],
                length_includes_head=True, 
                head_width=0.04, 
                head_length=0.03,
                color='red')


    text_insert = f'{percent_increase_restricted["binary_DICE_TC"]:.0f}%\nGain'
    print("\nThe percent increase of " + text_insert + " should go with TC")
    ax.text(hor_text_loc['TC'], vert_text_loc['TC'], text_insert, transform=ax.transAxes, fontsize=other_font_size, color='red',
            verticalalignment='top')
    plt.arrow(x=hor_arrow_loc['TC'], 
                y=vert_arrow_loc['TC'], 
                dx=0, 
                dy=arrow_length['TC'],
                length_includes_head=True, 
                head_width=0.04, 
                head_length=0.03,
                color='red')


    text_insert = f'{percent_increase_restricted["binary_DICE_WT"]:.0f}%\nGain'
    print("\nThe percent increase of " + text_insert + " should go with WT")
    ax.text(hor_text_loc['WT'], vert_text_loc['WT'], text_insert, transform=ax.transAxes, fontsize=other_font_size, color='red',
            verticalalignment='top')
    plt.arrow(x=hor_arrow_loc['WT'], 
                y=vert_arrow_loc['WT'], 
                dx=0, 
                dy=arrow_length['WT'],
                length_includes_head=True, 
                head_width=0.04, 
                head_length=0.03,
                color='red')





    # deleting part of legend that comes from the pointplot
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles[:2] + 2*[None], labels=labels[:2] + 2*[None], loc='lower left')

    ax.set_ylim(top=1.0, bottom=0.0)

    # ax.get_xaxis().set_visible(False)


    print(f"\n\nThe p-values for differences in mean validation over samples between the public initial and final consensus models are: {pvalues}\n\n")

    fpath = os.path.join(output_pardir, 'performance_increase_restricted_init_violin.png')

    print("Saving output file at: ", fpath)

    save_at_dpi(fpath=fpath)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_pardir', '-dp', type=str, help='Absolute path to the data parent directory.', default="../")
    parser.add_argument('--output_pardir', '-op', type=str, help='Absolute path to the output parent directory.', default="../../output")
    args = parser.parse_args()
    main(**vars(args))