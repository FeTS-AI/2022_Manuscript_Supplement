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

import pandas as pd
import os

def main(data_pardir):

    percent_increases_df = pd.read_csv(os.path.join(data_pardir, 'p_value_for_singlet_and_triplet_pairs_PLUS.csv'))
    print(percent_increases_df)
    print(percent_increases_df.to_latex())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_pardir', '-dp', type=str, help='Absolute path to the data parent directory.', default="../data")
    args = parser.parse_args()
    main(**vars(args))