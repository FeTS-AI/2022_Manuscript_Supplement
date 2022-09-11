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


import argparse, os
import pandas as pd

from fets_paper_figures import JACCARD, IN_DF_JACCARD, DICE, IN_DF_DICE


def main(data_pardir, jaccard):
    if jaccard:
        sing_trip_results = pd.read_csv(os.path.join(data_pardir, 'singlet_and_triplet_jaccard_scores.csv'))
    else:   
        sing_trip_results = pd.read_csv(os.path.join(data_pardir, 'singlet_and_triplet_dice_scores.csv'))
        
    print(sing_trip_results.style.to_latex())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_pardir', '-dp', type=str, help='Absolute path to the data parent directory.', default="../")
    parser.add_argument('--jaccard', '-j', action='store_true', help='Whether or not to convert DICE scores to Jaccard index.')
    
    args = parser.parse_args()
    main(**vars(args))