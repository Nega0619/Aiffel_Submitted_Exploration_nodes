from curses import meta
import glob
import json
import os
from pathlib import Path
import pandas as pd

##################################################
# 현 상황   : suite에서 폴더 자체로 올린 데이터 검수하는 용도
# TODO     : meta 폴더에 json파일만 있는 경우
# 하드코딩   : meta_path 에 ISON
##################################################

# def get_meta_file_list_info(meta_path):

# meta path안의 모든 json 파일 가져오기
def get_all_metaFiles(meta_path):
    meta_file_list=[]
    for f in os.listdir(meta_path):
        filepath = meta_path + f
        meta_file_list += [meta_path+f+'/'+i for i in os.listdir(filepath)]       # meta폴더 내의 폴더명 + 파일명
    return meta_file_list


def get_xlsx(file_path, project_name='ISON'):
    source_path = file_path+'/'
    meta_path = source_path+'/meta/'+project_name+'/'
    df = pd.DataFrame(columns=['data_key', 'tags', 'work_assignee'])

    meta_file_list = get_all_metaFiles(meta_path)

    # meta 폴더에서 json 정보 가져오기
    for i, mf in enumerate(meta_file_list):
        df.loc[i] = ''
        with open(mf) as json_meta_data:
            json_meta_data = json.load(json_meta_data)
        
        df.loc[i]['data_key']   = json_meta_data['data_key']
        df.loc[i]['tags']       = json_meta_data['tags'][0]['name']
        df.loc[i]['work_assignee'] = json_meta_data['work_assignee']

        # label 폴더에서 json 정보 가져오기
        label_path = source_path + json_meta_data['label_path'][0]
        with open(label_path) as json_label_data:
            json_label_data = json.load(json_label_data)

        # object 개수대로 pandas의 열 수 늘려주기
        object_num = len(json_label_data['objects'])
        for num in range(object_num):
            index_num = num+1
            # index_num    = json_label_data['objects'][num]['annotation']['meta']['index_num']
            class_name = json_label_data['objects'][num]['class_name']
            properties = json_label_data['objects'][num]['properties']
            properties = '' if not properties else properties[0]['option_name']

            # dataframe에 해당 컬럼이없으면 추가해주기
            if 'class'+str(index_num) not in df.columns:
                df['class'+str(index_num)] = ''
                df['property'+str(index_num)] = ''
                print(f'{index_num}번 클래스 추가')
            
            df.loc[i]['class'+str(index_num)] = class_name
            df.loc[i]['property'+str(index_num)] = properties
    
    df.to_excel(source_path+project_name+'.xlsx')

    return True
