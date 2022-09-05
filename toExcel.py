import encodings
import glob
import json
import os
from pathlib import Path
from tkinter import PROJECTING
import pandas as pd
import platform
import logging
logger = logging.getLogger()

##################################################
# 현 상황   : suite에서 폴더 자체로 올린 데이터 검수하는 용도
##################################################

def init_logger():
    # log의 출력 기준 설정
    logger.setLevel(logging.debug)

    # log 출력 형식
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s' )

    # log 출력
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # log를 파일에 출력
    file_handler = logging.FileHandler('my.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

    # logging.basicConfig(filename='.log', encoding='utf-8', level=logging.DEBUG)

def get_metaFolder_files(meta_path):
    logger.info('Enter code get_metaFolder_files')

    files=[]
    for f in os.listdir(meta_path):
        file_path = os.path.join(meta_path, f)
        # get all files from folders
        if os.path.isdir(file_path):
            for ff in os.listdir(file_path):
                files.append(os.path.join(os.path.join(meta_path, f), ff))
        else:
            files.append(file_path)
    logger.debug('THIS IS META FILES\n', files)
    logger.info('Exit  code get_metaFolder_files')

    return files

def read_json(files, source_path):
    df = pd.DataFrame(columns=['data_key', 'tags', 'work_assignee'])

    for i, mf in enumerate(files):
        df.loc[i] = ''

        # get json info from meta folder
        with open(mf, encoding='UTF8') as json_meta_data:
            json_meta_data = json.load(json_meta_data)
        
        df.loc[i]['data_key']   = json_meta_data['data_key']
        df.loc[i]['tags']       = json_meta_data['tags'][0]['name']
        df.loc[i]['work_assignee'] = json_meta_data['work_assignee']

        # get json info from label folder
        # label_path = source_path + json_meta_data['label_path'][0]
        label_path = os.path.join(source_path, json_meta_data['label_path'][0])
        with open(label_path) as json_label_data:
            json_label_data = json.load(json_label_data)

        # if label exists on data
        if 'objects' in json_label_data:
            object_num = len(json_label_data['objects'])
            for num in range(object_num):
                index_num = num+1
                class_name = json_label_data['objects'][num]['class_name']
                properties = json_label_data['objects'][num]['properties']
                properties = '' if not properties else properties[0]['option_name']

                # object 개수대로 class와 property 수 늘려주기 
                if 'class'+str(index_num) not in df.columns:
                    df['class'+str(index_num)] = ''
                    df['property'+str(index_num)] = ''
                    print(f'{index_num}번 클래스 추가')
                
                df.loc[i]['class'+str(index_num)] = class_name
                df.loc[i]['property'+str(index_num)] = properties
    
    return df

def make_xlsx(file_path):
    logger = init_logger()
    logger.debug('this is test')

    # 프로젝트명 뽑아오기
    if platform.system() == 'Linux':
        project_name = file_path.split('/')[-1]
    elif platform.system() == 'Windows':
        project_name = file_path.split('\\')[-1]
    logging.info('file_path:', file_path)
    logging.info('project_name:', project_name)
    
    meta_path = os.path.join(os.path.join(file_path, 'meta'), project_name)

    files = get_metaFolder_files(meta_path)
    logger.info('Successfully get the meta files from {meta_path}'.format())

    df = read_json(files, file_path)
    df.to_excel(os.path.join(file_path, project_name+'.xlsx'))

    result_path = os.path.join(file_path, project_name+'.xlsx')
    return True, result_path
