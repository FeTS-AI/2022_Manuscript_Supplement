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


import pandas as pd
import matplotlib.pyplot as plt

from .plotting import save_at_dpi, DICE, IN_DF_DICE, IN_DF_JACCARD, JACCARD
import seaborn as sns


def dice_or_jaccard(jaccard):

    if jaccard:
        IN_DF_DICE_OR_JACCARD = IN_DF_JACCARD
        DICE_OR_JACCARD = JACCARD
    else:
        IN_DF_DICE_OR_JACCARD = IN_DF_DICE
        DICE_OR_JACCARD = DICE

    metrics = ['MeanBinary' + IN_DF_DICE_OR_JACCARD, 
               'binary_' + IN_DF_DICE_OR_JACCARD + '_WT', 
               'binary_' + IN_DF_DICE_OR_JACCARD + '_TC', 
               'binary_' + IN_DF_DICE_OR_JACCARD + '_ET'] 


    region_label_dict = {metrics[0]: "Average",
                        metrics[1]: "WT",
                        metrics[2]: "TC", 
                        metrics[3]: "ET"}

    new_metric_names = [region_label_dict[metric] for metric in metrics]

    return new_metric_names, metrics, region_label_dict, IN_DF_DICE_OR_JACCARD, DICE_OR_JACCARD


def spread_metrics_across_rows(df, jaccard):

    new_metric_names, _, region_label_dict, IN_DF_DICE_OR_JACCARD, _ = dice_or_jaccard(jaccard)
    
    temp_df = df.copy()
    
    # convert the metric names to new ones
    temp_df = temp_df.rename(region_label_dict, axis=1)
    
    # restrict to only metric names columns, with model version as the index
    temp_df = temp_df[['ModelVersion'] + new_metric_names].set_index(['ModelVersion'])

    # create two level of columns to put all columns (metrics) under a top level : 'DICE'
    temp_df.columns = pd.MultiIndex.from_tuples([(IN_DF_DICE_OR_JACCARD, metric) for metric in new_metric_names])

    # now stack the dataframe
    final_df = temp_df.stack()
    # Move the model version back out of the index
    final_df = final_df.reset_index()

    # At this point, final_df should have exactly three columns 'ModelVersion', 'level_1', and 'DICE'.
    # The level_1 column will contain the string of which metric applies, and the DICE holds the value.

    # renaming the level_1 column
    final_df = final_df.rename(mapper={'level_1': 'Tumor Sub-Compartment'}, axis=1)
    
    return final_df


def get_comparison_df_detailed (model_round, df, jaccard):

    temp_df = df[df['TaskName']=='shared_model_validation']

    version_df = temp_df[temp_df['ModelVersion']==model_round]
    init_df = temp_df[temp_df['ModelVersion']==0]
    
    print(f"length of init df is {len(init_df)}")
    
    return spread_metrics_across_rows(version_df, jaccard=jaccard), spread_metrics_across_rows(init_df, jaccard=jaccard)


def compute_increases(model_round, df, jaccard):
    
    temp_df = df[df['TaskName']=='shared_model_validation']

    v_df = temp_df[temp_df['ModelVersion']==model_round]
    init_df = temp_df[temp_df['ModelVersion']==0]


    vmodel_score = {}
    init_score = {}
    restricted_init_score = {}
    percent_increase_restricted = {}

    _, metrics, _, _, _ = dice_or_jaccard(jaccard)
    
    for metric in metrics:
        vmodel_score[metric] = v_df[metric].mean()

    valcols = list(v_df['CollaboratorName'].unique())

    for metric in metrics:
        init_score[metric] = init_df[metric].mean()
        restricted_init_score[metric] = init_df[init_df['CollaboratorName'].isin(valcols)][metric].mean()
        percent_increase_restricted[metric] = int(round(100 * (vmodel_score[metric]/restricted_init_score[metric]-1)))
    return  vmodel_score, init_score, restricted_init_score, percent_increase_restricted


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
                                     metric_name_column_name=None, 
                                     model_version_column_name=None):
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
        
    if model_version_column_name is None:
        model_version_column_name = 'ModelVersion' 

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
    
    final_df = final_df.rename({'ModelVersion': model_version_column_name}, axis=1)

    # now ready to plot
    g = sns.lineplot(x=model_version_column_name,
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
    
    if fpath is None:
        raise ValueError('No output will be produced since fpath is None.')
    else:
        print("Saving output file to: ", fpath)
        save_at_dpi(fpath)



def aggregated_fine_grained_binary_dice_over_rounds(df, 
                                                    task, 
                                                    show_envelope=False, 
                                                    fpath=None, 
                                                    no_title=False,
                                                    custom_title=None,
                                                    metric_name_column_name=None, 
                                                    metric_value_column_name=None, 
                                                    model_version_column_name=None, 
                                                    metric_names=['binary_DICE_ET', 'binary_DICE_TC', 'binary_DICE_WT']): 
    """
    Three plots (possibly with envelopes) (one for each region et, tc, wt) for a given task of binary dice 
    scores over rounds.
    """
    
    if metric_name_column_name is not None:
        metric_names = ['ET', 'TC', 'WT']
        
    if model_version_column_name is None:
        model_version_column_name = 'ModelVersion'

    if show_envelope:
        curvepermetric_value_over_rounds(df=df, 
                                         metric_names=metric_names,
                                         task=task,
                                         fpath=fpath, 
                                         no_title=no_title, 
                                         metric_name_column_name=metric_name_column_name, 
                                         metric_value_column_name=metric_value_column_name, 
                                         custom_title=custom_title, 
                                         model_version_column_name=model_version_column_name)
    else:
        temp_df = df.groupby(['ModelVersion', 'TaskName'])[metric_names].mean().reset_index()
        curvepermetric_value_over_rounds(df=temp_df, 
                                         metric_names=metric_names,
                                         task=task,
                                         fpath=fpath, 
                                         no_title=no_title, 
                                         metric_name_column_name=metric_name_column_name, 
                                         metric_value_column_name=metric_value_column_name, 
                                         custom_title=custom_title, 
                                         model_version_column_name=model_version_column_name)
