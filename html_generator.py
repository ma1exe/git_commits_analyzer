#!/usr/bin/env python3
import os
import json
import shutil
from datetime import datetime

class HTMLGenerator:
    """
    Генератор HTML-отчетов по статистике разработчиков Git без использования веб-сервера.
    Встраивает CSS и JS непосредственно в HTML-файл.
    """
    
    def __init__(self, json_file, output_dir=None, html_filename=None):
        """
        Инициализация генератора HTML.
        
        :param json_file: Путь к JSON-файлу с результатами анализа
        :param output_dir: Директория для сохранения HTML-отчета (если None, используется директория JSON-файла)
        :param html_filename: Имя HTML-файла (если None, то используется имя JSON-файла с расширением .html)
        """
        self.json_file = json_file
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Определяем директорию для вывода
        if output_dir is None:
            # Используем директорию JSON-файла
            self.output_dir = os.path.dirname(os.path.abspath(json_file))
        else:
            self.output_dir = output_dir
            
        # Определяем имя выходного HTML-файла
        if html_filename:
            self.html_filename = html_filename
        else:
            # Используем имя JSON-файла, заменяя расширение на .html
            base_name = os.path.basename(json_file)
            name_without_ext = os.path.splitext(base_name)[0]
            self.html_filename = name_without_ext + ".html"
            
        self.data = None
        print(f"HTML-генератор инициализирован. JSON-файл: {json_file}, HTML-файл: {os.path.join(self.output_dir, self.html_filename)}")        

    def generate(self):
        """
        Генерирует HTML-отчет со встроенными CSS и JS.
        """
        print(f"Генерация HTML-отчета в директории {self.output_dir}...")
        
        # Загружаем данные из JSON
        self._load_data()
        
        # Создаем выходную директорию, если она не существует
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        # Создаем HTML-файл
        self._generate_html()
        
        print(f"HTML-отчет успешно сгенерирован в {self.output_dir}")
        print(f"Откройте {os.path.join(self.output_dir, self.html_filename)} в вашем браузере")
        
    def _load_data(self):
        """
        Загружает данные из JSON-файла.
        """
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except Exception as e:
            raise Exception(f"Ошибка при загрузке JSON: {str(e)}")
    
    def _get_css_content(self):
        """
        Собирает содержимое всех CSS файлов в один блок.
        """
        css_files = [
            "main.css",
            "charts.css",
            "developer-cards.css",
            "advanced-metrics.css"
        ]
        
        css_content = "/* Compiled CSS */\n"
        
        # Ищем CSS в static/css/
        css_dir = os.path.join(self.current_dir, "static", "css")
        
        for css_file in css_files:
            file_path = os.path.join(css_dir, css_file)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        css_content += f"\n/* {css_file} */\n{content}\n"
                except Exception as e:
                    print(f"Ошибка при чтении CSS файла {css_file}: {str(e)}")
            else:
                print(f"Файл {css_file} не найден, пропускаем")
        
        return css_content
    
    def _get_js_content(self):
        """
        Собирает содержимое всех JS файлов в один блок.
        Файлы загружаются в определенном порядке для обеспечения правильной работы.
        """
        # Порядок загрузки JS файлов имеет значение из-за зависимостей
        js_files = [
            "core.js",
            "utils.js",
            "team-stats.js",
            "developer-stats.js",
            "charts.js",
            "visibility-controls.js",
            "advanced-metrics.js",
            "main.js"
        ]
        
        js_content = "/* Compiled JavaScript */\n"
        
        # Ищем JavaScript в static/js/
        js_dir = os.path.join(self.current_dir, "static", "js")
        
        for js_file in js_files:
            file_path = os.path.join(js_dir, js_file)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        js_content += f"\n/* {js_file} */\n{content}\n"
                except Exception as e:
                    print(f"Ошибка при чтении JS файла {js_file}: {str(e)}")
            else:
                print(f"Файл {js_file} не найден, пропускаем")
        
        return js_content
    
    def _get_html_template(self):
        """
        Получает шаблон HTML.
        """
        template_path = os.path.join(self.current_dir, "templates", "index.html")
        
        if os.path.exists(template_path):
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"Ошибка при чтении шаблона HTML: {str(e)}")
                return self._get_default_html_template()
        else:
            print(f"Шаблон HTML не найден, используем встроенный шаблон")
            return self._get_default_html_template()
    
    def _get_default_html_template(self):
        """
        Возвращает встроенный шаблон HTML для случая, когда внешний шаблон недоступен.
        """
        return """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Статистика продуктивности разработчиков Git</title>
    
    <!-- Встроенные стили -->
    <style>
    /* CSS_PLACEHOLDER */
    </style>
    
    <!-- Chart.js для визуализации данных -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js"></script>
</head>
<body>
    <div class="container">
        <h1>Статистика продуктивности разработчиков Git</h1>
        
        <!-- Контейнер для сообщений об ошибках -->
        <div id="error-container" style="display: none;">
            <div class="error-message" id="error-message"></div>
        </div>
        
        <!-- Метаданные -->
        <div id="metadata" class="section"></div>
        
        <!-- Общая статистика команды -->
        <div id="team-stats" class="section"></div>
        
        <!-- Графики -->
        <div class="chart-section">
            <h2>Визуализация данных</h2>
            
            <div class="chart-container">
                <h3>Коммиты разработчиков</h3>
                <div id="commit-chart"></div>
            </div>
            
            <div class="chart-container">
                <h3>Влияние и вклад</h3>
                <div id="impact-chart"></div>
            </div>
            
            <div class="chart-container">
                <h3>Активность по времени</h3>
                <div id="timeline-chart"></div>
            </div>
        </div>
        
        <!-- Рейтинг полезности разработчиков -->
        <div id="usefulness-rating" class="section"></div>
        
        <!-- Детальная статистика по разработчикам -->
        <div id="developer-stats" class="section"></div>
        
        <div class="footer">
            <p>Сгенерировано анализатором продуктивности Git <!-- GENERATION_DATE_PLACEHOLDER --></p>
        </div>
    </div>
    
    <!-- Встраиваем данные JSON прямо в HTML для автономной работы -->
    <script>
        window.gitAnalysisData = /* JSON_DATA_PLACEHOLDER */;
    </script>
    
    <!-- Встроенный JavaScript -->
    <script>
    /* JS_PLACEHOLDER */
    </script>
</body>
</html>"""
    
    def _generate_html(self):
        """
        Генерирует основной HTML-файл с встроенными CSS и JS.
        """
        if not self.data:
            raise Exception("Данные не загружены")
        
        # Получаем шаблон HTML
        html_template = self._get_html_template()
        
        # Получаем содержимое CSS и JS
        css_content = self._get_css_content()
        js_content = self._get_js_content()
        
        # Заменяем плейсхолдеры в шаблоне
        html_content = html_template.replace('/* CSS_PLACEHOLDER */', css_content)
        html_content = html_content.replace('/* JS_PLACEHOLDER */', js_content)
        
        # Заменяем плейсхолдер JSON данных
        json_data_str = json.dumps(self.data, ensure_ascii=False)
        html_content = html_content.replace('/* JSON_DATA_PLACEHOLDER */', json_data_str)
        
        # Обновляем дату генерации
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        html_content = html_content.replace('<!-- GENERATION_DATE_PLACEHOLDER -->', current_datetime)
        
        # Путь к HTML-файлу
        html_file = os.path.join(self.output_dir, self.html_filename)
        print(f"Генерация HTML-файла: {html_file}")
        
        # Записываем HTML в файл
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)