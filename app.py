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

st.set_page_config(layout='wide')
# ------------------sidebar-----------------------------------------------
shuketubi = st.sidebar.date_input('日付を入力', value=datetime.date.today())
bin = st.sidebar.selectbox('便を入力', [1, 2, 3, 4])
selected_item = st.sidebar.radio('処理を選択', ['リスト登録', '品番検索', 'マスタ更新'])
# ------------------header-------------------------------------------------
st.title(selected_item)
# ------------------search-------------------------------------------------
if selected_item == '品番検索':

  with st.sidebar.form(key='item'):
    hinban: str = st.text_input('品番')
    store: str = st.text_input('置場')
    submit_button = st.form_submit_button(label='送信')

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
          'ad': 'かんＳＥＬＦ',
          'sup_code': '仕入先',
          'seban': '背番号',
          'hinban': '品番',
          'num': '収容数',
          'store': 'ストアアドレス',
          'k_num': '回転枚数',
          'y_num': '読取枚数',
          'h_num': '発注枚数',
          'box': '箱種',
          'sup_name':'仕入先名'
        }, inplace=True
      )
      st.session_state.df = df_items
    else:
      if 'df' in st.session_state:
        del st.session_state.df
      st.write('見つかりませんでした')

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

      st.write('追加情報を入力')
      num: int = st.text_input('集欠数', value=0)
      num_all: int = st.text_input('集欠数_全体', value=0)
      cust_name: str = st.text_input('得意先名', value='')
      due_date: datetime.date = st.date_input('期日', value=datetime.date.today())
      tonyu: int = st.text_input('投入数', value=0)
      inventory: int = st.text_input('在庫数', value=0)
      afure: int = st.text_input('あふれ数', value=0)
      comment: str = st.text_input('コメント', value='')

      register_button = st.button('選択した品番を登録')

      if register_button:
        del st.session_state.df
        ad = aggrid_data['selected_rows'][0]['かんＳＥＬＦ']
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
          st.success('登録しました')
        else:
          st.error(f'問題が発生しました(status code: {res.status_code})')

# ------------------list-------------------------------------------------
elif selected_item == 'リスト登録':

  q = f'?day={shuketubi.isoformat()}'
  url = f'http://127.0.0.1:8000/data/{q}'
  res = requests.get(url)
  data = res.json()
  if len(data) != 0:
    df_data = pd.DataFrame(data)
    df_data.rename(
        columns= {
          'id': 'ID',
          's_num': '集欠数',
          'num_all': '集欠数_全体',
          'cust_name': '得意先名',
          'due_date': '期日',
          'tonyu': '投入数',
          'inventory': '在庫数',
          'afure': 'あふれ数',
          'shuketubi': '集欠日',
          'bin': '集欠便',
          'comment': 'コメント',
          'ad': 'かんＳＥＬＦ',
          'sup_code': '仕入先',
          'sup_name': '仕入先名',
          'seban': '背番号',
          'hinban': '品番',
          'm_num': '収容数',
          'store': 'ストアアドレス',
          'k_num': '回転枚数',
          'y_num': '読取枚数',
          'h_num': '発注枚数',
          'box': '箱種'
        }, inplace=True
      )
    st.session_state.list = df_data
  else:
    if 'list' in st.session_state:
      del st.session_state.list
    st.write('対象のリストはありません')

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
    # 修正ボタン
    change_button = st.button('修正内容を登録')
    if change_button:
      df = aggrid_data['data']
      del st.session_state.list
      url = 'http://127.0.0.1:8000/data/update/'
      payload = []
      for id, ad, shuketubi, bin, num, num_all, cust_name, due_date, tonyu, inventory, afure, comment in \
      zip(df['ID'],
          df['かんＳＥＬＦ'],
          df['集欠日'],
          df['集欠便'],
          df['集欠数'],
          df['集欠数_全体'],
          df['得意先名'],
          df['期日'],
          df['投入数'],
          df['在庫数'],
          df['あふれ数'],
          df['コメント']):
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
        st.success('登録しました')
      else:
        st.error(f'問題が発生しました(status code: {res.status_code})')

    # 削除ボタン
    delete_button = st.button('選択を削除')
    if delete_button:
      if len(aggrid_data['selected_rows']) > 0:
        del st.session_state.list
        url = 'http://127.0.0.1:8000/data/delete/'
        payload = []
        for row in aggrid_data['selected_rows']:
          payload.append(row['ID'])
        res = requests.post(url, json.dumps(payload))
        if res.status_code == 200 and res.json()['message'] == 'delete success':
          st.success('削除しました')
        else:
          st.error(f'問題が発生しました(status code: {res.status_code})')

    # CSVダウンロード
    csv = aggrid_data['data'].to_csv(index=False)
    b64 = base64.b64encode(csv.encode('utf-8-sig')).decode()
    d = datetime.date.today().isoformat()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="shuketu_list{d}.csv">CSVファイルのダウンロード</a>'
    st.markdown(href, unsafe_allow_html=True)


elif selected_item == 'マスタ更新':

  db = 'test.db'

  st.markdown('### ● マスタアップロード')
  file = st.file_uploader('マスタをアップロードしてください.')
  if file:
    if file.name == 'master.csv':
      with open(file.name, 'wb') as f:
          f.write(file.read())

      df = pd.read_csv('master.csv',
                    usecols=[1, 4, 6, 7, 8, 9, 26, 27, 29, 45],
                    dtype = str).fillna(0).astype(
                      {'かんＳＥＬＦ': str, 
                        '仕入先': str, 
                        '収容数': int, 
                        '回転枚数': int, 
                        '読取枚数': int, 
                        '発注枚数': int}
                      )
      df.rename(columns={'かんＳＥＬＦ': 'ad',
                        '仕入先': 'sup_code',
                        '背番号': 'seban',
                        '品番': 'hinban',
                        '収容数': 'num',
                        'ストアアドレス': 'store',
                        '回転枚数': 'k_num',
                        '読取枚数': 'y_num',
                        '発注枚数': 'h_num',
                        '箱種': 'box'}, inplace=True)
      df['seban'] = df['seban'].str.strip()
      df['hinban'] = df['hinban'].str.strip()
      df['store'] = df['store'].str.strip()
      df['box'] = df['box'].str.strip()

      con = sqlite3.connect(db)
      cur = con.cursor()
      cur.execute(
        'DROP TABLE IF EXISTS master'
      )
      cur.execute(
        '''
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
            box TEXT)
        '''
      )				
      df.to_sql('master', con, if_exists='append', index=False)
      cur.execute(
          "SELECT * FROM master LIMIT 5"
      )
      tables = cur.fetchall()
      con.close()
      st.table(tables)

  st.markdown('### ● 仕入先アップロード')
  file = st.file_uploader('仕入先をアップロードしてください.')
  if file:
    if file.name == 'sup.csv':
      with open(file.name, 'wb') as f:
          f.write(file.read())

      df_s = pd.read_csv('sup.csv',
                  usecols=[0, 1],
                  dtype = str).fillna(0)
      df_s.rename(columns={'仕入先': 'sup_code','仕入先名': 'sup_name'}, inplace=True)

      df_s['sup_name'] = df_s['sup_name'].str.strip()

      con = sqlite3.connect(db)
      cur = con.cursor()
      cur.execute(
          'DROP TABLE IF EXISTS sup'
      )
      cur.execute(
          '''
          CREATE TABLE sup (
              id INTEGER PRIMARY KEY, 
              sup_code TEXT,
              sup_name TEXT)
          '''
      )
      df_s.to_sql('sup', con, if_exists='append', index=False)
      cur.execute(
          "SELECT * FROM sup LIMIT 5"
      )
      tables = cur.fetchall()
      con.close()
      st.table(tables)
