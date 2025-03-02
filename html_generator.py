#!/usr/bin/env python3
import os
import json
import shutil
from datetime import datetime

class HTMLGenerator:
    """
    Генератор HTML-отчетов по статистике разработчиков Git без использования веб-сервера.
    """
    
    def __init__(self, json_file, output_dir=None, html_filename=None):
        """
        Инициализация генератора HTML.
        
        :param json_file: Путь к JSON-файлу с результатами анализа
        :param output_dir: Директория для сохранения HTML-отчета (если None, используется директория JSON-файла)
        :param html_filename: Имя HTML-файла (если None, то используется имя JSON-файла с расширением .html)
        """
        self.json_file = json_file
        
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
        Генерирует полный HTML-отчет со всеми необходимыми файлами.
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
        print(f"Откройте {os.path.join(self.output_dir, 'index.html')} в вашем браузере")
        
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
        Получает содержимое CSS файла или возвращает стандартный CSS, если файл не найден.
        """
        # Определяем путь к CSS файлу
        current_dir = os.path.dirname(os.path.abspath(__file__))
        css_file = os.path.join(current_dir, "static", "style.css")
        
        # Если файл существует, читаем его содержимое
        if os.path.exists(css_file):
            try:
                with open(css_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"Ошибка при чтении CSS файла: {str(e)}")
                
        # Если файл не найден или произошла ошибка чтения, используем стандартный CSS
        return """
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }
        .container { max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); }
        h1, h2, h3 { color: #333; }
        h1 { border-bottom: 2px solid #eaecef; padding-bottom: 0.3em; font-size: 2em; }
        h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
        h3 { font-size: 1.2em; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 0.9em; }
        table, th, td { border: 1px solid #ddd; }
        th, td { padding: 12px; text-align: left; }
        th { background-color: #f2f2f2; position: sticky; top: 0; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .chart-container { margin: 25px 0; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 1px 5px rgba(0, 0, 0, 0.05); }
        .developer-card { margin-bottom: 20px; padding: 15px; border: 1px solid #e1e4e8; border-radius: 8px; transition: box-shadow 0.3s ease; }
        .developer-card:hover { box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); }
        .stat-value { font-weight: bold; color: #0366d6; }
        .footer { margin-top: 40px; text-align: center; color: #777; font-size: 0.9em; padding: 20px; border-top: 1px solid #eaecef; }
        .usefulness-meter { height: 20px; background-color: #e9ecef; border-radius: 10px; margin-bottom: 10px; overflow: hidden; }
        .usefulness-meter .fill { height: 100%; background: linear-gradient(90deg, #28a745, #17a2b8); border-radius: 10px; transition: width 0.5s ease; }
        .stat-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; margin: 20px 0; }
        .stat-box { background-color: #fff; border: 1px solid #e1e4e8; border-radius: 8px; padding: 15px; display: flex; flex-direction: column; }
        .stat-box .title { font-size: 0.9em; color: #586069; margin-bottom: 5px; }
        .stat-box .value { font-size: 1.6em; font-weight: 600; color: #24292e; }
        @media (max-width: 768px) { .stat-grid { grid-template-columns: 1fr; } table { display: block; overflow-x: auto; } }
        """
            
    def _get_js_content(self):
        """
        Получает содержимое JS файла или возвращает стандартный JS, если файл не найден.
        """
        # Определяем путь к JS файлу
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Сначала ищем standalone_script.js
        js_file = os.path.join(current_dir, "static", "standalone_script.js")
        
        # Если standalone_script.js не найден, ищем обычный script.js
        if not os.path.exists(js_file):
            js_file = os.path.join(current_dir, "static", "script.js")
            
        # Если файл существует, читаем его содержимое
        if os.path.exists(js_file):
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"Ошибка при чтении JS файла: {str(e)}")
                
        # Если файл не найден или произошла ошибка чтения, используем стандартный JS
        return """
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Git Developer Statistics Visualization loaded');
            
            // Загружаем данные из встроенного JSON
            const data = window.gitAnalysisData;
            if (data) {
                // Отображаем метаданные
                const metadataDiv = document.getElementById('metadata');
                if (metadataDiv && data.metadata) {
                    metadataDiv.innerHTML = `
                        <p>Сгенерировано: ${data.metadata.generated_at}</p>
                        <p>Количество разработчиков: ${data.metadata.developer_count}</p>
                    `;
                }
                
                // Отображаем статистику по разработчикам
                const developerStatsDiv = document.getElementById('developer-stats');
                if (developerStatsDiv && data.developers) {
                    let html = '<h2>Статистика по разработчикам</h2>';
                    
                    for (const [devId, stats] of Object.entries(data.developers)) {
                        html += `
                            <div class="developer-card">
                                <h3>${stats.name} &lt;${devId}&gt;</h3>
                                <p>Активность: ${stats.first_commit_date} — ${stats.last_commit_date}</p>
                                <p>Всего коммитов: ${stats.total_commits}</p>
                                <p>Существенных коммитов: ${stats.substantial_commits}</p>
                                <p>Добавлено строк: ${stats.lines_added}</p>
                                <p>Удалено строк: ${stats.lines_removed}</p>
                            </div>
                        `;
                    }
                    
                    developerStatsDiv.innerHTML = html;
                }
                
                // Если доступен Chart.js, создаем графики
                if (typeof Chart !== 'undefined') {
                    createCommitChart(data);
                }
            }
            
            // Функция для создания графика коммитов
            function createCommitChart(data) {
                const chartDiv = document.getElementById('commit-chart');
                if (!chartDiv) return;
                
                // Извлекаем данные для графика
                const developers = Object.keys(data.developers);
                const developerNames = developers.map(dev => data.developers[dev].name);
                const commitCounts = developers.map(dev => data.developers[dev].total_commits);
                
                // Создаем график с помощью Chart.js
                const ctx = document.createElement('canvas');
                chartDiv.appendChild(ctx);
                
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: developerNames,
                        datasets: [{
                            label: 'Коммиты',
                            data: commitCounts,
                            backgroundColor: 'rgba(54, 162, 235, 0.5)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: { beginAtZero: true }
                        }
                    }
                });
            }
        });
        """
            
    def _generate_html(self):
        """
        Генерирует основной HTML-файл на основе данных из JSON.
        """
        if not self.data:
            raise Exception("Данные не загружены")
            
        # Получаем содержимое CSS и JS файлов
        css_content = self._get_css_content()
        js_content = self._get_js_content()
            
        # Путь к HTML-файлу
        html_file = os.path.join(self.output_dir, self.html_filename)
        print(f"Генерация HTML-файла: {html_file}")        

        # Создаем HTML-контент со встроенными CSS и JS
        html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Статистика продуктивности разработчиков Git</title>
    
    <!-- Встроенные стили -->
    <style>
{css_content}
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
            <p>Сгенерировано анализатором продуктивности Git {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
    
    <!-- Встраиваем данные JSON прямо в HTML для автономной работы -->
    <script>
        window.gitAnalysisData = {json.dumps(self.data, ensure_ascii=False)};
    </script>
    
    <!-- Встроенный JavaScript -->
    <script>
{js_content}
    </script>
</body>
</html>
"""
        
        # Записываем HTML в файл
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)