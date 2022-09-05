import encodings
import glob
import json
import os
from pathlib import Path
import pandas as pd

##################################################
# 현 상황   : suite에서 폴더 자체로 올린 데이터 검수하는 용도
# TODO     : 프로젝트 정보 받는 부분 추가
##################################################

def get_metaFolder_files(meta_path):
    files=[]
    for f in os.listdir(meta_path):
        file_path = os.path.join(meta_path, f)
        # get all files from folders
        if os.path.isdir(file_path):
            for ff in os.listdir(file_path):
                files.append(os.path.join(os.path.join(meta_path, f), ff))
        else:
            files.append(file_path)
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

def make_xlsx(file_path, project_name='ISON'):
    
    meta_path = os.path.join(os.path.join(file_path, 'meta'), project_name)

    files = get_metaFolder_files(meta_path)

    df = read_json(files, file_path)
    df.to_excel(os.path.join(file_path, project_name+'.xlsx'))

    result_path = os.path.join(file_path, project_name+'.xlsx')
    return True, result_path


# import glob
# import json
# import os
# from pathlib import Path
# import pandas as pd

# ##################################################
# # 현 상황   : suite에서 폴더 자체로 올린 데이터 검수하는 용도
# # TODO     : 프로젝트 정보 받는 부분 추가
# ##################################################

# def get_metaFolder_files(meta_path):
#     files=[]
#     for f in os.listdir(meta_path):
#         file_path = os.path.join(meta_path, f)
#         # get all files from folders
#         if os.path.isdir(file_path):
#             for ff in os.listdir(file_path):
#                 files.append(os.path.join(os.path.join(meta_path, f), ff))
#         else:
#             files.append(file_path)
#     return files

# def read_json(files, source_path):
#     df = pd.DataFrame(columns=['data_key', 'tags', 'work_assignee'])

#     for i, mf in enumerate(files):
#         df.loc[i] = ''

#         # get json info from meta folder
#         with open(mf) as json_meta_data:
#             json_meta_data = json.load(json_meta_data, encoding="utf-8")
        
#         df.loc[i]['data_key']   = json_meta_data['data_key']
#         df.loc[i]['tags']       = json_meta_data['tags'][0]['name']
#         df.loc[i]['work_assignee'] = json_meta_data['work_assignee']

#         # get json info from label folder
#         # label_path = source_path + json_meta_data['label_path'][0]
#         label_path = os.path.join(source_path, json_meta_data['label_path'][0])
#         with open(label_path) as json_label_data:
#             json_label_data = json.load(json_label_data)

#         # if label exists on data
#         if 'objects' in json_label_data:
#             object_num = len(json_label_data['objects'])
#             for num in range(object_num):
#                 index_num = num+1
#                 class_name = json_label_data['objects'][num]['class_name']
#                 properties = json_label_data['objects'][num]['properties']
#                 properties = '' if not properties else properties[0]['option_name']

#                 # object 개수대로 class와 property 수 늘려주기 
#                 if 'class'+str(index_num) not in df.columns:
#                     df['class'+str(index_num)] = ''
#                     df['property'+str(index_num)] = ''
#                     print(f'{index_num}번 클래스 추가')
                
#                 df.loc[i]['class'+str(index_num)] = class_name
#                 df.loc[i]['property'+str(index_num)] = properties
    
#     return df

# def make_xlsx(file_path, project_name='ISON'):
    
#     meta_path = os.path.join(os.path.join(file_path, 'meta'), project_name)

#     files = get_metaFolder_files(meta_path)

#     df = read_json(files, file_path)
#     df.to_excel(os.path.join(file_path, project_name+'.xlsx'))

#     result_path = os.path.join(file_path, project_name+'.xlsx')
#     return True, result_path
