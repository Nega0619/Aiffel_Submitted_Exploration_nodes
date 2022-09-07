import json
import os
import pandas as pd
import platform
import logging
from datetime import datetime

##################################################
# 현 상황   : suite에서 폴더 자체로 올린 데이터 검수하는 용도
##################################################

def init_logger(path=''):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # set logging output
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # log 출력
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # log를 파일에 출력
    log_path = os.path.join(path, 'my.log')
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info('◆◆◆◆◆ start program ◆◆◆◆◆')

    return logger

def get_files_endswith(path='', endswith=''):
    assert path != '' , 'vacant path'
    assert endswith != '' , 'vacant endswith'

    result_files = []
    for (root, directories, files) in os.walk(path):
        for file in files:
            if endswith in file:
                result_files += [os.path.join(root, file)]
    return result_files

def read_json(files, source_path):
    try:
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
    except Exception as e:
        logger.error(mf+'파일에서 문제 발생했음!!')
        logger.error(str(e), exc_info=True)

def get_json_contents(file_path):
    try:
        # get json files in meta folder
        meta_path = os.path.join(file_path, 'meta')
        meta_files = get_files_endswith(meta_path, '.json')
        logger.debug('meta json files\n'+str(meta_files))
        logger.info('성공적으로 meta/json파일을 가져왔습니다.')

        df = pd.DataFrame(columns=['data_key', 'tags', 'work_assignee'])

        for i, mf in enumerate(meta_files):
            logger.debug('reading.... meta\n'+ mf)
            df.loc[i] = ''

            # get json info from meta folder
            with open(mf, encoding='UTF8') as json_meta_data:
                json_meta_data = json.load(json_meta_data)

            df.loc[i]['data_key'] = json_meta_data['data_key']
            df.loc[i]['tags'] = '' if not json_meta_data['tags'] else json_meta_data['tags'][0]['name']
            df.loc[i]['work_assignee'] = json_meta_data['work_assignee']
            logger.debug('got meta info')

            # get json info from label folder
            # json_meta_data['label_path'][0] = label/name.json
            label_file = os.path.join(file_path, json_meta_data['label_path'][0])
            with open(label_file, encoding='UTF8') as json_label_data:
                json_label_data = json.load(json_label_data)
                logger.debug('reading.... label\n' + label_file)

            # if label exists on data
            if 'objects' in json_label_data:
                logger.debug('Exist objects')
                object_num = len(json_label_data['objects'])
                for num in range(object_num):
                    index_num = num + 1
                    class_name = json_label_data['objects'][num]['class_name']
                    properties = json_label_data['objects'][num]['properties']
                    if not properties:          # empty property
                        properties = ''
                    elif properties[0]['type'] == 'radio':
                        properties = properties[0]['option_name']
                    elif properties[0]['type'] == 'free response':
                        properties = properties[0]['value']
                    # properties = '' if not properties else properties[0]['option_name']

                    # object 개수대로 class와 property 수 늘려주기
                    if 'class' + str(index_num) not in df.columns:
                        df['class' + str(index_num)] = ''
                        df['property' + str(index_num)] = ''
                        print(f'{index_num}번 클래스 추가')

                    df.loc[i]['class' + str(index_num)] = class_name
                    df.loc[i]['property' + str(index_num)] = properties

        return df
    except Exception as e:
        logger.error(str(e), exc_info=True)

def make_xlsx(file_path):
    # 프로젝트명 뽑아오기
    if platform.system() == 'Linux':
        logger.info('os env : Linux')
        file_name = file_path.split('/')[-1]
        logger.info('저장될 파일 이름: '+ file_name)
    elif platform.system() == 'Windows':
        logger.info('os env : Windows')
        file_name = file_path.split('/')[-1]
        logger.info('저장될 파일 이름: '+ file_name)

    df = get_json_contents(file_path)
    df.to_excel(os.path.join(file_path, file_name+'.xlsx'))
    logger.info('성공적으로 파일을 저장하였습니다.')

if __name__ == '__main__':
    file_path = '/home/hwi/Downloads/ISON 2022-09-01 17_07_55 (1)'
    # file_path='/home/hwi/Downloads/Licence Plate Recognition 2022-09-07 13_31_29'

    start_time = datetime.now()
    logger = init_logger(file_path)

    make_xlsx(file_path)

    end_time = datetime.now()

    logger.info(' 프로그램 실행 시간 '+ str(end_time-start_time))
    logger.info('◆◆◆◆◆  end  program ◆◆◆◆◆\n')
