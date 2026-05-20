麻雀点数計算サイト（Django版）
概要

このアプリは、Django と Python ライブラリ「mahjong」を使用した
麻雀の点数計算Webアプリです。

ユーザーが手牌・和了牌・鳴き情報などを入力すると、
翻数・符・点数・役一覧を自動計算します。

また、ログイン機能を搭載しており、
各ユーザーごとに計算履歴を保存・閲覧できます。

主な機能
点数計算
翻数計算
符計算
点数計算
満貫 / 跳満 / 倍満 / 三倍満 / 役満 判定
入力対応
手牌入力

例:

123m456p789s11z55m
和了牌入力

例:

5m
鳴き対応
チー
123m
ポン
777p
カン
1111s
公開 / 非公開
open
closed

暗槓にも対応しています。

対応設定
ツモ / ロン
親 / 子
場風
自風
ドラ
裏ドラ
赤ドラ
リーチ
本場
供託
履歴機能

ログインユーザーごとに、
過去の計算結果を保存できます。

履歴画面
計算履歴一覧
詳細表示
削除（任意）
使用技術
技術	内容
Python	バックエンド
Django	Webフレームワーク
SQLite	データベース
Django Templates	フロント
mahjong	点数計算ライブラリ
ディレクトリ構成
mahjong_calc/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── mahjong_calc/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── calcapp/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── utils.py
│   ├── urls.py
│   ├── admin.py
│   └── migrations/
│
├── templates/
│   ├── base.html
│   ├── registration/
│   │   └── login.html
│   │
│   └── calcapp/
│       ├── index.html
│       ├── history.html
│       └── history_detail.html
インストール方法
1. ZIPを展開
Expand-Archive -Path .\mahjong_calc.zip -DestinationPath .\mahjong_calc
2. フォルダ移動
cd .\mahjong_calc
3. 仮想環境作成
python -m venv .venv
4. 仮想環境有効化
Windows
.\.venv\Scripts\Activate.ps1
Mac/Linux
source .venv/bin/activate
5. ライブラリインストール
pip install -r requirements.txt
データベース作成
python manage.py migrate

実行後、
db.sqlite3
が自動生成されます。

管理者ユーザー作成
python manage.py createsuperuser
サーバ起動
python manage.py runserver
アクセスURL
ページ	URL
ログイン	http://127.0.0.1:8000/accounts/login/
計算フォーム	http://127.0.0.1:8000/
管理画面	http://127.0.0.1:8000/admin/
履歴一覧	http://127.0.0.1:8000/history/
動作確認用サンプル
例1（門前ロン）
手牌
123m456p789s11z55m
和了牌
5m
鳴き

なし

設定
子
ロン
場風: 東
自風: 南
リーチ: ON
本場: 0
供託: 1
ドラ: 4m
例2（鳴きあり）
手牌
234p678p789s11z55m
和了牌
5m
鳴き
pon 777m open
設定
子
ツモ
場風: 東
自風: 東
本場: 1
ドラ: 3p
例3（暗槓あり）
手牌
123m456m789m11z55p
和了牌
5p
鳴き
kan 9999s closed
設定
親
ツモ
場風: 南
自風: 南
本場: 0
供託: 0
ドラ: 8s
セキュリティ
Django標準認証使用
CSRF対策済み
ログイン必須
ユーザーごとのデータ分離
所有者制御対応
今後の拡張予定
牌画像UI
ドラ牌パレット
点数履歴分析
AIによる役解説
AIによる待ち牌提案
スマホ対応UI
WebSocketによるリアルタイム卓
ライセンス

個人学習・ポートフォリオ用途で自由に使用可能。
