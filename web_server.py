#!/usr/bin/env python3
import os
import json
import argparse
from flask import Flask, render_template, send_from_directory, jsonify

app = Flask(__name__)

# Путь к JSON-файлу с результатами анализа
results_file = None

@app.route('/')
def index():
    """Отображает главную страницу."""
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    """Отдает статические файлы."""
    return send_from_directory('static', path)

@app.route('/developer_stats.json')
def serve_data():
    """Отдает JSON-файл с результатами анализа."""
    if not results_file or not os.path.exists(results_file):
        return jsonify({"error": "Файл с результатами не найден"}), 404
        
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

def main():
    """Основная функция для запуска веб-сервера."""
    parser = argparse.ArgumentParser(description='Веб-интерфейс для просмотра статистики разработчиков Git.')
    parser.add_argument('--results-file', required=True, help='Путь к JSON-файлу с результатами анализа')
    parser.add_argument('--host', default='127.0.0.1', help='Хост для запуска сервера')
    parser.add_argument('--port', type=int, default=5000, help='Порт для запуска сервера')
    parser.add_argument('--debug', action='store_true', help='Запустить сервер в режиме отладки')
    
    args = parser.parse_args()
    
    global results_file
    results_file = args.results_file
    
    if not os.path.exists(results_file):
        print(f"Ошибка: Файл {results_file} не существует")
        return 1
        
    print(f"Запуск веб-сервера на http://{args.host}:{args.port}/")
    print(f"Используется файл результатов: {results_file}")
    
    app.run(host=args.host, port=args.port, debug=args.debug)
    
if __name__ == "__main__":
    main()
