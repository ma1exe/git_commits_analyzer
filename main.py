#!/usr/bin/env python3
import argparse
import os
from git_collector import GitDataCollector
from analyzer import DevActivityAnalyzer
from output_generator import JSONOutputGenerator
import config

def main():
    # Парсим аргументы командной строки
    parser = argparse.ArgumentParser(description='Анализ Git-репозитория для оценки продуктивности разработчиков.')
    parser.add_argument('--repo-path', required=True, help='Путь к Git-репозиторию для анализа')
    parser.add_argument('--output-file', default='developer_stats.json', help='Путь к выходному JSON-файлу')
    parser.add_argument('--ignore-reverts', action='store_true', help='Игнорировать revert-коммиты')
    parser.add_argument('--ignore-merges', action='store_true', help='Игнорировать merge-коммиты')
    parser.add_argument('--start-date', help='Начальная дата для анализа (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='Конечная дата для анализа (YYYY-MM-DD)')
    parser.add_argument('--min-changes', type=int, default=5, help='Минимальное количество изменений для существенного коммита')
    parser.add_argument('--generate-html', action='store_true', help='Генерировать HTML-отчет')
    parser.add_argument('--html-output-dir', default='git_stats_report', help='Директория для сохранения HTML-отчета')
    parser.add_argument('--inline-html', action='store_true', 
                        help='Создать автономный HTML с встроенными CSS/JS (рекомендуется для локального просмотра)')
    
    # Аргументы для весов параметров оценки эффективности
    parser.add_argument('--weight-substantial-commits', type=float, default=0.3, 
                        help='Вес для существенных коммитов (по умолчанию: 0.3)')
    parser.add_argument('--weight-lines', type=float, default=0.15, 
                        help='Вес для общего количества строк (по умолчанию: 0.15)')
    parser.add_argument('--weight-impact', type=float, default=0.25, 
                        help='Вес для влияния коммитов (по умолчанию: 0.25)')
    parser.add_argument('--weight-substantive-ratio', type=float, default=0.2, 
                        help='Вес для соотношения существенных коммитов (по умолчанию: 0.2)')
    parser.add_argument('--weight-revert-penalty', type=float, default=-0.1, 
                        help='Вес для штрафа за revert-коммиты (по умолчанию: -0.1)')
    parser.add_argument('--weight-merge-penalty', type=float, default=-0.05, 
                        help='Вес для штрафа за merge-коммиты (по умолчанию: -0.05)')
    parser.add_argument('--weight-daily-activity', type=float, default=0.2, 
                        help='Вес для ежедневной активности (по умолчанию: 0.2)')
    
    # Аргумент для исключения разработчиков из отчета
    parser.add_argument('--exclude-developers', nargs='+', 
                        help='Список email разработчиков, которых нужно исключить из отчета')
    
    args = parser.parse_args()

    # Настраиваем конфигурацию
    config.IGNORE_REVERTS = args.ignore_reverts
    config.IGNORE_MERGES = args.ignore_merges
    config.REPO_PATH = args.repo_path

    # Собираем пользовательские веса в словарь
    custom_weights = {}
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
    if args.weight_merge_penalty != -0.05:
        custom_weights['merge_penalty'] = args.weight_merge_penalty

    # Выводим информацию о пользовательских весах
    if custom_weights:
        print("Используются пользовательские веса для расчета рейтинга полезности:")
        for param, value in custom_weights.items():
            print(f"  - {param}: {value}")
    else:
        print("Используются стандартные веса для расчета рейтинга полезности")
    
    # Генерируем выходные данные
    output_generator = JSONOutputGenerator(analysis_results)
    output_data = output_generator.generate_output(
        args.output_file, 
        custom_weights=custom_weights if custom_weights else None,
        excluded_developers=args.exclude_developers
    )
    
    print(f"Анализ завершен. Результаты сохранены в {args.output_file}")
    
    # Генерируем HTML-отчет, если это запрошено
    if args.generate_html:
        # Определяем имя HTML-файла на основе имени JSON-файла
        base_name = os.path.basename(args.output_file)
        name_without_ext = os.path.splitext(base_name)[0]
        html_filename = name_without_ext + ".html"
        
        from html_generator import HTMLGenerator
        
        html_gen = HTMLGenerator(
            args.output_file, 
            args.html_output_dir,
            html_filename=html_filename
        )
        html_gen.generate()

if __name__ == "__main__":
    main()