# 共同輸送システム モビリティハブ管理システム API

## 構成

- モビリティハブ管理システムはDockerで環境構築されています。
- Nginx+flaskで構成されたWebサーバとMySQL DBにて構成しています。
<img src="Documents/img1.png"/>

## 環境構築手順

- sample.envを.envにコピーする。
  - 以下のパスワードを設定する。
    - MYSQL_ROOT_PASSWORD
    - MHMNG_DB_USER_PASSWORD
- CONFIG/mysql/init.sql に上記 MHMNG_DB_USER_PASSWORD のパスワードを設定する
  - 21行目のMHMNG_DB_USER_PASSWORDの部分
  - CREATE USER IF NOT EXISTS 'mh'@'%' IDENTIFIED BY 'MHMNG_DB_USER_PASSWORD';
- CERTS
  - サーバーの公開鍵ファイルを格納してください。 (server.crt と server.key)

### 初回
- docker-compose build
- docker-compose up
  - DBの初期化が終わるのを待つ。終わったらCtl+CでDockerを停止する。
- docker-compose up -d

## 問合せ及び要望に関して

- 本リポジトリは現状は主に配布目的の運用となるため、IssueやPull Requestに関しては受け付けておりません。

## ライセンス

- 本リポジトリはMITライセンスで提供されています。
- 特筆が無い限り、ソースコードおよび関連ドキュメントの著作権はIntent Exchange 株式会社に帰属します。

## 免責事項

- 本リポジトリの内容は予告なく変更・削除する可能性があります。
- 本リポジトリの利用により生じた損失及び損害等について、いかなる責任も負わないものとします。