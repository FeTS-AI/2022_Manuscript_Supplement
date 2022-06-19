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

from fets_paper_figures import prep_plots, curvepermetric_value_over_rounds    



def main(data_pardir, output_pardir):    
    
    # Curve showing that the DICE was generally higher for larger regions: WT > ET > TC

    df = pd.read_csv(os.path.join(data_pardir, 'val_df_final__.csv'))

    prep_plots()

    temp_df = df.rename({'binary_DICE_ET': 'ET', 
                        'binary_DICE_TC': 'TC', 
                        'binary_DICE_WT': 'WT'}, axis=1)

    temp_df = temp_df.rename({"Binary DICE": "Region Of Interest"}, axis=1)
    temp_df = temp_df.rename({"DICE": "DSC"}, axis=1)



    curvepermetric_value_over_rounds(df=temp_df, 
                                    metric_names=['WT', 'ET', 'TC'],
                                    task='shared_model_validation',
                                    xmin=0,
                                    ymin=0.6, 
                                    ymax=0.9, 
                                    fpath=os.path.join(output_pardir, 'dice_better_on_larger_regions.png'), 
                                    custom_title='Mean Local Validation Across Sites', 
                                    metric_value_column_name='DSC', 
                                    metric_name_column_name='Region Of Interest')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_pardir', '-dp', type=str, help='Absolute path to the data parent directory.', default="../")
    parser.add_argument('--output_pardir', '-op', type=str, help='Absolute path to the output parent directory.', default="../../output")
    args = parser.parse_args()
    main(**vars(args))