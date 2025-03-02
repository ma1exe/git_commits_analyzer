import os
import subprocess
import re
from datetime import datetime
import config
import sys
import threading

class GitDataCollector:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.total_commits = 0  # Общее количество коммитов для отслеживания прогресса
        self.processed_commits = 0  # Количество обработанных коммитов
        
    def collect_data(self):
        """Сбор данных из Git-репозитория."""
        print("Собираем данные из Git...")
        
        # Проверяем, что путь ведет к Git-репозиторию
        if not self._is_git_repo():
            raise ValueError(f"{self.repo_path} не является Git-репозиторием")
        
        # Получаем общее количество коммитов для отслеживания прогресса
        self._count_total_commits()
        print(f"Всего коммитов в репозитории: {self.total_commits}")
        
        # Получаем все коммиты
        commits = self._get_commits()
        
        # Получаем детальную информацию по каждому коммиту
        commit_details = self._get_commit_details(commits)
        
        # Получаем изменения файлов для каждого коммита
        commit_file_changes = self._get_file_changes(commits)
        
        # Получаем данные о разработчиках (даты прихода/ухода, др.)
        developer_info = self._get_developer_info(commits)
        
        return {
            'commits': commits,
            'commit_details': commit_details,
            'file_changes': commit_file_changes,
            'developer_info': developer_info
        }
    
    def _is_git_repo(self):
        """Проверка, что указанный путь - валидный Git-репозиторий."""
        return os.path.isdir(os.path.join(self.repo_path, '.git'))
    
    def _count_total_commits(self):
        """Подсчитывает общее количество коммитов в репозитории для отслеживания прогресса."""
        try:
            cmd = ['git', 'rev-list', '--count', 'HEAD']
            if config.START_DATE:
                cmd.append(f'--since={config.START_DATE}')
            if config.END_DATE:
                cmd.append(f'--until={config.END_DATE}')
                
            result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True)
            if result.returncode == 0:
                self.total_commits = int(result.stdout.strip())
            else:
                print(f"Предупреждение: Не удалось получить общее количество коммитов: {result.stderr}")
                self.total_commits = 1000  # Значение по умолчанию
        except Exception as e:
            print(f"Ошибка при подсчете коммитов: {str(e)}")
            self.total_commits = 1000  # Значение по умолчанию
    
    def _update_progress(self, increment=1):
        """Обновляет и выводит прогресс обработки коммитов."""
        self.processed_commits += increment
        if self.total_commits > 0:
            percentage = (self.processed_commits / self.total_commits) * 100
            sys.stdout.write(f"\nПрогресс анализа: {percentage:.1f}% ({self.processed_commits}/{self.total_commits})")
            sys.stdout.flush()
            # Каждые 10% выводим новую строку для лучшей читаемости
            if self.processed_commits % max(1, self.total_commits // 10) == 0:
                print()
    
    def _get_commits(self):
        """Получение всех коммитов из репозитория."""
        # Используем нестандартный разделитель, который маловероятен в сообщениях коммитов
        separator = "<<__GIT_SEPARATOR__>>"
        cmd = ['git', 'log', f'--pretty=format:%H{separator}%an{separator}%ae{separator}%at{separator}%s']
        
        # Добавляем диапазон дат, если указан
        if config.START_DATE:
            cmd.append(f'--since={config.START_DATE}')
        if config.END_DATE:
            cmd.append(f'--until={config.END_DATE}')
        
        result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Ошибка при получении коммитов: {result.stderr}")
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            
            # Используем максимальное количество разбиений - 4, чтобы сообщение коммита осталось целым
            parts = line.split(separator, 4)
            if len(parts) < 5:
                print(f"Предупреждение: пропуск строки с неполными данными: {line}")
                continue
                
            commit_hash, author_name, author_email, timestamp, subject = parts
            
            # Проверяем, является ли коммит revert-коммитом или merge-коммитом
            is_revert = subject.startswith('Revert "') or 'revert' in subject.lower()
            is_merge = subject.startswith('Merge ') or subject.startswith('Merge: ') or 'merge' in subject.lower()
            
            # Пропускаем revert-коммиты, если настроено их игнорирование
            if is_revert and config.IGNORE_REVERTS:
                continue

            # Пропускаем merge-коммиты, если настроено их игнорирование
            if is_merge and config.IGNORE_MERGES:
                continue
                
            commits.append({
                'hash': commit_hash,
                'author_name': author_name,
                'author_email': author_email,
                'timestamp': int(timestamp),
                'date': datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S'),
                'subject': subject,
                'is_revert': is_revert,
                'is_merge': is_merge
            })
            
        return commits
    
    def _get_commit_details(self, commits):
        """Получение детальной информации по каждому коммиту."""
        commit_details = {}
        total_commits = len(commits)
        
        print(f"\nПолучение детальной информации по {total_commits} коммитам...")
        
        for i, commit in enumerate(commits):
            # Отображаем прогресс
            percentage = ((i + 1) / total_commits) * 100
            sys.stdout.write(f"\nПрогресс получения деталей: {percentage:.1f}% ({i+1}/{total_commits})")
            sys.stdout.flush()
            
            # Получаем метаданные коммита
            cmd = ['git', 'show', '--stat', '--format=fuller', commit['hash']]
            result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"\nПредупреждение: Не удалось получить детали коммита {commit['hash']}: {result.stderr}")
                continue
                
            # Парсим детали коммита
            commit_details[commit['hash']] = {
                'raw_output': result.stdout,
                'stats': self._parse_commit_stats(result.stdout)
            }
            
        print("\nПолучение деталей коммитов завершено.")
        return commit_details
    
    def _get_file_changes(self, commits):
        """Получение изменений файлов для каждого коммита."""
        file_changes = {}
        total_commits = len(commits)
        
        print(f"\nПолучение изменений файлов по {total_commits} коммитам...")
        
        for i, commit in enumerate(commits):
            # Отображаем прогресс
            percentage = ((i + 1) / total_commits) * 100
            sys.stdout.write(f"\nПрогресс получения изменений: {percentage:.1f}% ({i+1}/{total_commits})")
            sys.stdout.flush()
            
            # Получаем файлы, измененные в этом коммите
            cmd = ['git', 'show', '--name-status', '--pretty=format:', commit['hash']]
            result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"\nПредупреждение: Не удалось получить изменения файлов для коммита {commit['hash']}: {result.stderr}")
                continue
                
            # Парсим изменения файлов
            changes = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                parts = line.split('\t')
                if len(parts) < 2:
                    continue
                    
                change_type = parts[0]
                file_path = parts[1]
                
                # Пропускаем игнорируемые файлы
                if os.path.basename(file_path) in config.IGNORED_FILES:
                    continue
                
                # Получаем diff для этого файла в этом коммите
                file_diff = self._get_file_diff(commit['hash'], file_path)
                
                changes.append({
                    'change_type': change_type,
                    'file_path': file_path,
                    'file_ext': os.path.splitext(file_path)[1].lower(),
                    'diff': file_diff,
                    'is_substantial': self._is_substantial_change(file_diff, file_path)
                })
                
            file_changes[commit['hash']] = changes
        
        print("\nПолучение изменений файлов завершено.")
        return file_changes
    
    def _get_developer_info(self, commits):
        """Получение информации о разработчиках."""
        developer_info = {}
        
        # Для каждого уникального email разработчика
        for commit in commits:
            email = commit['author_email'].lower()
            
            if email not in developer_info:
                developer_info[email] = {
                    'name': commit['author_name'],
                    'email': email,
                    'first_commit_date': commit['date'],
                    'last_commit_date': commit['date'],
                    'first_commit_timestamp': commit['timestamp'],
                    'last_commit_timestamp': commit['timestamp'],
                }
            else:
                # Обновляем даты первого и последнего коммита
                if commit['timestamp'] < developer_info[email]['first_commit_timestamp']:
                    developer_info[email]['first_commit_date'] = commit['date']
                    developer_info[email]['first_commit_timestamp'] = commit['timestamp']
                    
                if commit['timestamp'] > developer_info[email]['last_commit_timestamp']:
                    developer_info[email]['last_commit_date'] = commit['date']
                    developer_info[email]['last_commit_timestamp'] = commit['timestamp']
        
        return developer_info
    
    def _get_file_diff(self, commit_hash, file_path):
        """Получение diff для конкретного файла в коммите."""
        cmd = ['git', 'show', '--format=', commit_hash, '--', file_path]
        result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True)
        
        if result.returncode != 0:
            return ""
            
        return result.stdout
    
    def _is_substantial_change(self, diff, file_path):
        """
        Определяет, является ли изменение существенным.
        Игнорирует изменения только в отступах, если так настроено.
        """
        if not diff:
            return False
        
        # Бинарные файлы считаем несущественными для анализа
        if self._is_binary_file(file_path):
            return False
            
        # Если настроено игнорирование изменений только в пробелах, проверяем
        if config.IGNORE_WHITESPACE_ONLY:
            # Удаляем все строки, которые изменяют только пробелы
            clean_diff = []
            for line in diff.split('\n'):
                if line.startswith('+') or line.startswith('-'):
                    # Удаляем пробелы и проверяем, осталось ли что-то
                    content_line = re.sub(r'\s', '', line[1:])
                    if content_line:
                        clean_diff.append(line)
                else:
                    clean_diff.append(line)
                    
            # Если не осталось существенных строк, это изменение только пробелов
            if not any(line.startswith('+') or line.startswith('-') for line in clean_diff):
                return False
                
        # Проверяем, соответствует ли размер изменения минимальному порогу
        added_lines = sum(1 for line in diff.split('\n') if line.startswith('+') and not line.startswith('+++'))
        removed_lines = sum(1 for line in diff.split('\n') if line.startswith('-') and not line.startswith('---'))
        
        return (added_lines + removed_lines) >= config.MIN_CODE_CHANGE_SIZE
    
    def _parse_commit_stats(self, commit_output):
        """Парсинг статистики коммита из вывода git show."""
        stats = {
            'files_changed': 0,
            'insertions': 0,
            'deletions': 0
        }
        
        # Ищем итоговую строку в конце вывода коммита
        summary_match = re.search(r'(\d+) files? changed(?:, (\d+) insertions?\(\+\))?(?:, (\d+) deletions?\(-\))?', commit_output)
        
        if summary_match:
            stats['files_changed'] = int(summary_match.group(1) or 0)
            stats['insertions'] = int(summary_match.group(2) or 0)
            stats['deletions'] = int(summary_match.group(3) or 0)
            
        return stats
        
    def _is_binary_file(self, file_path):
        """Проверка, является ли файл бинарным."""
        # Распространенные расширения бинарных файлов
        binary_extensions = {
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg',
            '.pdf', '.zip', '.tar', '.gz', '.rar',
            '.exe', '.dll', '.so', '.dylib',
            '.pyc', '.pyo', '.pyd',
            '.db', '.sqlite', '.sqlite3',
            '.jar', '.war', '.ear',
            '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        }
        
        ext = os.path.splitext(file_path)[1].lower()
        return ext in binary_extensions
