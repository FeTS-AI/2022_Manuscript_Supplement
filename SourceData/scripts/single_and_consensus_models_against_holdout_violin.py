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

from fets_paper_figures import prep_plots, my_violin_plot, save_at_dpi, BINARY_DICE, DICE, JACCARD, dice_or_jaccard


def main(data_pardir, output_pardir, jaccard):



    single_models_val_df = pd.read_csv(os.path.join(data_pardir, 'single_models_val_df.csv'))
    consensus_model_results_inhouse_only_df = pd.read_csv(os.path.join(data_pardir, 'consensus_model_results_inhouse_only_df.csv'))

    new_metric_names, metrics, region_label_dict, IN_DF_DICE_OR_JACCARD, DICE_OR_JACCARD = dice_or_jaccard(jaccard)
    

    # Now one that brings in the consensus models (but only tested against inhouse data as that is what was
    # used for the single model scoring)

    # Since this is testing against only a subset of the heldout data, the hatch is 'x'


    prep_plots()


    my_pal = [(0.8705882352941177, 0.5607843137254902, 0.0196078431372549),
            (0.9254901960784314, 0.8823529411764706, 0.2),  
            (0.8, 0.47058823529411764, 0.7372549019607844), 
            (0.792156862745098, 0.5686274509803921, 0.3803921568627451), 
            (0.33725490196078434, 0.7058823529411765, 0.9137254901960784), 
            (0.5803921568627451, 0.5803921568627451, 0.5803921568627451)] 



    consens_sup = consensus_model_results_inhouse_only_df.rename({'Model Type': 'Model Name'}, axis=1)

    consens_sup = consens_sup[consens_sup['Model Name']=='singlet_0'].replace(to_replace='singlet_0', value='Full Federation Consensus')

    temp_df = single_models_val_df.rename({'Single Institution': 'Model Name'}, axis=1).append(consens_sup)

    # forcing correct placement with alphabetic placement
    temp_df = temp_df.replace(to_replace='All single institution ensemble', value='G ensemble')

    temp_df = temp_df.sort_values(by='Model Name')

    # some stdout for the paper
    for metric in ['Average', 'ET', 'TC', 'WT']:
        consens_result = temp_df[(temp_df['Model Name']=='Full Federation Consensus') & (temp_df[BINARY_DICE]==metric)][DICE_OR_JACCARD].mean()
        ensemble_result = temp_df[(temp_df['Model Name']=='G ensemble') & (temp_df[BINARY_DICE]==metric)][DICE_OR_JACCARD].mean()
        print(f"For metric {metric}, the consensus scored {consens_result}, the ensemble scored {ensemble_result}, and the percent increase was {(100 * (ensemble_result/consens_result - 1))}")

        
    # getting p values for comparisons
    pvalues = {'ensemble vs cons': {}}

    sites = ['Site 1', 'Site 2', 'Site 3', 'Site 4']


    pvalues.update({site + ' vs cons': {} for site in sites})

    for metric in temp_df[BINARY_DICE].unique():
        samples_1 = temp_df[(temp_df["Model Name"] == "G ensemble") & (temp_df[BINARY_DICE] == metric)][DICE_OR_JACCARD].values
        samples_2 = temp_df[(temp_df["Model Name"] == 'Full Federation Consensus') & (temp_df[BINARY_DICE] == metric)][DICE_OR_JACCARD].values
        stat, pvalue = scipy.stats.wilcoxon(samples_1, samples_2)
        m1, m2 = np.mean(samples_1), np.mean(samples_2)
        sd1, sd2 = np.std(samples_1), np.std(samples_2)
        pvalues['ensemble vs cons'][metric] = pvalue 
        
    temp_df = temp_df.replace(to_replace='G ensemble', value='Ensemble')
    temp_df = temp_df.replace(to_replace='Institution 42', value='Site 3')
    temp_df = temp_df.replace(to_replace='Institution 43', value='Site 4')
    temp_df = temp_df.replace(to_replace='Institution 44', value='Site 2')
    temp_df = temp_df.replace(to_replace='Institution 46', value='Site 1')


    for site in sites:
        for metric in temp_df[BINARY_DICE].unique():
            samples_1 = temp_df[(temp_df["Model Name"] == site) & 
                                (temp_df[BINARY_DICE] == metric) ][DICE].values
            samples_2 = temp_df[(temp_df["Model Name"] == 'Full Federation Consensus') & (temp_df[BINARY_DICE] == metric)][DICE].values
            stat, pvalue = scipy.stats.wilcoxon(samples_1, samples_2)
            m1, m2 = np.mean(samples_1), np.mean(samples_2)
            sd1, sd2 = np.std(samples_1), np.std(samples_2)
            pvalues[site + ' vs cons'][metric] = pvalue
            
    sorting_dict = {'Full Federation Consensus': 0, 
                    'Ensemble': 1,
                    'Site 1': 2,
                    'Site 2': 3, 
                    'Site 3': 4, 
                    'Site 4': 5, 
                    
        
    }

    base_shift = 0.062
        
        
    ax = my_violin_plot(x_column=BINARY_DICE, 
                    y_column=DICE_OR_JACCARD, 
                    data=temp_df, 
                    hue='Model Name', 
                    order=['Average', 'ET', 'TC', 'WT'], 
                    hatch='x', 
                    mean_marker_size=15, 
                    palette=my_pal,
                    sorting_key= lambda x: x.apply(lambda x: sorting_dict[x]), 
                    group_size=6, 
                    shrink_factor = 0.7, 
                    box_width=0.3,
                    shifts = {0: 3.32*base_shift,   # grey!
                                1: -3.35*base_shift,   # orange! 
                                2: -2.02*base_shift, # yellow!
                                3: -0.72*base_shift,   # purple!
                                4: 0.665*base_shift, # site 2!
                                5: 1.95*base_shift}) # blue!

    # deleting part of legend that comes from the pointplot
    handles, labels = ax.get_legend_handles_labels()
    cut_off = int(len(handles)/2)
    ax.legend(handles=handles[:cut_off] + cut_off*[None], labels=labels[:cut_off] + cut_off*[None])

    ax.set_ylim(top=1.0, bottom=0.0)
    ax.set_title('Centralized Out-Of-Sample Data')

    fpath = os.path.join(output_pardir, 'single_and_consensus_models_against_holdout_violin_' + DICE_OR_JACCARD + '.pdf')

    print(f"Saving output file at: {fpath}")

    save_at_dpi(fpath=fpath)

    print(f"\n\nThe p-values for significance of various model results versus the consensus model results are: ", pvalues)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_pardir', '-dp', type=str, help='Absolute path to the data parent directory.', default="../")
    parser.add_argument('--output_pardir', '-op', type=str, help='Absolute path to the output parent directory.', default="../../output")
    parser.add_argument('--jaccard', '-j', action='store_true', help='Whether or not to convert DICE scores to Jaccard index.')
    args = parser.parse_args()
    main(**vars(args))