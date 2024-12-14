from flask import Flask, jsonify, request
from flask_cors import CORS
from google.cloud import translate_v2 as translate
import sqlite3
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
import logging

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # CORS設定を更新

# Google Sheets API認証
SERVICE_ACCOUNT_FILE = 'service_account.json'  # サービスアカウントのJSONファイルのパス
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# スプレッドシートの設定
SHEET_ID = '13W3SPt7KrGnYCLzC8DQ0QyoNhFFs8CEd4faHBhUSDww'
SHEET_RANGE = 'DB!A:AC'  # 取得する範囲

def authenticate_google_services():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return credentials

def get_spreadsheet_data():
    credentials = authenticate_google_services()
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SHEET_ID, range=SHEET_RANGE).execute()
    rows = result.get('values', [])
    if rows:
        headers = rows[0]
        data = rows[1:]
        return data, headers
    return [], []

def init_db():
    conn = sqlite3.connect('example.db')
    c = conn.cursor()

    # 既存のテーブルを削除
    c.execute('DROP TABLE IF EXISTS restaurants')

    # 新しいテーブルを作成
    c.execute('''
        CREATE TABLE IF NOT EXISTS restaurants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address TEXT,
            phone_number TEXT,
            tabelog_rating REAL,
            tabelog_review_count INTEGER,
            tabelog_link TEXT,
            google_rating REAL,
            google_review_count INTEGER,
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

def insert_data_to_db(data, headers):
    conn = sqlite3.connect('example.db')
    c = conn.cursor()

    # データを挿入
    for row in data:
        # 行の長さが29に満たない場合、足りない部分を空文字で補完
        if len(row) < 29:
            row += [''] * (29 - len(row))  # 足りない分を空文字で補完

        c.execute('''
            INSERT INTO restaurants (
                name, address, phone_number, tabelog_rating, tabelog_review_count, tabelog_link, google_rating, 
                google_review_count, google_link, opening_hours, course, menu, drink_menu, store_top_image, 
                description, longitude, latitude, area, nearest_station, directions, capacity, category, 
                budget_min, budget_max, has_private_room, has_drink_all_included, detail_image1, detail_image2, 
                detail_image3
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', tuple(row))

    conn.commit()
    conn.close()


@app.route('/', methods=['GET'])
def hello():
    return jsonify({'message': 'Flask start!'})

@app.route('/api/hello', methods=['GET'])
def hello_world():
    return jsonify(message='Hello World by Flask')

@app.route('/api/areas', methods=['GET'])
def get_areas():
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT area FROM restaurants")
    rows = cursor.fetchall()
    conn.close()
    areas = [row[0] for row in rows]
    return jsonify(areas)

@app.route('/api/genres', methods=['GET'])
def get_genres():
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM restaurants")
    rows = cursor.fetchall()
    conn.close()
    genres = [row[0] for row in rows]
    return jsonify(genres)

@app.route('/restaurant/<int:id>/menu', methods=['GET'])
def get_menu_details(id):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute("SELECT menu, drink_menu FROM restaurants WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({
            "foodMenu": row[0],
            "drinkMenu": row[1],
        })
    return jsonify({"error": "Menu not found"}), 404


@app.route('/result', methods=['GET'])
def result_restaurants():
    # クエリパラメータを取得
    area = request.args.get('area', '')  # エリア
    guests = request.args.get('guests', None, type=int)  # 人数
    genre = request.args.get('genre', '')  # ジャンル
    budget_min = request.args.get('budgetMin', None, type=int)  # 予算の下限
    budget_max = request.args.get('budgetMax', None, type=int)  # 予算の上限
    private_room = request.args.get('privateRoom', '')  # 個室の希望
    drink_included = request.args.get('drinkIncluded', '')  # 飲み放題の希望

    # SQLクエリの構築
    query = "SELECT * FROM restaurants WHERE 1=1"
    params = []

    # エリアは必須条件
    if area:
        query += " AND area = ?"
        params.append(area)
    
    # その他の条件は任意
    if guests is not None:
        query += " AND capacity >= ?"
        params.append(guests)
    if genre:
        query += " AND category LIKE ?"
        params.append(f"%{genre}%")
    if budget_min is not None:
        query += " AND budget_min >= ?"
        params.append(budget_min)
    if budget_max is not None:
        query += " AND budget_max <= ?"
        params.append(budget_max)
    if private_room:
        query += " AND has_private_room = ?"
        params.append(private_room)
    if drink_included:
        query += " AND has_drink_all_included = ?"
        params.append(drink_included)

    # データベース接続とクエリの実行
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    # データを整形して返却
    result = [
        {
            "id": row[0],
            "name": row[1],
            "address": row[2],
            "phone_number": row[3],
            "tabelog_rating": row[4],
            "tabelog_review_count": row[5],
            "tabelog_link": row[6],
            "google_rating": row[7],
            "google_review_count": row[8],
            "google_link": row[9],
            "opening_hours": row[10],
            "course": row[11],
            "menu": row[12],
            "drink_menu": row[13],
            "store_top_image": row[14],
            "description": row[15],
            "longitude": row[16],
            "latitude": row[17],
            "area": row[18],
            "nearest_station": row[19],
            "directions": row[20],
            "capacity": row[21],
            "category": row[22],
            "budget_min": row[23],
            "budget_max": row[24],
            "has_private_room": row[25],
            "has_drink_all_included": row[26],
            "detail_image1": row[27],
            "detail_image2": row[28],
            "detail_image3": row[29],
        }
        for row in rows
    ]
    return jsonify(result)

@app.route('/restaurant/<int:id>', methods=['GET'])
def get_restaurant_by_id(id):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM restaurants WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        print("No data found for this ID")
        return jsonify({'error': 'Restaurant not found'}), 404

    restaurant = {
        "id": row[0],
        "name": row[1],
        "address": row[2],
        "phone_number": row[3],
        "tabelog_rating": row[4],
        "tabelog_review_count": row[5],
        "tabelog_link": row[6],
        "google_rating": row[7],
        "google_review_count": row[8],
        "google_link": row[9],
        "opening_hours": row[10],
        "course": row[11],
        "menu": row[12],
        "drink_menu": row[13],
        "store_top_image": row[14],
        "description": row[15],
        "longitude": row[16],
        "latitude": row[17],
        "area": row[18],
        "nearest_station": row[19],
        "directions": row[20],
        "capacity": row[21],
        "category": row[22],
        "budget_min": row[23],
        "budget_max": row[24],
        "has_private_room": row[25],
        "has_drink_all_included": row[26],
        "detail_image1": row[27],
        "detail_image2": row[28],
        "detail_image3": row[29],
    }
    return jsonify(restaurant)
    

if __name__ == '__main__':
    app.run(debug=True)
