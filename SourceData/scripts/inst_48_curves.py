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
import pandas as pd

from fets_paper_figures import prep_plots, aggregated_fine_grained_binary_dice_over_rounds, dice_or_jaccard
    

def main(data_pardir, output_pardir, jaccard):
    # This function produces a validation curve for institution 48

    new_metric_names, metrics, region_label_dict, IN_DF_DICE_OR_JACCARD, DICE_OR_JACCARD = dice_or_jaccard(jaccard)
 

    df = pd.read_csv(os.path.join(data_pardir, 'val_df_final.csv'))    
    prep_plots()


    temp_df = df[df['CollaboratorName']=='institution_11']
    
    temp_df = temp_df.drop(['binary_DICE_ET', 'binary_DICE_TC', 'binary_DICE_WT'], axis=1)

    temp_df = temp_df.rename(region_label_dict, axis=1)

    temp_df = temp_df.rename({"Binary DICE": "Tumor Sub-Compartment", 
                            IN_DF_DICE_OR_JACCARD: DICE_OR_JACCARD}, axis=1)

    fpath = os.path.join(output_pardir, 'inst_48_curves_' + DICE_OR_JACCARD + '.pdf')

    aggregated_fine_grained_binary_dice_over_rounds(df=temp_df, 
                                                    task='shared_model_validation', 
                                                    show_envelope=True, 
                                                    fpath=fpath, 
                                                    no_title=False, 
                                                    metric_name_column_name='Tumor Sub-Compartment', 
                                                    metric_value_column_name=DICE_OR_JACCARD, 
                                                    custom_title='Local Validation For Site 48', 
                                                    model_version_column_name='FL Training Round', 
                                                    metric_names=metrics)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_pardir', '-dp', type=str, help='Absolute path to the data parent directory.', default="../")
    parser.add_argument('--output_pardir', '-op', type=str, help='Absolute path to the output parent directory.', default="../../output")
    parser.add_argument('--jaccard', '-j', action='store_true', help='Whether or not to convert DICE scores to Jaccard index.')  
    args = parser.parse_args()
    main(**vars(args))