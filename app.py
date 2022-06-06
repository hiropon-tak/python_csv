# coding: cp932
from re import U
import streamlit as st
import datetime
import requests
import json
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from st_aggrid.shared import GridUpdateMode
import base64
import sqlite3
import utility as utl

st.set_page_config(layout='wide')

# ------------------sidebar-----------------------------------------------
shuketubi = st.sidebar.date_input('���t�����', value=datetime.date.today())
bin = st.sidebar.selectbox('�ւ����', [1, 2, 3, 4])
selected_item = st.sidebar.radio('������I��', ['���X�g�o�^', '�i�Ԍ���', '�}�X�^�X�V'])

# ------------------header-------------------------------------------------
st.title(selected_item)

# ------------------search-------------------------------------------------
if selected_item == '�i�Ԍ���':

  with st.sidebar.form(key='item'):
    hinban: str = st.text_input('�i��')
    store: str = st.text_input('�u��')
    submit_button = st.form_submit_button(label='���M')

  if submit_button:
    
    q = f'?hinban={hinban}&store={store}'
    url = f'http://127.0.0.1:8000/masters/{q}'
    res = requests.get(url)
    items = res.json()
    if len(items) != 0: 
      df_items = pd.DataFrame(items)
      df_items = df_items.reindex(columns=[
        'id', 'ad', 'sup_code', 'sup_name', 'hinban', 'seban', 'store', 'num', 'box', 'k_num', 'y_num', 'h_num'
      ])
      df_items.rename(
        columns= {
          'ad': '����r�d�k�e',
          'sup_code': '�d����',
          'seban': '�w�ԍ�',
          'hinban': '�i��',
          'num': '���e��',
          'store': '�X�g�A�A�h���X',
          'k_num': '��]����',
          'y_num': '�ǎ文��',
          'h_num': '��������',
          'box': '����',
          'sup_name':'�d���於'
        }, inplace=True
      )
      st.session_state.df = df_items
    else:
      if 'df' in st.session_state:
        del st.session_state.df
      st.write('������܂���ł���')

  if 'df' in st.session_state: 

    gb = GridOptionsBuilder.from_dataframe(st.session_state.df)
    # gb.configure_default_column(editable=True)
    gb.configure_grid_options(enableRangeSelection=True)
    gb.configure_selection(selection_mode='multiple', use_checkbox=True)
    aggrid_data = AgGrid(
        st.session_state.df,
        gridOptions=gb.build(),
        allow_unsafe_jscode=True,
        enable_enterprise_modules=True,
        update_mode=GridUpdateMode.MODEL_CHANGED
    )

    if len(aggrid_data['selected_rows']) == 1:

      st.write('�ǉ��������')
      num: int = st.text_input('�W����', value=0)
      num_all: int = st.text_input('�W����_�S��', value=0)
      cust_name: str = st.text_input('���Ӑ於', value='')
      due_date: datetime.date = st.date_input('����', value=datetime.date.today())
      tonyu: int = st.text_input('������', value=0)
      inventory: int = st.text_input('�݌ɐ�', value=0)
      afure: int = st.text_input('���ӂꐔ', value=0)
      comment: str = st.text_input('�R�����g', value='')

      register_button = st.button('�I�������i�Ԃ�o�^')

      if register_button:
        del st.session_state.df
        ad = aggrid_data['selected_rows'][0]['����r�d�k�e']
        url = 'http://127.0.0.1:8000/create/'
        payload = {
          'ad': ad,
          'num': num,
          'num_all': num_all,
          'cust_name': cust_name,
          'due_date': due_date.isoformat(),
          'tonyu': tonyu,
          'inventory': inventory,
          'afure': afure,
          'shuketubi': shuketubi.isoformat(),
          'bin': bin,
          'comment': comment
        }
        res = requests.post(url, json.dumps(payload))
        if res.status_code == 200:
          st.success('�o�^���܂���')
        else:
          st.error(f'��肪�������܂���(status code: {res.status_code})')

# ------------------list---------------------------------------------------
elif selected_item == '���X�g�o�^':

  q = f'?day={shuketubi.isoformat()}'
  url = f'http://127.0.0.1:8000/data/{q}'
  res = requests.get(url)
  data = res.json()
  if len(data) != 0:
    df_data = pd.DataFrame(data)
    df_data.rename(
        columns= {
          'id': 'ID',
          's_num': '�W����',
          'num_all': '�W����_�S��',
          'cust_name': '���Ӑ於',
          'due_date': '����',
          'tonyu': '������',
          'inventory': '�݌ɐ�',
          'afure': '���ӂꐔ',
          'shuketubi': '�W����',
          'bin': '�W����',
          'comment': '�R�����g',
          'ad': '����r�d�k�e',
          'sup_code': '�d����',
          'sup_name': '�d���於',
          'seban': '�w�ԍ�',
          'hinban': '�i��',
          'm_num': '���e��',
          'store': '�X�g�A�A�h���X',
          'k_num': '��]����',
          'y_num': '�ǎ文��',
          'h_num': '��������',
          'box': '����'
        }, inplace=True
      )
    st.session_state.list = df_data
  else:
    if 'list' in st.session_state:
      del st.session_state.list
    st.write('�Ώۂ̃��X�g�͂���܂���')

  if 'list' in st.session_state: 

    gb = GridOptionsBuilder.from_dataframe(st.session_state.list)
    gb.configure_default_column(editable=True)
    gb.configure_grid_options(enableRangeSelection=True)
    gb.configure_selection(selection_mode='multiple', use_checkbox=True)
    aggrid_data = AgGrid(
        st.session_state.list,
        gridOptions=gb.build(),
        allow_unsafe_jscode=True,
        enable_enterprise_modules=True,
        update_mode=GridUpdateMode.MODEL_CHANGED
    )
    # �C���{�^��
    change_button = st.button('�C�����e��o�^')
    if change_button:
      df = aggrid_data['data']
      del st.session_state.list
      url = 'http://127.0.0.1:8000/data/update/'
      payload = []
      for id, ad, shuketubi, bin, num, num_all, cust_name, due_date, tonyu, inventory, afure, comment in \
      zip(df['ID'],
          df['����r�d�k�e'],
          df['�W����'],
          df['�W����'],
          df['�W����'],
          df['�W����_�S��'],
          df['���Ӑ於'],
          df['����'],
          df['������'],
          df['�݌ɐ�'],
          df['���ӂꐔ'],
          df['�R�����g']):
          buf = {
            'id': id,
            'ad': ad,
            'shuketubi': shuketubi,
            'bin': bin,
            'num': num,
            'num_all': num_all,
            'cust_name': cust_name,
            'due_date': due_date,
            'tonyu': tonyu,
            'inventory': inventory,
            'afure': afure,
            'comment': comment
          }
          payload.append(buf)
      res = requests.post(url, json.dumps(payload))
      if res.status_code == 200 and res.json()['message'] == 'update success':
        st.success('�o�^���܂���')
      else:
        st.error(f'��肪�������܂���(status code: {res.status_code})')

    # �폜�{�^��
    delete_button = st.button('�I�����폜')
    if delete_button:
      if len(aggrid_data['selected_rows']) > 0:
        del st.session_state.list
        url = 'http://127.0.0.1:8000/data/delete/'
        payload = []
        for row in aggrid_data['selected_rows']:
          payload.append(row['ID'])
        res = requests.post(url, json.dumps(payload))
        if res.status_code == 200 and res.json()['message'] == 'delete success':
          st.success('�폜���܂���')
        else:
          st.error(f'��肪�������܂���(status code: {res.status_code})')

    # CSV�_�E�����[�h
    csv = aggrid_data['data'].to_csv(index=False)
    b64 = base64.b64encode(csv.encode('utf-8-sig')).decode()
    d = datetime.date.today().isoformat()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="shuketu_list{d}.csv">CSV�t�@�C���̃_�E�����[�h</a>'
    st.markdown(href, unsafe_allow_html=True)

# ------------------master-------------------------------------------------
elif selected_item == '�}�X�^�X�V':

  db = 'test.db'

  #�}�X�^
  st.markdown('### �� �}�X�^�A�b�v���[�h(KANOUT)')
  file = st.file_uploader('�}�X�^���A�b�v���[�h���Ă�������.')
  if file:
    if file.name == 'KANOUT':
      file_name = file.name
      widths = [1, 5, 1, 1, 5, 2, 4, 14, 5, 8, 5, 1, 10, 4, 5, 2, 1, 3, 6, 2, 4, 8, 5, 6, 4, 8, 4, 3, 4, 4, 8, 4, 4, 4, 5, 5, 5, 5, 5, 5, 8, 1, 1, 2, 1, 8, 10, 8, 12, 1, 3, 1, 9]
      names = ['aki', 'ad', 'kaitei', 'cp', 'sup_code', 'ukeire', 'seban', 'hinban', 'num', 'store', 'sikyu', 's_kubun', 'line_add', 'aki2', 'shuyoseki', 'tanto', 'iro', 'pocket', 'cycle', 'aki3', 'setteimai', 'setteiryo', 'mai_bin', 'ryo_bin', 'zen_mai', 'zen_ryo', 'k_num', 'y_num', 's_num', 'h_num', 'sohat', 'kinko', 'hakko', 'hakkosumi', 'b_add', 'a_add', 'gai_1', 'gai_2', 'gai_3', 'siharai', 'kigo', 'b_kubun', 'u_kubun', 'mark', 'mark_col', 'box', 'kose', 's_okiba', 'comment', 'sys_kubun', 'shukkaba', 'n_kubun', 'aki4']
      usecols= [1, 4, 6, 7, 8, 9, 26, 27, 29, 45]
      fn = {
        'num': 0,
        'k_num': 0,
        'y_num': 0,
        'h_num': 0,
        'ad': '',
        'sup_code': '',
        'seban': '',
        'hinban': '',
        'store': '',
        'box': ''
      }
      with open(file.name, 'wb') as f:
          f.write(file.read())
      df = utl.master2df(file_name, widths, names, usecols, fn)
      drop = 'DROP TABLE IF EXISTS master'
      create = '''
                CREATE TABLE master (
                  id INTEGER PRIMARY KEY, 
                  ad TEXT, 
                  sup_code TEXT, 
                  seban TEXT, 
                  hinban TEXT, 
                  num INTEGER, 
                  store TEXT, 
                  k_num INTEGER, 
                  y_num INTEGER, 
                  h_num INTEGER,
                  box TEXT
                )
               '''
      table_name = 'master'
      tables = utl.df2table(db, df, drop, create, table_name)
      st.table(tables)

  #�d����}�X�^
  st.markdown('### �� �d����A�b�v���[�h(USROUT)')
  file = st.file_uploader('�d������A�b�v���[�h���Ă�������.')
  if file:
    if file.name == 'USROUT':
      file_name = file.name
      widths = [6, 5, 20]
      names = ['ad', 'sup_code', 'sup_name']
      usecols= [1, 2]
      fn = 0
      with open(file.name, 'wb') as f:
          f.write(file.read())
      df = utl.master2df(file_name, widths, names, usecols, fn)
      drop = 'DROP TABLE IF EXISTS sup'
      create = '''
                CREATE TABLE sup (
                  id INTEGER PRIMARY KEY, 
                  sup_code TEXT,
                  sup_name TEXT
                )
               '''
      table_name = 'sup'
      tables = utl.df2table(db, df, drop, create, table_name)
      st.table(tables)

  #�ݐσ}�X�^
  st.markdown('### �� �����ݐσA�b�v���[�h(RUIOUT)')
  file = st.file_uploader('�����ݐς��A�b�v���[�h���Ă�������.')
  if file:
    if file.name == 'RUIOUT':
      d = 3
      with open(file.name, 'wb') as f:
          f.write(file.read())
      df = utl.ruiout2df(d)
      drop = 'DROP TABLE IF EXISTS rui'
      s = ''
      for i in range(d):
          s += f'''
              n_bi{i} TEXT,
              n_bin{i} TEXT,
              h_kubun{i} TEXT,
              h_bi{i} TEXT,
              h_bin{i} TEXT,
              h_jikan{i} TEXT,
              noban{i} TEXT,
              hako{i} INTEGER,
              nonyu{i} INTEGER,'''
      s = s[:-1]
      create = f'''
          CREATE TABLE rui (
              id INTEGER PRIMARY KEY, 
              ad TEXT,{s}
          )
          '''
      table_name = 'rui'
      tables = utl.df2table(db, df, drop, create, table_name)
      st.table(tables)
