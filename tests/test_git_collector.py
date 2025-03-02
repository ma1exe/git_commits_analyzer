#!/usr/bin/env python3
import unittest
import os
import tempfile
import subprocess
from unittest.mock import patch, MagicMock
import sys
import shutil

# Добавляем родительскую директорию в путь для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from git_collector import GitDataCollector
import config

class TestGitDataCollector(unittest.TestCase):
    
    def setUp(self):
        # Создаем временную директорию для тестового репозитория
        self.temp_dir = tempfile.mkdtemp()
        self.git_repo_path = os.path.join(self.temp_dir, 'test_repo')
        os.makedirs(self.git_repo_path)
        
        # Инициализируем Git-репозиторий
        self._run_git_command(['git', 'init'])
        self._setup_git_config()
        
        # Создаем тестовый файл и делаем коммит
        test_file_path = os.path.join(self.git_repo_path, 'test_file.txt')
        with open(test_file_path, 'w') as f:
            f.write('Initial content')
        
        self._run_git_command(['git', 'add', 'test_file.txt'])
        self._run_git_command(['git', 'commit', '-m', 'Initial commit'])
        
        # Создаем объект коллектора
        self.collector = GitDataCollector(self.git_repo_path)
    
    def tearDown(self):
        # Удаляем временную директорию и все ее содержимое
        shutil.rmtree(self.temp_dir)
    
    def _run_git_command(self, command):
        subprocess.run(command, cwd=self.git_repo_path, check=True, capture_output=True)
    
    def _setup_git_config(self):
        # Настраиваем минимальную git-конфигурацию для коммитов
        self._run_git_command(['git', 'config', 'user.email', 'test@example.com'])
        self._run_git_command(['git', 'config', 'user.name', 'Test User'])
    
    def test_is_git_repo(self):
        # Проверяем, что метод правильно определяет Git-репозиторий
        self.assertTrue(self.collector._is_git_repo())
        
        # Проверяем что метод правильно определяет не Git-репозиторий
        non_git_dir = os.path.join(self.temp_dir, 'not_git')
        os.makedirs(non_git_dir)
        not_git_collector = GitDataCollector(non_git_dir)
        self.assertFalse(not_git_collector._is_git_repo())
    
    def test_get_commits(self):
        # Получаем коммиты
        commits = self.collector._get_commits()
        
        # Должен быть хотя бы один коммит (который мы сделали в setUp)
        self.assertGreaterEqual(len(commits), 1)
        
        # Проверяем структуру данных коммита
        commit = commits[0]
        self.assertIn('hash', commit)
        self.assertIn('author_name', commit)
        self.assertIn('author_email', commit)
        self.assertIn('timestamp', commit)
        self.assertIn('date', commit)
        self.assertIn('subject', commit)
        
        # Проверяем данные коммита
        self.assertEqual(commit['author_name'], 'Test User')
        self.assertEqual(commit['author_email'], 'test@example.com')
        self.assertEqual(commit['subject'], 'Initial commit')
    
    def test_ignores_reverts_when_configured(self):
        # Создаем revert-коммит
        test_file_path = os.path.join(self.git_repo_path, 'test_file.txt')
        with open(test_file_path, 'w') as f:
            f.write('Modified content')
        
        self._run_git_command(['git', 'add', 'test_file.txt'])
        self._run_git_command(['git', 'commit', '-m', 'Modify test file'])
        
        # Теперь делаем revert-коммит
        self._run_git_command(['git', 'revert', 'HEAD', '--no-edit'])
        
        # Включаем игнорирование revert-коммитов
        config.IGNORE_REVERTS = True
        
        # Получаем коммиты
        commits = self.collector._get_commits()
        
        # Должно быть 2 коммита (Initial + Modify), без revert
        revert_commits = [c for c in commits if c['is_revert']]
        self.assertEqual(len(revert_commits), 0)
        
        # Выключаем игнорирование revert-коммитов
        config.IGNORE_REVERTS = False
        
        # Получаем коммиты снова
        commits = self.collector._get_commits()
        
        # Теперь должно быть 3 коммита (Initial + Modify + Revert)
        revert_commits = [c for c in commits if c['is_revert']]
        self.assertEqual(len(revert_commits), 1)
    
    def test_is_substantial_change(self):
        # Создаем диффы для тестирования
        # 1. Существенное изменение
        substantial_diff = """diff --git a/test_file.txt b/test_file.txt
index 123456..789012 100644
--- a/test_file.txt
+++ b/test_file.txt
@@ -1,5 +1,15 +1,15 @
-Line 1
-Line 2
-Line 3
-Line 4
-Line 5
+Line 1 modified
+New line 2
+New line 3
+New line 4
+New line 5
+New line 6
+New line 7
+New line 8
+New line 9
+New line 10
"""
        
        # 2. Изменение только отступов
        whitespace_diff = """diff --git a/test_file.txt b/test_file.txt
index 123456..789012 100644
--- a/test_file.txt
+++ b/test_file.txt
@@ -1,5 +1,5 @
-Line 1
-    Line 2
-Line 3
-Line 4
-Line 5
+Line 1
+  Line 2
+Line 3
+Line 4
+Line 5
"""
        
        # Настраиваем порог для существенных изменений
        config.MIN_CODE_CHANGE_SIZE = 5
        config.IGNORE_WHITESPACE_ONLY = True
        
        # Проверяем существенное изменение
        self.assertTrue(self.collector._is_substantial_change(substantial_diff, 'test_file.txt'))
        
        # Проверяем изменение только отступов
        self.assertFalse(self.collector._is_substantial_change(whitespace_diff, 'test_file.txt'))
        
        # Проверяем с выключенным игнорированием отступов
        config.IGNORE_WHITESPACE_ONLY = False
        self.assertTrue(self.collector._is_substantial_change(whitespace_diff, 'test_file.txt'))

if __name__ == '__main__':
    unittest.main()
