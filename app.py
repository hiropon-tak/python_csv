# coding: cp932
import streamlit as st
import datetime
import requests
import json
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from st_aggrid.shared import GridUpdateMode

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
      register_button = st.button('�I�������i�Ԃ�o�^')

      if register_button:
        del st.session_state.df
        ad = aggrid_data['selected_rows'][0]['����r�d�k�e']
        url = 'http://127.0.0.1:8000/create/'
        payload = {
          'ad': ad,
          'num': 0,
          'num_all': 0,
          'cust_name': '',
          'due_date': '',
          'tonyu': 0,
          'inventory': 0,
          'afure': 0,
          'shuketubi': shuketubi.isoformat(),
          'bin': bin,
          'comment': ''
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
  df_data = pd.DataFrame(data)
  df_data.rename(
      columns= {
        'id': 'ID',
        's_num': '�W����',
        'num_all': '�W����(�S��)',
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
        update_mode=GridUpdateMode.VALUE_CHANGED
    )

    change_button = st.button('�C�����e��o�^')
    if change_button:
      df = aggrid_data['data']
    for row in df.itertuples():
        del st.session_state.list
        ad = aggrid_data['selected_rows'][0]['����r�d�k�e']
        url = 'http://127.0.0.1:8000/create/'
        payload = {
          'ad': ad,
          'num': 0,
          'num_all': 0,
          'cust_name': '',
          'due_date': '',
          'tonyu': 0,
          'inventory': 0,
          'afure': 0,
          'shuketubi': shuketubi.isoformat(),
          'bin': bin,
          'comment': ''
        }
        res = requests.post(url, json.dumps(payload))
        if res.status_code == 200:
          st.success('�o�^���܂���')
        else:
          st.error(f'��肪�������܂���(status code: {res.status_code})')


