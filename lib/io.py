import os
import yaml
import stat
import glob
import pandas as pd

from itertools import product
from rich import print as rprint

from src.utils import get_project_root
root = get_project_root()

def load_files(path:str) -> list:
    file_list = glob.glob(path)
    print('Reading files in :'+path+'...')
    print('Found {} files'.format(len(file_list)))
    if len(file_list)==0:
        print("No files found, exiting...")
        return []
    return file_list

def load_data(numbers:list,labels:list,ovs:list,chs:list,path:str=f'{root}/analysis',debug:bool=False):
    return load_df('',numbers,labels,ovs,chs,path,debug)

def load_fit(numbers:list,labels:list,ovs:list,chs:list,path:str=f'{root}/analysis',debug:bool=False):
    return load_df('_fit',numbers,labels,ovs,chs,path,debug)

def load_analysis(numbers:list,labels:list,ovs:list,chs:list,path:str=f'{root}/analysis',debug:bool=False):
    return load_df('_analysis',numbers,labels,ovs,chs,path,debug)

def load_df(stage:str,numbers:list,labels:list,ovs:list,chs:list,path:str=f'{root}/analysis',debug:bool=False):
    import pandas as pd
    from itertools import product
    df = pd.DataFrame()
    for n, label, ov, ch in product(numbers, labels, ovs, chs):
        try:
            new_df = pd.read_csv(f'{path}/{n}/{label}/{n}_{label}_DC_data{stage}_{ov}_{ch}.csv')
            # Append new df to existing df and add n,label,ov and ch as new columns with the same length as the new df
            if len(new_df) == 0:
                if debug: rprint(f'No data for {n} {label} {ov} {ch}')
                continue
            # Check if columns are already in the df          
            new_df['Number'] = n
            new_df['Set'] = label
            new_df['OV'] = ov
            new_df['Channel'] = ch
            df = df.append(new_df, ignore_index=True)
        
        except:
            if debug: rprint(f'No data for {n} {label} {ov} {ch}')
            pass
    return df

def get_duration(nunbers:list,labels:list,chs:list,ovs:list,ow:bool=True,debug:bool=False):
    for n, label, ch, ov in product(nunbers, labels, chs, ovs):
        try:
            times = yaml.load(open(f'{root}/analysis/times.yml'),Loader=yaml.FullLoader)
        except FileNotFoundError:
            times = {}
        
        # Check if the key already exists
        if times.get((n, label, ov, ch), None) is not None and ow is False:
            if debug: rprint(f"Times for {n} {label} {ov} {ch} already found")
            continue
        
        le_path=f'{root}/data/{n}/{label}/DC/C{ch}--OV{ov}**'
        file_list = load_files(le_path)

        df = pd.read_csv(file_list[0], skiprows=2, nrows=50)
        df2 = pd.read_csv(file_list[-1], skiprows=2, nrows=50)

        time_first=df["TrigTime"].iloc[0].split(' ')[-1]
        time_last=df2["TrigTime"].iloc[-1].split(' ')[-1]

        i_time=pd.to_datetime(time_first).strftime("%Y/%m/%d, %H:%M:%S")
        f_time=pd.to_datetime(time_last).strftime("%Y/%m/%d, %H:%M:%S")
        diff_time=pd.to_datetime(time_last)-pd.to_datetime(time_first)
        diff_time=diff_time.total_seconds()
        times[(n,label,ov,ch)] = {'i_time':i_time, 'f_time':f_time, 'diff_time':diff_time}
        with open(f'{root}/analysis/times.yml', 'w') as file:
            documents = yaml.dump(times, file)
    
    os.chmod(f'{root}/analysis/times.yml', stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    return times