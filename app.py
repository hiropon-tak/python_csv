# coding: cp932
import streamlit as st
import datetime
import requests
import json
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from st_aggrid.shared import GridUpdateMode
import base64

st.set_page_config(layout='wide')
# ------------------sidebar-----------------------------------------------
shuketubi = st.sidebar.date_input('���t�����', value=datetime.date.today())
bin = st.sidebar.selectbox('�ւ����', [1, 2, 3, 4])
selected_item = st.sidebar.radio('������I��', ['���X�g�o�^', '�i�Ԍ���'])
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
    df_items = pd.DataFrame(items)
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
        'sup_name':'�d���於'
      }, inplace=True
    )
    st.session_state.df = df_items

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
        update_mode=GridUpdateMode.SELECTION_CHANGED
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

# ------------------list-------------------------------------------------
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
        }, inplace=True
      )
    st.session_state.list = df_data

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

    change_button = st.button('�C�����e��o�^')
    if change_button:
      df = aggrid_data['data']
      del st.session_state.list
      url = 'http://127.0.0.1:8000/data/update/'
      payload = []
      for row in df.itertuples():
          buf = {
            'id': row[1],
            'ad':row[2],
            'shuketubi':row[3],
            'bin': row[4],
            'num': row[6],
            'num_all': row[7],
            'cust_name': row[9],
            'due_date': row[10],
            'tonyu': row[12],
            'inventory': row[18],
            'afure': row[19],
            'comment': row[21]
          }
          payload.append(buf)
      res = requests.post(url, json.dumps(payload))
      if res.status_code == 200 and res.json()['message'] == 'update success':
        st.success('�o�^���܂���')
      else:
        st.error(f'��肪�������܂���(status code: {res.status_code})')

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

    csv = aggrid_data['data'].to_csv(index=False)
    b64 = base64.b64encode(csv.encode('utf-8-sig')).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="result.csv">CSV�t�@�C���̃_�E�����[�h</a>'
    st.markdown(href, unsafe_allow_html=True)





