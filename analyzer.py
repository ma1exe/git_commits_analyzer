from collections import defaultdict
from datetime import datetime
import os
import re
import config

class DevActivityAnalyzer:
    def __init__(self, git_data):
        self.git_data = git_data
        self.commits = git_data['commits']
        self.commit_details = git_data['commit_details']
        self.file_changes = git_data['file_changes']
        self.developer_info = git_data['developer_info']
        
    def analyze(self):
        """Анализ данных из Git и возврат статистики по разработчикам."""
        print("Анализируем активность разработчиков...")
        
        # Инициализируем структуры данных
        developer_stats = defaultdict(lambda: {
            'name': '',
            'email': '',
            'first_commit_date': None,
            'last_commit_date': None,
            'active_days': 0,
            'total_commits': 0,
            'substantial_commits': 0,
            'lines_added': 0,
            'lines_removed': 0,
            'files_modified': set(),
            'file_types_modified': set(),
            'file_categories': defaultdict(int),
            'commit_impact': 0,
            'commit_distribution': defaultdict(int),  # Распределение по месяцам/годам
            'code_churn': 0,  # Добавленные + удаленные строки
            'net_contribution': 0,  # Добавленные - удаленные строки
            'commit_subjects': [],
            'average_commit_size': 0,
            'reverts_count': 0,
            'merge_count': 0,  # Количество merge-коммитов
            'most_modified_files': defaultdict(int),
            'squash_count': 0,  # Примерное количество squash-коммитов
        })
        
        # Анализируем каждый коммит
        for commit in self.commits:
            self._analyze_commit(commit, developer_stats)
            
        # Рассчитываем производные метрики и завершаем статистику
        for dev_id, stats in developer_stats.items():
            # Используем информацию о разработчике
            dev_info = self.developer_info.get(dev_id, {})
            
            # Устанавливаем даты первого и последнего коммита
            if dev_info:
                stats['first_commit_date'] = dev_info.get('first_commit_date', stats['first_commit_date'])
                stats['last_commit_date'] = dev_info.get('last_commit_date', stats['last_commit_date'])
            
            # Преобразуем множества файлов в списки для JSON-сериализации
            stats['files_modified'] = list(stats['files_modified'])
            stats['file_types_modified'] = list(stats['file_types_modified'])
            
            # Наиболее часто изменяемые файлы (топ-10)
            stats['most_modified_files'] = dict(sorted(
                stats['most_modified_files'].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10])
            
            # Рассчитываем средний размер коммита
            if stats['total_commits'] > 0:
                stats['average_commit_size'] = (stats['lines_added'] + stats['lines_removed']) / stats['total_commits']
                
            # Рассчитываем нормализованные метрики на основе активного периода
            if stats['first_commit_date'] and stats['last_commit_date']:
                # Получаем объекты даты
                first_date = datetime.strptime(stats['first_commit_date'], '%Y-%m-%d %H:%M:%S')
                last_date = datetime.strptime(stats['last_commit_date'], '%Y-%m-%d %H:%M:%S')
                
                # Рассчитываем активный период в днях
                active_days = (last_date - first_date).days + 1  # +1, чтобы избежать деления на ноль для коммитов в один день
                stats['active_days'] = active_days
                
                if active_days > 0:
                    stats['commits_per_day'] = stats['total_commits'] / active_days
                    stats['lines_per_day'] = (stats['lines_added'] + stats['lines_removed']) / active_days
                else:
                    stats['commits_per_day'] = stats['total_commits']
                    stats['lines_per_day'] = stats['lines_added'] + stats['lines_removed']
            
            # Преобразуем defaultdict в обычный dict для JSON-сериализации
            stats['commit_distribution'] = dict(stats['commit_distribution'])
            stats['file_categories'] = dict(stats['file_categories'])
            
            # Обнаруживаем потенциальные squash-коммиты
            # (простая эвристика: коммиты с большим количеством файлов и изменений)
            potential_squashes = sum(1 for subject in stats['commit_subjects'] 
                                    if ('merge' in subject.lower() or 'squash' in subject.lower()))
            stats['squash_count'] = potential_squashes
            
            # Ограничиваем количество сохраняемых тем коммитов (чтобы не перегружать JSON)
            if len(stats['commit_subjects']) > 20:
                stats['commit_subjects'] = stats['commit_subjects'][:20]
            
        return dict(developer_stats)
    
    def _analyze_commit(self, commit, developer_stats):
        """Анализ одного коммита и обновление статистики разработчика."""
        dev_id = commit['author_email'].lower()  # Используем email как ID разработчика
        
        # Получаем или инициализируем статистику разработчика
        dev_stats = developer_stats[dev_id]
        
        # Устанавливаем или обновляем базовую информацию
        dev_stats['name'] = commit['author_name']
        dev_stats['email'] = commit['author_email']
        
        # Обновляем счетчик коммитов
        dev_stats['total_commits'] += 1
        
        # Если это revert-коммит, увеличиваем счетчик
        if commit['is_revert']:
            dev_stats['reverts_count'] += 1
            
        # Если это merge-коммит, увеличиваем счетчик
        if commit.get('is_merge', False):
            dev_stats['merge_count'] += 1
        
        # Обновляем темы коммитов
        dev_stats['commit_subjects'].append(commit['subject'])
        
        # Обновляем даты коммитов
        commit_date = commit['date']
        if not dev_stats['first_commit_date'] or commit_date < dev_stats['first_commit_date']:
            dev_stats['first_commit_date'] = commit_date
        if not dev_stats['last_commit_date'] or commit_date > dev_stats['last_commit_date']:
            dev_stats['last_commit_date'] = commit_date
            
        # Обновляем распределение коммитов (по месяцам/годам)
        commit_date_obj = datetime.strptime(commit_date, '%Y-%m-%d %H:%M:%S')
        month_year = commit_date_obj.strftime('%Y-%m')
        dev_stats['commit_distribution'][month_year] += 1
        
        # Получаем детали коммита и изменения файлов
        commit_hash = commit['hash']
        commit_detail = self.commit_details.get(commit_hash, {})
        commit_files = self.file_changes.get(commit_hash, [])
        
        # Обновляем добавленные/удаленные строки
        stats = commit_detail.get('stats', {})
        dev_stats['lines_added'] += stats.get('insertions', 0)
        dev_stats['lines_removed'] += stats.get('deletions', 0)
        
        # Обновляем code churn и net contribution
        dev_stats['code_churn'] += stats.get('insertions', 0) + stats.get('deletions', 0)
        dev_stats['net_contribution'] += stats.get('insertions', 0) - stats.get('deletions', 0)
        
        # Проверяем, является ли этот коммит существенным
        substantial_change = False
        for file_change in commit_files:
            # Добавляем файл в модифицированные файлы
            file_path = file_change['file_path']
            dev_stats['files_modified'].add(file_path)
            
            # Обновляем счетчик изменений для этого файла
            dev_stats['most_modified_files'][file_path] += 1
            
            # Извлекаем расширение файла
            ext = file_change.get('file_ext', '')
            if ext:
                dev_stats['file_types_modified'].add(ext)
                
                # Определяем категорию файла
                if ext in config.CODE_FILE_EXTENSIONS:
                    dev_stats['file_categories']['code'] += 1
                elif ext in config.MARKUP_FILE_EXTENSIONS:
                    dev_stats['file_categories']['markup'] += 1
                elif ext in config.STYLE_FILE_EXTENSIONS:
                    dev_stats['file_categories']['style'] += 1
                elif ext in config.CONFIG_FILE_EXTENSIONS:
                    dev_stats['file_categories']['config'] += 1
                else:
                    dev_stats['file_categories']['other'] += 1
                
            # Проверяем, является ли изменение существенным
            if file_change.get('is_substantial', False):
                substantial_change = True
                
        if substantial_change:
            dev_stats['substantial_commits'] += 1
            
        # Рассчитываем влияние коммита (может быть уточнено более сложными метриками)
        # Простая формула: (изменено файлов) * (добавлено + удалено строк)
        impact = stats.get('files_changed', 0) * (stats.get('insertions', 0) + stats.get('deletions', 0))
        dev_stats['commit_impact'] += impact

    def _calculate_file_complexity(self, file_path):
        """
        Рассчитывает примерную сложность файла на основе его типа.
        Более высокий балл = более сложный файл.
        """
        # Сложность по умолчанию
        complexity = 1.0
        
        # Настраиваем на основе типа файла
        ext = os.path.splitext(file_path)[1].lower()
        
        # Считаем определенные типы файлов более сложными, чем другие
        complexity_multipliers = {
            '.py': 1.2,    # Python файлы
            '.js': 1.1,    # JavaScript файлы
            '.java': 1.3,  # Java файлы
            '.cpp': 1.4,   # C++ файлы
            '.c': 1.3,     # C файлы
            '.h': 1.1,     # Header файлы
            '.rb': 1.2,    # Ruby файлы
            '.go': 1.2,    # Go файлы
            '.php': 1.2,   # PHP файлы
            '.html': 0.8,  # HTML файлы
            '.css': 0.8,   # CSS файлы
            '.md': 0.5,    # Markdown файлы
            '.txt': 0.5,   # Text файлы
            '.json': 0.7,  # JSON файлы
            '.xml': 0.8,   # XML файлы
            '.yaml': 0.7,  # YAML файлы
            '.yml': 0.7,   # YAML файлы
        }
        
        if ext in complexity_multipliers:
            complexity *= complexity_multipliers[ext]
            
        return complexity
