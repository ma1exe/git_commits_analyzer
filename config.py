# Настройки по умолчанию

# Настройки репозитория
REPO_PATH = None
START_DATE = None
END_DATE = None

# Настройки анализа
IGNORE_REVERTS = False
IGNORE_MERGES = False
MIN_CODE_CHANGE_SIZE = 5  # Минимальное количество изменений для существенного коммита
IGNORE_WHITESPACE_ONLY = True
CONSIDER_FILE_COMPLEXITY = True

# Настройки вывода
OUTPUT_FILE = 'developer_stats.json'
INCLUDE_DETAILED_STATS = True

# Список расширений файлов по категориям
CODE_FILE_EXTENSIONS = {
    '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp', 
    '.cs', '.go', '.rb', '.php', '.scala', '.swift', '.kt', '.rs', '.dart'
}

MARKUP_FILE_EXTENSIONS = {
    '.html', '.xml', '.md', '.rst', '.adoc', '.tex'
}

STYLE_FILE_EXTENSIONS = {
    '.css', '.scss', '.sass', '.less', '.styl'
}

CONFIG_FILE_EXTENSIONS = {
    '.json', '.yaml', '.yml', '.toml', '.ini', '.config', '.conf'
}

# Файлы, которые следует игнорировать при анализе
IGNORED_FILES = {
    'package-lock.json', 'yarn.lock', '.gitignore', '.gitattributes', 
    'Pipfile.lock', 'poetry.lock', 'requirements.txt'
}
