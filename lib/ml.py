import os
import stat
import yaml
import pandas as pd
import plotly.express as px

from itertools import product
from rich import print as rprint
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from src.utils import get_project_root
root = get_project_root()

def classify_df(df, ow=False, debug=False):
    # Find the peaks of the Amplitude distribution for each set, OV and Channel
    numbers = df['Number'].unique()
    labels = df['Set'].unique()
    ovs = df['OV'].unique()
    chs = df['Channel'].unique()

    peaks = generate_yaml(df, 'peak', ow=ow, debug=debug)
    score = generate_yaml(df, 'score', ow=ow, debug=debug)
    clusters = generate_yaml(df, 'clusters', ow=ow, debug=debug)
    
    df['Cluster'] = -1

    for n, label, ov, ch in product(numbers, labels, ovs, chs):
        data = df[(df['Number'] == n) & (df['Set'] == label) & (df['OV'] == ov) & (df['Channel'] == ch)]
        # Skip if there are no data
        if len(data) == 0:
            if debug: rprint(f"No data for {n} {label} {ov} {ch}")
            continue
        # Check if the peak has already been found
        if peaks[int(n)][str(label)][int(ov)][int(ch)] is not None and ow is False:
            if debug: rprint(f"Peak for {n} {label} {ov} {ch} already found")
            continue
        # Find the peaks of the Amplitude distribution by finding the cluster centers but iterate over the number of clusters to find the best number of clusters
        for i in range(2,10):
            kmeans = KMeans(n_clusters=i, random_state=0).fit(data['Amplitude'].values.reshape(-1,1))
            prev_score = -1
            this_score = silhouette_score(data['Amplitude'].values.reshape(-1,1), kmeans.labels_)
            if this_score > prev_score:
                score[int(n)][str(label)][int(ov)][int(ch)] = float(this_score)
                peaks[int(n)][str(label)][int(ov)][int(ch)] = kmeans.cluster_centers_.tolist()
                clusters[int(n)][str(label)][int(ov)][int(ch)] = kmeans.labels_.tolist()    
                prev_score = this_score
        
        if debug: rprint(f"Best number of clusters for {n} {label} {ov} {ch} is {i} with a silhouette score of {score[int(n)][str(label)][int(ov)][int(ch)]}")
        df.loc[(df['Number'] == n) & (df['Set'] == label) & (df['OV'] == ov) & (df['Channel'] == ch), 'Cluster'] = kmeans.labels_

    save_yaml(peaks, 'peak', debug=debug)
    save_yaml(score, 'score', debug=debug)
    save_yaml(clusters, 'clusters', debug=debug)
    return df


def generate_yaml(df:pd.DataFrame, name:str, path:str=f'{root}/data/analysis/', ow:bool=False, debug:bool=False):
    # Check if path exists
    if not os.path.exists(path):
        os.makedirs(path)
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    # First check if the dictionary already exists
    try:
        data = yaml.load(open(f'{path}{name}.yml'),Loader=yaml.FullLoader)
    except FileNotFoundError:
        data = {}
    
    numbers = df['Number'].unique()
    labels = df['Set'].unique()
    ovs = df['OV'].unique()
    chs = df['Channel'].unique()
    # Only create the non existing branches of the dictionary
    for n in numbers:
        n = int(n)
        if data.get(n, None) is None:
            data[n] = {}
        for label in labels:
            label = str(label)
            if data[n].get(label, None) is None:
                data[n][label] = {}
            for ov in ovs:
                ov = int(ov)
                if data[n][label].get(ov, None) is None:
                    data[n][label][ov] = {}
                for ch in chs:
                    ch = int(ch)
                    if data[n][label][ov].get(ch, None) is None or ow is True:
                        data[n][label][ov][ch] = None
    if debug: rprint(f'{name} dictionary updated with {numbers} {labels} {ovs} {chs}')
    return data


def save_yaml(data:dict, name:str, path:str=f'{root}/data/analysis/', debug:bool=False) -> None:
    # Save the data
    with open(f'{path}{name}.yml', 'w') as file:
        yaml.dump(data, file)
    os.chmod(f'{path}{name}.yml', stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    if debug: rprint(f'{name} dictionary saved in {path}{name}.yml')
    return