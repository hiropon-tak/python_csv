# coding: cp932
import streamlit as st
import datetime
import requests
import json
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from st_aggrid.shared import GridUpdateMode

st.set_page_config(layout="wide")

# ------------------sidebar-----------------------------------------------
with st.sidebar.form(key='item'):
  hinban: str = st.text_input('�i��')
  store: str = st.text_input('�u��')
  submit_button = st.form_submit_button(label='���M')

selected_item = st.sidebar.radio('������I��', ['���X�g�o�^', '�i�Ԍ���'])

# ------------------header-------------------------------------------------
st.title(selected_item)
# ------------------search-------------------------------------------------

if selected_item == '�i�Ԍ���':

  if submit_button:
    
    q = f'?hinban={hinban}&store={store}'
    url = f'http://127.0.0.1:8000/masters/{q}'
    res = requests.get(url)
    items = res.json()
    df_items = pd.DataFrame(items)
    df_items.rename(
      columns={
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
    gb.configure_default_column(editable=True)
    gb.configure_grid_options(enableRangeSelection=True)
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    aggrid_data = AgGrid(
        st.session_state.df,
        gridOptions=gb.build(),
        allow_unsafe_jscode=True,
        enable_enterprise_modules=True,
        update_mode=GridUpdateMode.SELECTION_CHANGED
    )

    if len(aggrid_data['selected_rows']) > 0:
      register_button = st.button('�I�������i�Ԃ�o�^')

      if register_button:
        
        st.success('�o�^���܂���')


elif selected_item == '���X�g�o�^':
  st.write('list')
