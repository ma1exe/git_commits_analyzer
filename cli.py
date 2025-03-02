#!/usr/bin/env python3
"""
Командный интерфейс для Git Developer Productivity Analyzer.
Предоставляет быстрый доступ к функциональности анализатора без GUI.
"""

import argparse
import os
import sys
import logging
from git_collector import GitDataCollector
from analyzer import DevActivityAnalyzer
from output_generator import JSONOutputGenerator
from html_generator import HTMLGenerator
import config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Основная функция для запуска анализа через командную строку"""
    parser = argparse.ArgumentParser(
        description='Git Developer Productivity Analyzer - CLI',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Основные параметры
    parser.add_argument('--repo-path', required=True, help='Путь к Git-репозиторию для анализа')
    parser.add_argument('--output-file', default='developer_stats.json', help='Путь к выходному JSON-файлу')
    
    # Параметры анализа
    parser.add_argument('--ignore-reverts', action='store_true', help='Игнорировать revert-коммиты')
    parser.add_argument('--start-date', help='Начальная дата для анализа (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='Конечная дата для анализа (YYYY-MM-DD)')
    parser.add_argument('--min-changes', type=int, default=5, help='Минимальное количество изменений для существенного коммита')
    
    # Параметры HTML-отчета
    parser.add_argument('--generate-html', action='store_true', help='Генерировать HTML-отчет')
    parser.add_argument('--html-output-dir', default='git_stats_report', help='Директория для сохранения HTML-отчета')
    parser.add_argument('--inline-html', action='store_true', 
                       help='Создать автономный HTML с встроенными CSS/JS (рекомендуется для локального просмотра)')
    
    # Исключение разработчиков
    parser.add_argument('--exclude-developers', nargs='+', 
                       help='Список email разработчиков, которых нужно исключить из отчета')
    
    # Настройки логирования
    parser.add_argument('--verbose', '-v', action='store_true', help='Включить подробное логирование')
    parser.add_argument('--log-file', help='Файл для сохранения лога')
    
    # Опция загрузки весов из файла
    parser.add_argument('--weights-file', help='JSON-файл с весами параметров')
    
    # Веса параметров
    weight_group = parser.add_argument_group('Параметры весов для расчета полезности')
    weight_group.add_argument('--weight-substantial-commits', type=float, default=0.3,
                            help='Вес для существенных коммитов')
    weight_group.add_argument('--weight-lines', type=float, default=0.15,
                            help='Вес для общего количества строк')
    weight_group.add_argument('--weight-impact', type=float, default=0.25,
                            help='Вес для влияния коммитов')
    weight_group.add_argument('--weight-substantive-ratio', type=float, default=0.2,
                            help='Вес для соотношения существенных коммитов')
    weight_group.add_argument('--weight-revert-penalty', type=float, default=-0.1,
                            help='Вес для штрафа за revert-коммиты')
    weight_group.add_argument('--weight-daily-activity', type=float, default=0.2,
                            help='Вес для ежедневной активности')
    
    args = parser.parse_args()
    
    # Настройка логирования
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    if args.log_file:
        file_handler = logging.FileHandler(args.log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)
    
    # Проверяем существование репозитория
    if not os.path.exists(args.repo_path):
        logger.error(f"Ошибка: путь к репозиторию не существует: {args.repo_path}")
        return 1
    
    if not os.path.exists(os.path.join(args.repo_path, '.git')):
        logger.error(f"Ошибка: указанная директория не является Git-репозиторием: {args.repo_path}")
        return 1
    
    # Настраиваем конфигурацию
    config.IGNORE_REVERTS = args.ignore_reverts
    config.REPO_PATH = args.repo_path
    config.OUTPUT_FILE = args.output_file
    config.START_DATE = args.start_date
    config.END_DATE = args.end_date
    config.MIN_CODE_CHANGE_SIZE = args.min_changes
    
    # Создаем директорию для выходного файла, если она не существует
    output_dir = os.path.dirname(os.path.abspath(args.output_file))
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"Начинаем анализ репозитория: {args.repo_path}")
    
    try:
        # Собираем данные из Git
        collector = GitDataCollector(args.repo_path)
        git_data = collector.collect_data()
        
        logger.info(f"Собрано {len(git_data['commits'])} коммитов")
        
        # Анализируем данные
        analyzer = DevActivityAnalyzer(git_data)
        analysis_results = analyzer.analyze()
        
        logger.info(f"Проанализировано {len(analysis_results)} разработчиков")
        
        # Загружаем веса из файла, если указан
        custom_weights = {}
        if args.weights_file:
            try:
                import json
                with open(args.weights_file, 'r', encoding='utf-8') as f:
                    file_weights = json.load(f)
                    custom_weights.update(file_weights)
                    logger.info(f"Загружены веса из файла: {args.weights_file}")
            except Exception as e:
                logger.error(f"Ошибка при загрузке весов из файла: {str(e)}")
        
        # Добавляем веса из аргументов командной строки (перезаписывают загруженные из файла)
        if args.weight_substantial_commits != 0.3:
            custom_weights['substantial_commits'] = args.weight_substantial_commits
        if args.weight_lines != 0.15:
            custom_weights['lines'] = args.weight_lines
        if args.weight_impact != 0.25:
            custom_weights['impact'] = args.weight_impact
        if args.weight_substantive_ratio != 0.2:
            custom_weights['substantive_ratio'] = args.weight_substantive_ratio
        if args.weight_revert_penalty != -0.1:
            custom_weights['revert_penalty'] = args.weight_revert_penalty
        if args.weight_daily_activity != 0.2:
            custom_weights['daily_activity'] = args.weight_daily_activity
        
        # Выводим информацию о пользовательских весах
        if custom_weights:
            logger.info("Используются пользовательские веса для расчета рейтинга полезности:")
            for param, value in custom_weights.items():
                logger.info(f"  - {param}: {value}")
        else:
            logger.info("Используются стандартные веса для расчета рейтинга полезности")
        
        # Генерируем выходные данные
        output_generator = JSONOutputGenerator(analysis_results)
        output_data = output_generator.generate_output(
            args.output_file, 
            custom_weights=custom_weights if custom_weights else None,
            excluded_developers=args.exclude_developers
        )
        
        logger.info(f"Анализ завершен. Результаты сохранены в {args.output_file}")
        
        # Генерируем HTML-отчет, если это запрошено
        if args.generate_html:
            # Определяем имя HTML-файла на основе имени JSON-файла
            base_name = os.path.basename(args.output_file)
            name_without_ext = os.path.splitext(base_name)[0]
            html_filename = name_without_ext + ".html"
            
            logger.info(f"Генерируем HTML-отчет с именем {html_filename}")
            
            html_gen = HTMLGenerator(
                args.output_file, 
                args.html_output_dir,
                html_filename=html_filename
            )
            html_gen.generate()
        
        return 0
    
    except Exception as e:
        logger.error(f"Ошибка при выполнении анализа: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())