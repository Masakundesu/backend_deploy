import sqlite3

def init_db():
    conn = sqlite3.connect('example.db')
    c = conn.cursor()

    # 既存のテーブルを削除
    c.execute('DROP TABLE IF EXISTS restaurants')

    # 新しいテーブルを作成（29列に対応）
    c.execute('''
        CREATE TABLE IF NOT EXISTS restaurants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address TEXT,
            phone TEXT,
            tabelog_rating REAL,
            tabelog_reviews INTEGER,
            tabelog_link TEXT,
            google_rating REAL,
            google_reviews INTEGER,
            google_link TEXT,
            opening_hours TEXT,
            course TEXT,
            menu TEXT,
            drink_menu TEXT,
            store_top_image TEXT,
            description TEXT,
            longitude REAL,
            latitude REAL,
            area TEXT,
            nearest_station TEXT,
            directions TEXT,
            capacity INTEGER,
            category TEXT,
            budget_min INTEGER,
            budget_max INTEGER,
            has_private_room TEXT,
            has_drink_all_included TEXT,
            detail_image1 TEXT,
            detail_image2 TEXT,
            detail_image3 TEXT
        )
    ''')
    conn.commit()
    conn.close()

    # テーブルが正しく作成されたか確認（オプション）
    check_db()

def check_db():
    conn = sqlite3.connect('example.db')
    c = conn.cursor()

    # テーブルの存在確認
    c.execute('PRAGMA table_info(restaurants)')
    columns = c.fetchall()
    print(f"Columns in 'restaurants' table: {columns}")
    
    conn.close()

# 実行してデータベースを作成
init_db()
