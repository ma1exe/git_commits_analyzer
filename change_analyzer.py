#!/usr/bin/env python3
import re
import os
import config

class ChangeAnalyzer:
    """
    Класс для анализа изменений в коммитах с продвинутой оценкой существенности.
    """
    
    def __init__(self):
        # Словарь весов для различных типов файлов
        self.file_weights = {
            # Исходный код
            '.py': 1.0,     # Python
            '.java': 1.0,   # Java
            '.js': 1.0,     # JavaScript
            '.ts': 1.0,     # TypeScript
            '.cpp': 1.0,    # C++
            '.c': 1.0,      # C
            '.cs': 1.0,     # C#
            '.go': 1.0,     # Go
            '.rs': 1.0,     # Rust
            
            # Тесты (имеют меньший вес)
            'test_': 0.7,   # Файлы тестов (по названию)
            '_test': 0.7,
            '.test': 0.7,
            'spec_': 0.7,
            '_spec': 0.7,
            
            # Конфигурационные файлы
            '.json': 0.6,   # JSON конфигурация
            '.yml': 0.6,    # YAML конфигурация 
            '.yaml': 0.6,   # YAML конфигурация
            '.toml': 0.6,   # TOML конфигурация
            '.ini': 0.6,    # INI конфигурация
            '.config': 0.6, # Прочая конфигурация
            
            # Документация
            '.md': 0.5,     # Markdown
            '.rst': 0.5,    # reStructuredText
            '.txt': 0.5,    # Текстовые файлы
            '.docs': 0.5,   # Документация
            
            # Стили и шаблоны
            '.css': 0.8,    # CSS
            '.scss': 0.8,   # SCSS
            '.sass': 0.8,   # SASS
            '.less': 0.8,   # LESS
            '.html': 0.8,   # HTML
            '.xml': 0.7,    # XML
            
            # Ресурсы (меньший вес)
            '.svg': 0.4,    # SVG-изображения
            '.png': 0.3,    # PNG-изображения
            '.jpg': 0.3,    # JPG-изображения
            '.jpeg': 0.3,   # JPEG-изображения
            '.gif': 0.3,    # GIF-изображения
            
            # Прочее
            '.csv': 0.5,    # CSV-данные
            '.sql': 0.9,    # SQL-запросы
        }
        
        # Веса для типов коммитов на основе ключевых слов
        self.commit_type_weights = {
            'fix': 1.2,       # Исправления оцениваются выше
            'bug': 1.2,       # Исправления багов
            'hotfix': 1.3,    # Срочные исправления
            'feat': 1.1,      # Новые функции
            'feature': 1.1,   # Новые функции
            'refactor': 1.0,  # Рефакторинг
            'perf': 1.2,      # Оптимизация производительности
            'test': 0.8,      # Тестирование
            'docs': 0.7,      # Документация
            'style': 0.6,     # Стилевые изменения
            'chore': 0.5,     # Рутинные задачи
        }
        
        # Индикаторы сложности изменений
        self.complexity_indicators = [
            r'if\s+\(.+\)',       # Условные операторы
            r'for\s+\(.+\)',      # Циклы for
            r'while\s+\(.+\)',    # Циклы while
            r'switch\s+\(.+\)',   # Конструкции switch
            r'case\s+.+:',        # Case в switch
            r'try\s*{',           # Блоки обработки исключений
            r'catch\s*\(.+\)',    # Обработка исключений
            r'function\s+\w+',    # Объявления функций
            r'def\s+\w+',         # Объявления функций (Python)
            r'class\s+\w+',       # Объявления классов
            r'import\s+.+',       # Импорты (признак зависимостей)
            r'@\w+',              # Декораторы/аннотации (признак сложности)
            r'\s*return\s+.+',    # Возвраты значений
            r'async\s+',          # Асинхронный код
            r'await\s+',          # Асинхронный код
            r'\w+\.\w+\(.+\)',    # Вызовы методов
        ]
        
        # Порог для определения существенности
        self.min_change_threshold = config.MIN_CODE_CHANGE_SIZE
    
    def _is_binary_file(self, file_path):
        """
        Определяет, является ли файл бинарным на основе расширения.
        """
        binary_extensions = ['.bin', '.exe', '.dll', '.so', '.pyc', '.jar', '.war', 
                            '.class', '.o', '.obj', '.png', '.jpg', '.jpeg', '.gif', 
                            '.bmp', '.ico', '.pdf', '.doc', '.docx', '.ppt', '.pptx', 
                            '.xls', '.xlsx', '.zip', '.tar', '.gz', '.rar', '.7z']
        
        file_ext = os.path.splitext(file_path)[1].lower()
        return file_ext in binary_extensions
    
    def _get_file_weight(self, file_path):
        """
        Определяет вес файла на основе его типа и расположения.
        """
        if not file_path:
            return 1.0
            
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_path)[1].lower()
        
        weight = 1.0  # Вес по умолчанию
        
        # Проверяем расширение
        if file_ext in self.file_weights:
            weight = self.file_weights[file_ext]
        
        # Проверяем на тестовые файлы по имени
        for test_pattern in ['test_', '_test', '.test', 'spec_', '_spec']:
            if test_pattern in file_name.lower():
                weight = min(weight, self.file_weights.get(test_pattern, 0.7))
                break
        
        # Проверяем на расположение в тестовой директории
        path_parts = file_path.lower().split(os.path.sep)
        for part in path_parts:
            if part in ['test', 'tests', 'testing', 'spec', 'specs']:
                weight = min(weight, 0.7)
                break
        
        return weight
    
    def _analyze_complexity(self, diff):
        """
        Анализирует сложность изменений на основе содержимого.
        """
        if not diff:
            return 0
            
        complexity_score = 0
        added_lines = [line[1:] for line in diff.split('\n') 
                      if line.startswith('+') and not line.startswith('+++')]
        
        # Считаем уникальные индикаторы сложности
        unique_indicators = set()
        for line in added_lines:
            for pattern in self.complexity_indicators:
                if re.search(pattern, line):
                    unique_indicators.add(pattern)
        
        # Базовая оценка - количество строк
        complexity_score = len(added_lines) * 0.1
        
        # Добавляем бонус за наличие индикаторов сложности
        complexity_score += len(unique_indicators) * 0.5
        
        # Нормализуем к диапазону 0.5 - 2.0
        complexity_score = max(0.5, min(2.0, 0.5 + complexity_score / 10))
        
        return complexity_score
    
    def _get_commit_type_weight(self, commit_message):
        """
        Определяет вес коммита на основе сообщения.
        """
        if not commit_message:
            return 1.0
            
        commit_message = commit_message.lower()
        
        # Конвенциональные коммиты (fix:, feat:, etc.)
        match = re.match(r'^(\w+)(\([\w-]+\))?:', commit_message)
        if match:
            commit_type = match.group(1)
            if commit_type in self.commit_type_weights:
                return self.commit_type_weights[commit_type]
        
        # Если нет явного указания типа, ищем ключевые слова
        weight = 1.0
        for keyword, keyword_weight in self.commit_type_weights.items():
            if keyword in commit_message:
                # Используем наибольший вес из найденных ключевых слов
                weight = max(weight, keyword_weight)
        
        return weight
    
    def is_substantial_change(self, diff, file_path, commit_message=None):
        """
        Определяет, является ли изменение существенным с учетом
        типа файла, сложности изменений и контекста коммита.
        
        Args:
            diff: строка с diff-ом изменений
            file_path: путь к файлу
            commit_message: сообщение коммита (опционально)
            
        Returns:
            bool: True, если изменение существенное, иначе False
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
        added_lines = sum(1 for line in diff.split('\n') 
                          if line.startswith('+') and not line.startswith('+++'))
        removed_lines = sum(1 for line in diff.split('\n') 
                            if line.startswith('-') and not line.startswith('---'))
        
        total_changes = added_lines + removed_lines
        
        # Применяем веса и коэффициенты
        file_weight = self._get_file_weight(file_path)
        complexity_weight = self._analyze_complexity(diff)
        commit_weight = self._get_commit_type_weight(commit_message) if commit_message else 1.0
        
        # Вычисляем взвешенный размер изменения
        weighted_changes = total_changes * file_weight * complexity_weight * commit_weight
        
        # Логируем информацию о расчетах (по желанию)
        if hasattr(config, 'DEBUG_MODE') and config.DEBUG_MODE:
            print(f"File: {file_path}")
            print(f"  Changes: {total_changes}")
            print(f"  File Weight: {file_weight}")
            print(f"  Complexity: {complexity_weight}")
            print(f"  Commit Weight: {commit_weight}")
            print(f"  Weighted Changes: {weighted_changes}")
            print(f"  Substantial: {weighted_changes >= self.min_change_threshold}")
        
        # Сравниваем с порогом существенности
        return weighted_changes >= self.min_change_threshold