# streamlit-to-pg-sample

PostgreSQLがインストールされていること、DBサーバー上にpythonおよびstreamlit環境がインストール済みの前提

### Streamlit App情報
`/home/alma`直下にapp.pyを配置
```
# appの起動（バックグラウンドで稼働を継続）
streamlit run app.py &
```
```
# 稼働中のプロセス確認
ps -ef | grep streamlit
alma  21795  1  0 Feb24 ?  00:00:11 /usr/bin/python3 /home/alma/.local/bin/streamlit run tab_count.py
```
```
# 停止
kill -9 21795    # 上記で確認したPIDを指定
```

### 参考サイト
[Streamlitのインストール](https://zenn.dev/kyami/articles/e9700a136f6c20)
[session_stateを使用したインタラクティブなサンプル](https://nttdocomo-developers.jp/entry/20231216_1)
[PostgreSQLへの接続](https://docs.streamlit.io/knowledge-base/tutorials/databases/postgresql)
[チャート作成](https://shoblog.iiyan.net/how-to-create-a-graph-with-streamlit/)


# PostgreSQL
データベースクラスタ `/var/lib/pgsql/16/data`
```
# 起動
sudo systemctl start postgresql-16.service
# 停止
sudo systemctl stop postgresql-16.service
```
### 参考サイト
[PostgreSQL16のインストール](https://qiita.com/tom-sato/items/e1903cb974fb6c6d5664)