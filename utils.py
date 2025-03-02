import os
import re
import subprocess
from datetime import datetime, timedelta

def is_binary_file(file_path):
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

def normalize_author_name(name, email):
    """
    Нормализует имена авторов для обработки случаев, когда один и тот же человек 
    использует разные имена, но один и тот же email.
    """
    return email.lower()  # Используем email как уникальный идентификатор

def detect_squash_commit(commit_message, stats):
    """
    Определяет, является ли коммит squash-коммитом на основе темы и статистики.
    """
    # Проверяем ключевые слова в сообщении коммита
    message_lower = commit_message.lower()
    if ('squash' in message_lower or 
        'merge' in message_lower or 
        'объединены изменения' in message_lower or
        'combine' in message_lower):
        return True
        
    # Проверяем статистику коммита (большие коммиты с множеством изменений)
    if stats.get('files_changed', 0) > 10 and stats.get('insertions', 0) + stats.get('deletions', 0) > 100:
        return True
        
    return False

def categorize_changes(file_path):
    """
    Категоризирует файл на основе его расширения.
    Возвращает строку: 'code', 'test', 'doc', 'config', 'asset', 'other'
    """
    path_lower = file_path.lower()
    ext = os.path.splitext(file_path)[1].lower()
    
    # Исходный код
    if ext in {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.h', '.cs', '.go', '.rb', '.php'}:
        if 'test' in path_lower or 'spec' in path_lower:
            return 'test'
        return 'code'
        
    # Тесты
    if 'test' in path_lower or 'spec' in path_lower:
        return 'test'
        
    # Документация
    if ext in {'.md', '.rst', '.txt', '.pdf', '.doc', '.docx'} or 'readme' in path_lower or 'doc' in path_lower:
        return 'doc'
        
    # Конфигурация
    if ext in {'.json', '.yaml', '.yml', '.toml', '.ini', '.config', '.conf', '.xml'} or 'config' in path_lower:
        return 'config'
        
    # Ресурсы
    if ext in {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.css', '.scss', '.sass', '.less'}:
        return 'asset'
        
    # Другое
    return 'other'

def get_developer_active_periods(repo_path, author_email):
    """
    Определяет активные периоды разработчика в репозитории.
    Возвращает список периодов (начало, конец).
    
    Активный период - это непрерывный интервал времени, когда разработчик 
    регулярно делал коммиты (с промежутками не более 30 дней).
    """
    # Получаем все даты коммитов разработчика
    cmd = ['git', 'log', '--author=' + author_email, '--format=%at', '--date=unix']
    result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
    
    if result.returncode != 0 or not result.stdout.strip():
        return []
        
    # Преобразуем unix timestamps в объекты datetime
    commit_dates = [
        datetime.fromtimestamp(int(timestamp)) 
        for timestamp in result.stdout.strip().split('\n')
        if timestamp.strip()
    ]
    
    # Сортируем даты
    commit_dates.sort()
    
    # Определяем периоды активности
    active_periods = []
    current_period_start = commit_dates[0]
    current_period_end = commit_dates[0]
    
    for i in range(1, len(commit_dates)):
        current_date = commit_dates[i]
        gap = (current_date - current_period_end).days
        
        # Если разрыв больше 30 дней, считаем это новым периодом активности
        if gap > 30:
            active_periods.append((current_period_start, current_period_end))
            current_period_start = current_date
            
        current_period_end = current_date
        
    # Добавляем последний период
    active_periods.append((current_period_start, current_period_end))
    
    return active_periods

def analyze_commit_pattern(commit_messages):
    """
    Анализирует шаблоны коммитов для определения стиля работы разработчика.
    """
    patterns = {
        'descriptive': 0,  # Содержательные сообщения
        'minimal': 0,     # Минимальные/короткие сообщения
        'structured': 0,  # Структурированные (например, с префиксами fix:, feat:)
        'issue_references': 0, # Упоминания номеров задач/issues
    }
    
    for message in commit_messages:
        # Проверяем длину сообщения
        if len(message) < 10:
            patterns['minimal'] += 1
        elif len(message) > 50:
            patterns['descriptive'] += 1
            
        # Проверяем структурированность
        if re.match(r'^(fix|feat|docs|style|refactor|test|chore)(\(.*\))?:', message):
            patterns['structured'] += 1
            
        # Проверяем упоминания issues
        if re.search(r'#\d+|issue-\d+|task-\d+|jira-\d+', message, re.IGNORECASE):
            patterns['issue_references'] += 1
    
    # Нормализуем к процентам
    total = len(commit_messages) if commit_messages else 1
    for key in patterns:
        patterns[key] = round(patterns[key] * 100 / total, 2)
        
    return patterns
