import json
import datetime
from collections import defaultdict

class JSONOutputGenerator:
    def __init__(self, analysis_results):
        self.analysis_results = analysis_results
        
    def generate_output(self, output_file, custom_weights=None, excluded_developers=None):
        """
        Генерирует JSON-вывод из результатов анализа.
        
        Args:
            output_file (str): Путь к выходному JSON-файлу
            custom_weights (dict, optional): Пользовательские веса для расчета рейтинга полезности
            excluded_developers (list, optional): Список email разработчиков, которых нужно исключить из отчета
        """
        print(f"Формируем вывод в {output_file}...")
        
        # Фильтруем разработчиков, если указан список исключений
        developers_data = self.analysis_results.copy()
        if excluded_developers:
            print(f"Исключаем разработчиков из отчета: {', '.join(excluded_developers)}")
            for dev_email in excluded_developers:
                if dev_email in developers_data:
                    print(f"  - Исключен: {developers_data[dev_email]['name']} <{dev_email}>")
                    developers_data.pop(dev_email)
                else:
                    print(f"  - Предупреждение: разработчик {dev_email} не найден в данных")
        
        # Подготавливаем данные для JSON-сериализации
        output_data = {
            'metadata': {
                'generated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'developer_count': len(developers_data),
                'excluded_developers': excluded_developers or []
            },
            'developers': developers_data
        }
        
        # Рассчитываем статистику на уровне команды
        print("Расчет статистики на уровне команды...")
        team_stats = self._calculate_team_stats(excluded_developers)
        output_data['team_stats'] = team_stats
        
        # Добавляем рейтинг полезности
        print("Расчет рейтинга полезности разработчиков...")
        output_data['usefulness_rating'] = self._calculate_usefulness_rating(custom_weights)
        
        # Добавляем использованные веса для расчета рейтинга
        default_weights = {
            'substantial_commits': 0.3,
            'lines': 0.15,
            'impact': 0.25,
            'substantive_ratio': 0.2,
            'revert_penalty': -0.1,
            'daily_activity': 0.2
        }
        
        weights_used = default_weights.copy()
        if custom_weights:
            weights_used.update(custom_weights)
            
        output_data['weights_used'] = weights_used
        
        # Записываем в JSON-файл
        print(f"Записываем результаты в файл {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
            
        print(f"Данные успешно сохранены в {output_file}")
        return output_data

    def _calculate_team_stats(self, excluded_developers=None):
        """
        Рассчитывает статистику на уровне команды.
        
        Args:
            excluded_developers (list, optional): Список email разработчиков, которых нужно исключить из расчетов
        """
        print("Рассчитываем статистику для команды...")
        team_stats = {
            'total_commits': 0,
            'total_substantial_commits': 0,
            'total_lines_added': 0,
            'total_lines_removed': 0,
            'total_files_modified': set(),
            'total_file_types': set(),
            'average_commit_impact': 0,
            'commit_distribution': {},
            'most_active_developer': None,
            'most_impactful_developer': None,
            'most_prolific_developer': None,  # Наибольшее количество строк
        }
        
        # Создаем копию результатов анализа с исключением разработчиков, если нужно
        analysis_results = self.analysis_results.copy()
        if excluded_developers:
            for dev_email in excluded_developers:
                if dev_email in analysis_results:
                    analysis_results.pop(dev_email)
        
        # Агрегируем статистику
        print("Агрегируем статистику по разработчикам...")
        for dev_id, stats in analysis_results.items():
            team_stats['total_commits'] += stats['total_commits']
            team_stats['total_substantial_commits'] += stats['substantial_commits']
            team_stats['total_lines_added'] += stats['lines_added']
            team_stats['total_lines_removed'] += stats['lines_removed']
            team_stats['total_files_modified'].update(stats['files_modified'])
            team_stats['total_file_types'].update(stats['file_types_modified'])
            
            # Агрегируем распределение коммитов
            for month, count in stats['commit_distribution'].items():
                team_stats['commit_distribution'][month] = team_stats['commit_distribution'].get(month, 0) + count
        
        print(f"Всего коммитов: {team_stats['total_commits']}")
        print(f"Существенных коммитов: {team_stats['total_substantial_commits']}")
        print(f"Всего строк добавлено: {team_stats['total_lines_added']}")
        print(f"Всего строк удалено: {team_stats['total_lines_removed']}")
        print(f"Всего файлов изменено: {len(team_stats['total_files_modified'])}")
        print(f"Типов файлов: {len(team_stats['total_file_types'])}")
                
        # Находим наиболее активных и влиятельных разработчиков
        print("Определяем ключевых разработчиков...")
        most_active = None
        most_active_commits = 0
        most_impactful = None
        most_impact = 0
        most_prolific = None
        most_lines = 0
        
        for dev_id, stats in analysis_results.items():
            if stats['total_commits'] > most_active_commits:
                most_active_commits = stats['total_commits']
                most_active = dev_id
                
            if stats['commit_impact'] > most_impact:
                most_impact = stats['commit_impact']
                most_impactful = dev_id
                
            if stats['lines_added'] > most_lines:
                most_lines = stats['lines_added']
                most_prolific = dev_id
        
        if most_active:
            print(f"Наиболее активный разработчик: {analysis_results[most_active]['name']} - {most_active_commits} коммитов")
            team_stats['most_active_developer'] = {
                'id': most_active,
                'name': analysis_results[most_active]['name'],
                'commits': most_active_commits
            }
        
        if most_impactful:
            print(f"Наиболее влиятельный разработчик: {analysis_results[most_impactful]['name']} - {most_impact:.2f} влияние")
            team_stats['most_impactful_developer'] = {
                'id': most_impactful,
                'name': analysis_results[most_impactful]['name'],
                'impact': most_impact
            }
        
        if most_prolific:
            print(f"Наиболее продуктивный разработчик: {analysis_results[most_prolific]['name']} - {most_lines} строк добавлено")
            team_stats['most_prolific_developer'] = {
                'id': most_prolific,
                'name': analysis_results[most_prolific]['name'],
                'lines_added': most_lines
            }
        
        # Рассчитываем среднее влияние коммита
        if team_stats['total_commits'] > 0:
            total_impact = sum(stats['commit_impact'] for stats in analysis_results.values())
            team_stats['average_commit_impact'] = total_impact / team_stats['total_commits']
            print(f"Среднее влияние коммита: {team_stats['average_commit_impact']:.2f}")
            
        # Преобразуем множества в списки для JSON-сериализации
        team_stats['total_files_modified'] = list(team_stats['total_files_modified'])
        team_stats['total_file_types'] = list(team_stats['total_file_types'])
        
        return team_stats
        
    def _calculate_usefulness_rating(self, custom_weights=None):
        """
        Рассчитывает рейтинг полезности для каждого разработчика.
        Учитывает множество факторов с настраиваемыми весами.
        
        Args:
            custom_weights (dict, optional): Пользовательские веса для параметров. 
                                            По умолчанию используются предустановленные веса.
        """
        usefulness_rating = {}
        
        # Устанавливаем веса по умолчанию
        default_weights = {
            'substantial_commits': {
                'weight': 0.3,
                'description': 'Коммиты с существенными изменениями. Отражает способность разработчика делать осмысленные, значимые изменения.'
            },
            'lines': {
                'weight': 0.15, 
                'description': 'Общее количество строк, добавленных и удаленных. Отражает объем выполненной работы.'
            },
            'impact': {
                'weight': 0.25,
                'description': 'Влияние коммитов на кодовую базу. Учитывает как количество измененных файлов, так и объем изменений.'
            },
            'substantive_ratio': {
                'weight': 0.2,
                'description': 'Доля существенных коммитов к общему числу. Отражает качество и значимость вносимых изменений.'
            },
            'revert_penalty': {
                'weight': -0.1,
                'description': 'Штраф за отмену коммитов (revert). Отражает стабильность и надежность вносимых изменений.'
            },
            'daily_activity': {
                'weight': 0.2,
                'description': 'Регулярность и стабильность активности. Учитывает равномерность вклада во времени.'
            },
            'merge_penalty': {
                'weight': -0.05,
                'description': 'Штраф за merge-коммиты. Отражает работу по интеграции чужого кода.'
            }
        }
        
        # Применяем пользовательские веса, если они предоставлены
        weights = default_weights.copy()
        if custom_weights:
            for param, value in custom_weights.items():
                if param in weights:
                    weights[param]['weight'] = float(value)
                    print(f"Установлен пользовательский вес для {param}: {value}")
        
        # Создаем словарь только с весами для расчетов
        weight_values = {param: info['weight'] for param, info in weights.items()}
            
        # Получаем максимальные значения для нормализации
        max_substantial_commits = max((dev['substantial_commits'] for dev in self.analysis_results.values()), default=1)
        max_lines = max((dev['lines_added'] + dev['lines_removed'] for dev in self.analysis_results.values()), default=1)
        max_impact = max((dev['commit_impact'] for dev in self.analysis_results.values()), default=1)
        max_active_days = max((dev.get('active_days', 1) for dev in self.analysis_results.values()), default=1)
        
        print(f"Расчет рейтинга полезности с следующими весами:")
        for param, info in weights.items():
            print(f"  - {param}: {info['weight']} ({info['description']})")
        
        for dev_id, stats in self.analysis_results.items():
            print(f"Расчет рейтинга для разработчика: {stats['name']} <{dev_id}>")
            
            # Нормализуем значения от 0 до 1
            substantial_commits_norm = stats['substantial_commits'] / max_substantial_commits if max_substantial_commits > 0 else 0
            lines_norm = (stats['lines_added'] + stats['lines_removed']) / max_lines if max_lines > 0 else 0
            impact_norm = stats['commit_impact'] / max_impact if max_impact > 0 else 0
            
            # Рассчитываем соотношение существенных коммитов
            substantive_ratio = stats['substantial_commits'] / stats['total_commits'] if stats['total_commits'] > 0 else 0
            
            # Нормализуем количество revert-коммитов (отрицательный фактор)
            revert_penalty = stats['reverts_count'] / stats['total_commits'] if stats['total_commits'] > 0 else 0
            
            # Нормализуем количество merge-коммитов (отрицательный фактор)
            merge_penalty = stats.get('merge_count', 0) / stats['total_commits'] if stats['total_commits'] > 0 else 0
            
            # Нормализуем активность по времени (коммиты в день)
            active_days = stats.get('active_days', 1)
            daily_activity = (stats['total_commits'] / active_days) / (max_active_days / active_days) if active_days > 0 else 0
            
            # Рассчитываем итоговый рейтинг (с весами)
            usefulness_score = (
                substantial_commits_norm * weight_values['substantial_commits'] +
                lines_norm * weight_values['lines'] +
                impact_norm * weight_values['impact'] +
                substantive_ratio * weight_values['substantive_ratio'] +
                revert_penalty * weight_values['revert_penalty'] +
                daily_activity * weight_values['daily_activity']
            )
            
            # Добавляем штраф за merge-коммиты, если указан
            if 'merge_penalty' in weight_values:
                usefulness_score += merge_penalty * weight_values['merge_penalty']
            
            print(f"  - Итоговый рейтинг перед нормализацией: {usefulness_score}")
            
            # Нормализуем до 100
            normalized_score = round(usefulness_score * 100, 2)
            print(f"  - Нормализованный рейтинг (0-100): {normalized_score}")
            
            # Сохраняем значения факторов и рейтинг
            usefulness_rating[dev_id] = {
                'score': normalized_score,
                'factors': {
                    'substantial_commits': round(substantial_commits_norm * 100, 2),
                    'lines_contributed': round(lines_norm * 100, 2),
                    'commit_impact': round(impact_norm * 100, 2),
                    'substantive_ratio': round(substantive_ratio * 100, 2),
                    'revert_penalty': round(revert_penalty * 100, 2),
                    'daily_activity': round(daily_activity * 100, 2),
                    'merge_penalty': round(merge_penalty * 100, 2)
                },
                'factor_descriptions': {
                    param: info['description'] for param, info in weights.items()
                }
            }
        
        # Сортируем по убыванию рейтинга
        return dict(sorted(usefulness_rating.items(), key=lambda x: x[1]['score'], reverse=True))
