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
import scipy

from fets_paper_figures import prep_plots, save_at_dpi, my_violin_plot, BINARY_DICE, DICE


def main(data_pardir, output_pardir):

    # Now combine the initial model with the prelim fed consensus model with the main fed consensus (singlet_0) both restricted to inhouse cases
    # prelim consensus were already only evaluated against the inhouse heldout data


    # Since this is tested against a subset of the hold-out data, we use hatch='x'

    prelim_consensus_df = pd.read_csv(os.path.join(data_pardir, 'prelim_consensus_df.csv'))
    init_val_inhouse_only_df = pd.read_csv(os.path.join(data_pardir, 'init_val_inhouse_only_df.csv'))
    single_models_val_df = pd.read_csv(os.path.join(data_pardir, 'single_models_val_df.csv'))
    consensus_model_results_inhouse_only_df = pd.read_csv(os.path.join(data_pardir, 'consensus_model_results_inhouse_only_df.csv'))

    prep_plots()

    first_sup_df = init_val_inhouse_only_df.replace(to_replace='initial', value='Public Initial Model')

    temp_df = first_sup_df.append(prelim_consensus_df.replace(to_replace='Preliminary federation consensus', value='Preliminary Federation Consensus')).append(consensus_model_results_inhouse_only_df[consensus_model_results_inhouse_only_df['Model Type']=='singlet_0'].replace(to_replace='singlet_0', value='Full Federation Consensus'))

    # append ensemble

    supplement_df = single_models_val_df[single_models_val_df['Model Type']=='ensemble']
    temp_df = temp_df.append(supplement_df.replace(to_replace='ensemble', value='Ensemble'))

    prelim_fed_fig_sorting_dict = {'Public Initial Model': 0, 
                                'Ensemble': 4,
                                'Preliminary Federation Consensus': 2, 
                                'Full Federation Consensus': 3}

    fed_samples = {"Preliminary Federation Consensus": {}, 
                "Full Federation Consensus": {}}

    # getting p values for comparisons
    pvalues = {"init vs Preliminary federation consensus": {}, 
            "init vs Full federation consensus": {}, 
            "Preliminary consens vs full consens": {}}
    for model_type in [("Preliminary Federation Consensus", "init vs Preliminary federation consensus"), 
                    ("Full Federation Consensus", "init vs Full federation consensus")]:
        for metric in init_val_inhouse_only_df[BINARY_DICE].unique():
            samples_1 = temp_df[(temp_df["Model Type"] == "Public Initial Model") & (temp_df[BINARY_DICE] == metric)][DICE].values
            samples_2 = temp_df[(temp_df["Model Type"] == model_type[0]) & (temp_df[BINARY_DICE] == metric)][DICE].values
            stat, pvalue = scipy.stats.wilcoxon(samples_1, samples_2)
            m1, m2 = np.mean(samples_1), np.mean(samples_2)
            sd1, sd2 = np.std(samples_1), np.std(samples_2)
            pvalues[model_type[1]][metric] = pvalue
            
            fed_samples[model_type[0]][metric] = samples_2.copy()
            
            
    for metric in init_val_inhouse_only_df[BINARY_DICE].unique():
        stat, pvalue = scipy.stats.wilcoxon(fed_samples["Preliminary Federation Consensus"][metric], 
                                            fed_samples["Full Federation Consensus"][metric])        
        pvalues["Preliminary consens vs full consens"][metric] = pvalue       
            
            
            
    my_pal = [(0.00392156862745098, 0.45098039215686275, 0.6980392156862745),
            (0.984313725490196, 0.6862745098039216, 0.8941176470588236),
            (0.8705882352941177, 0.5607843137254902, 0.0196078431372549), 
            (0.9254901960784314, 0.8823529411764706, 0.2)] 


    ax = my_violin_plot(x_column=BINARY_DICE, 
                    y_column=DICE, 
                    data=temp_df, 
                    hue='Model Type', 
                    order=['Average', 'ET', 'TC', 'WT'], 
                    hatch='x', 
                    mean_marker_size=15, 
                    palette=my_pal, 
                    sorting_key=lambda x: x.apply(lambda x: prelim_fed_fig_sorting_dict[x]), 
                        group_size=4, 
                        shrink_factor=0.7, 
                        shifts={0: 0.1855,  #  brown
                                1: -0.1875,    #  blue
                                2: -0.065,   # grey  
                                3: 0.06},# green 
                        box_width=0.3)

    # deleting part of legend that comes from the pointplot
    handles, labels = ax.get_legend_handles_labels()
    cut_off = int(len(handles)/2)
    ax.legend(handles=handles[:cut_off] + cut_off*[None], labels=labels[:cut_off] + cut_off*[None])


    ax.set_title('Centralized Out-Of-Sample Data')

    ax.set_ylim(top=1.0, bottom=0)

    fpath = os.path.join(output_pardir, 'prelim_and_full_consens_and_initial_against_holdout_reg_scale_violin.pdf')

    print(f"Saving output file at: {fpath}\n")

    save_at_dpi(fpath=fpath)

    print(f"\n\nThe pvalues for mean over sample performance between various model pairs is: {pvalues}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_pardir', '-dp', type=str, help='Absolute path to the data parent directory.', default="../")
    parser.add_argument('--output_pardir', '-op', type=str, help='Absolute path to the output parent directory.', default="../../output")
    args = parser.parse_args()
    main(**vars(args))