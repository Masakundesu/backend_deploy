# レストラン検索アプリケーション

このアプリケーションは、レストランの検索と詳細情報の表示を行うWebアプリケーションです。FlaskバックエンドとNext.jsフロントエンドで構成されています。

## 機能
- エリアベースのレストラン検索
- 人数、ジャンル、予算による絞り込み
- 個室・飲み放題の有無によるフィルタリング
- レストランの詳細情報表示（評価、メニュー、写真など）
- Google SheetsからのデータインポートとSQLiteでの管理

## 環境構築

### バックエンド（Flask）

1. **Pythonの仮想環境を作成**
```bash
python -m venv venv
```

2. **仮想環境を有効化**
```bash
source venv/bin/activate
```


3. **Google Cloud Platformの設定**
- サービスアカウントを作成し、JSONキーファイルを取得
- `service_account.json`としてプロジェクトルートに配置

4. **データベースの初期化**
```bash
python init_db.py
```

5. **アプリケーションの起動**
```bash
python app.py
```


### フロントエンド（Next.js）

1. **依存関係のインストール**
```bash
npm install
```

2. **開発サーバーの起動**
```bash
npm run dev
```


## API エンドポイント

### GET /api/areas
- 利用可能なエリアの一覧を取得

### GET /api/genres
- 利用可能なジャンルの一覧を取得

### GET /result
クエリパラメータに基づいてレストランを検索
パラメータ：
- area: エリア名
- guests: 人数
- genre: ジャンル
- budgetMin: 最小予算
- budgetMax: 最大予算
- privateRoom: 個室の有無
- drinkIncluded: 飲み放題の有無

### GET /restaurant/{id}
- 指定されたIDのレストラン詳細情報を取得

## データベース構造
SQLiteデータベースには以下のカラムを持つrestaurantsテーブルが含まれます：
- id: INTEGER PRIMARY KEY AUTOINCREMENT
- name: TEXT
- address: TEXT
- phone: TEXT
- tabelog_rating: REAL
- tabelog_reviews: INTEGER
- tabelog_link: TEXT
- google_rating: REAL
- google_reviews: INTEGER
- google_link: TEXT
- opening_hours: TEXT
- course: TEXT
- menu: TEXT
- drink_menu: TEXT
- store_top_image: TEXT
- description: TEXT
- longitude: REAL
- latitude: REAL
- area: TEXT
- nearest_station: TEXT
- directions: TEXT
- capacity: INTEGER
- category: TEXT
- budget_min: INTEGER
- budget_max: INTEGER
- has_private_room: TEXT
- has_drink_all_included: TEXT
- detail_image1: TEXT
- detail_image2: TEXT
- detail_image3: TEXT

## フロントエンド構成
- ホームページ：レストラン検索フォーム
- レストラン詳細ページ：各レストランの詳細情報表示

## 開発環境
- Python 3.11以上
- Node.js 18.0.0以上
- SQLite3