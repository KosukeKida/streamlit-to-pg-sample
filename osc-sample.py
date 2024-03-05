import streamlit as st
import sqlalchemy as sa
import pandas as pd
import streamlit.components.v1 as components
from io import StringIO
from time import sleep
ss = st.session_state

# DB接続定義
engine = sa.create_engine(
    sa.engine.url.URL.create(
        drivername="postgresql",
        username="myuser",
        password="mypassword",
        host="myipv4address",
        port=5432,
        database="mydb",
    )
)


# 初期画面

st.title('OSC浅草')
st.title(' :blue[PostgreSQL] と :red[Streamlit] の展示')
'OSS-DBの模擬問題アプリをPostgreSQLとStreamlitで作成しました'
tab = st.tabs(['start', 'Q1','Q2','Q3','Q4','Q5','結果','分析','実行計画で遊ぼう'])

# tabで各機能を実装

with tab[0]:
    ss.name=st.text_input('お名前は？','浅草')
    '結果表示に用います。他の方にスコアが見えるので支障のないハンドルネームを使ってね。'
    if st.button('はじめる'):
        f'こんにちは、{ss.name}さん。OSS-DB 一緒に頑張りましょう。'


# 出題・回答パート

def quiz(i):
    SQL_i = f'SELECT q_no,q_text FROM question WHERE q_no = {i};'
    question_i = pd.read_sql(SQL_i,con=engine)

    for row in question_i.itertuples():
        st.write(f"{row.q_text}")

    ss.answer = st.multiselect('Select item', ['A', 'B', 'C', 'D' ,'E'], key=i)


with tab[1]:
    quiz(1)
    ss.answer_1=ss.answer

with tab[2]:
    quiz(2)
    ss.answer_2=ss.answer

with tab[3]:
    quiz(3)
    ss.answer_3=ss.answer

with tab[4]:
    quiz(4)
    ss.answer_4=ss.answer

with tab[5]:
    quiz(5)
    ss.answer_5=ss.answer

# 回答送信、採点

data = f"""
username,q_no,user_answer
"{ss.name}",1,"{ss.answer_1}"
"{ss.name}",2,"{ss.answer_2}"
"{ss.name}",3,"{ss.answer_3}"
"{ss.name}",4,"{ss.answer_4}"
"{ss.name}",5,"{ss.answer_5}"
"""

with tab[6]:
    df=pd.read_csv(StringIO(data))
    st.write(df)
    if st.button("回答する", key=0):
        table_name="answer"
        df.to_sql(table_name, con=engine, index=0, if_exists='append')

        with st.spinner('採点中です。お待ちください...'):
            sleep(3)
            st.success('採点が完了しました！')

        'あなたのスコア'
        calc_score=f"""
        SELECT username,sum(
        CASE user_answer WHEN correct_answer THEN q_score ELSE 0 END) score
        FROM answer AS a
        JOIN question AS q ON a.q_no = q.q_no
        WHERE username = '{ss.name}'
        GROUP BY username;
        """
        df = pd.read_sql(sql=calc_score, con=engine)
        st.write(df)

        'あなたの回答と、正答・配点は以下の通りです。どうでしたか？'
        check_answers=f"""
        SELECT username,a.q_no,user_answer,correct_answer,
        case user_answer when correct_answer then q_score ELSE 0 END AS user_score
        FROM answer AS a
        JOIN question AS q
        ON a.q_no = q.q_no
        WHERE username = '{ss.name}'
        ;
        """
        df = pd.read_sql(sql=check_answers, con=engine)
        st.write(df)

with tab[7]:
    '最近は以下の回答が集まっています。'
    sql_query="""
    SELECT * FROM answer ORDER BY a_id DESC LIMIT 50;
    """
    df = pd.read_sql(sql=sql_query, con=engine)
    st.write(df)

    '個人別スコア'
    sql_query="""
    SELECT username,
    sum(
        CASE user_answer
             WHEN correct_answer THEN q_score
                                 ELSE 0
        END
        ) score
    FROM answer AS a
    JOIN question AS q
    ON a.q_no = q.q_no
    GROUP BY username;
    """
    df = pd.read_sql(sql=sql_query, con=engine)
    st.bar_chart(df.set_index('username'))


    '問題ごとの正答率'
    sql_query="""
    SELECT no ,(score::numeric/cnt*100)::int correct_rate,100-(score::numeric/cnt*100)::int wrong_rate FROM
    (SELECT a.q_no no,
    sum(
        CASE user_answer
             WHEN correct_answer THEN 1
                                ELSE 0
        END
        ) score,
    count(a.q_no) cnt
    FROM answer AS a
    JOIN question AS q
    ON a.q_no = q.q_no
    GROUP BY a.q_no
    )
    ORDER BY no ASC;
    """
    st.code(f'{sql_query}')
    df = pd.read_sql(sql=sql_query, con=engine)
    st.write(df)
    st.bar_chart(df, x="no", y=["correct_rate", "wrong_rate"], color=["#008000", "#d3d3d3"])

with tab[8]:
    'コピペ用サンプル'
    query_sample1="""
    SELECT no ,(score::numeric/cnt*100)::int correct_rate,100-(score::numeric/cnt*100)::int wrong_rate FROM
    (SELECT a.q_no no,
    sum(
        CASE user_answer
             WHEN correct_answer THEN 1
                                ELSE 0
        END
        ) score,
    count(a.q_no) cnt
    FROM answer AS a
    JOIN question AS q
    ON a.q_no = q.q_no
    GROUP BY a.q_no
    )
    ORDER BY no ASC;
    """
    query_sample2="""
    SELECT a.q_no AS no,
    sum(
        CASE user_answer
            WHEN correct_answer THEN q_score
        END
        ) score
    FROM answer AS a
    JOIN question AS q
    ON a.q_no = q.q_no
    GROUP BY a.q_no;
    """
    query_sample3="""
    SELECT username,a.q_no,user_answer,correct_answer,
    CASE user_answer WHEN correct_answer THEN q_score else 0 END AS user_score
    FROM answer AS a
    JOIN question AS q
    ON a.q_no = q.q_no
    ;
    """

    st.code(f'{query_sample1}')
    st.code(f'{query_sample2}')
    st.code(f'{query_sample3}')

    st.title('SQL実行と同時に実行計画を取得できます')
    ss.query=st.text_area('SQL文を入力',f'{query_sample1}')
    st.code(f'{ss.query}')
    df = pd.read_sql(sql=ss.query, con=engine)
    st.write(df)

    explain_query="EXPLAIN ANALYZE  "
    explain_query += ss.query
    st.code(f'{explain_query}')
    df = pd.read_sql(sql=explain_query, con=engine)
    st.code("\n".join(df['QUERY PLAN'].to_list()))

    'https://github.com/dalibo/pev2?tab=readme-ov-file のローカル版を使用してます。'
    htmlcode=open('/home/alma/components/index.html', encoding="utf-8").read()
    components.html(f'{htmlcode}',height=1000,width=1200)