#!/usr/bin/env python3
import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Добавляем родительскую директорию в путь для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analyzer import DevActivityAnalyzer
import config

class TestDevActivityAnalyzer(unittest.TestCase):
    
    def setUp(self):
        # Подготавливаем тестовые данные
        self.test_git_data = {
            'commits': [
                {
                    'hash': 'abcd1234',
                    'author_name': 'Developer 1',
                    'author_email': 'dev1@example.com',
                    'timestamp': 1609459200,  # 2021-01-01
                    'date': '2021-01-01 00:00:00',
                    'subject': 'Add feature X',
                    'is_revert': False
                },
                {
                    'hash': 'efgh5678',
                    'author_name': 'Developer 1',
                    'author_email': 'dev1@example.com',
                    'timestamp': 1609545600,  # 2021-01-02
                    'date': '2021-01-02 00:00:00',
                    'subject': 'Fix bug in feature X',
                    'is_revert': False
                },
                {
                    'hash': 'ijkl9012',
                    'author_name': 'Developer 2',
                    'author_email': 'dev2@example.com',
                    'timestamp': 1609632000,  # 2021-01-03
                    'date': '2021-01-03 00:00:00',
                    'subject': 'Refactor module Y',
                    'is_revert': False
                },
                {
                    'hash': 'mnop3456',
                    'author_name': 'Developer 2',
                    'author_email': 'dev2@example.com',
                    'timestamp': 1609718400,  # 2021-01-04
                    'date': '2021-01-04 00:00:00',
                    'subject': 'Revert "Refactor module Y"',
                    'is_revert': True
                }
            ],
            'commit_details': {
                'abcd1234': {
                    'stats': {
                        'files_changed': 3,
                        'insertions': 150,
                        'deletions': 50
                    }
                },
                'efgh5678': {
                    'stats': {
                        'files_changed': 1,
                        'insertions': 10,
                        'deletions': 5
                    }
                },
                'ijkl9012': {
                    'stats': {
                        'files_changed': 5,
                        'insertions': 200,
                        'deletions': 150
                    }
                },
                'mnop3456': {
                    'stats': {
                        'files_changed': 5,
                        'insertions': 150,
                        'deletions': 200
                    }
                }
            },
            'file_changes': {
                'abcd1234': [
                    {
                        'change_type': 'M',
                        'file_path': 'src/feature_x.py',
                        'file_ext': '.py',
                        'diff': 'sample diff',
                        'is_substantial': True
                    },
                    {
                        'change_type': 'A',
                        'file_path': 'tests/test_feature_x.py',
                        'file_ext': '.py',
                        'diff': 'sample diff',
                        'is_substantial': True
                    },
                    {
                        'change_type': 'M',
                        'file_path': 'docs/feature_x.md',
                        'file_ext': '.md',
                        'diff': 'sample diff',
                        'is_substantial': False
                    }
                ],
                'efgh5678': [
                    {
                        'change_type': 'M',
                        'file_path': 'src/feature_x.py',
                        'file_ext': '.py',
                        'diff': 'sample diff',
                        'is_substantial': True
                    }
                ],
                'ijkl9012': [
                    {
                        'change_type': 'M',
                        'file_path': 'src/module_y.py',
                        'file_ext': '.py',
                        'diff': 'sample diff',
                        'is_substantial': True
                    },
                    {
                        'change_type': 'M',
                        'file_path': 'src/module_y_utils.py',
                        'file_ext': '.py',
                        'diff': 'sample diff',
                        'is_substantial': True
                    },
                    {
                        'change_type': 'M',
                        'file_path': 'tests/test_module_y.py',
                        'file_ext': '.py',
                        'diff': 'sample diff',
                        'is_substantial': True
                    },
                    {
                        'change_type': 'M',
                        'file_path': 'docs/module_y.md',
                        'file_ext': '.md',
                        'diff': 'sample diff',
                        'is_substantial': False
                    },
                    {
                        'change_type': 'M',
                        'file_path': 'config/module_y_config.json',
                        'file_ext': '.json',
                        'diff': 'sample diff',
                        'is_substantial': False
                    }
                ],
                'mnop3456': [
                    {
                        'change_type': 'M',
                        'file_path': 'src/module_y.py',
                        'file_ext': '.py',
                        'diff': 'sample diff',
                        'is_substantial': True
                    },
                    {
                        'change_type': 'M',
                        'file_path': 'src/module_y_utils.py',
                        'file_ext': '.py',
                        'diff': 'sample diff',
                        'is_substantial': True
                    },
                    {
                        'change_type': 'M',
                        'file_path': 'tests/test_module_y.py',
                        'file_ext': '.py',
                        'diff': 'sample diff',
                        'is_substantial': True
                    },
                    {
                        'change_type': 'M',
                        'file_path': 'docs/module_y.md',
                        'file_ext': '.md',
                        'diff': 'sample diff',
                        'is_substantial': False
                    },
                    {
                        'change_type': 'M',
                        'file_path': 'config/module_y_config.json',
                        'file_ext': '.json',
                        'diff': 'sample diff',
                        'is_substantial': False
                    }
                ]
            },
            'developer_info': {
                'dev1@example.com': {
                    'name': 'Developer 1',
                    'email': 'dev1@example.com',
                    'first_commit_date': '2021-01-01 00:00:00',
                    'last_commit_date': '2021-01-02 00:00:00',
                    'first_commit_timestamp': 1609459200,
                    'last_commit_timestamp': 1609545600
                },
                'dev2@example.com': {
                    'name': 'Developer 2',
                    'email': 'dev2@example.com',
                    'first_commit_date': '2021-01-03 00:00:00',
                    'last_commit_date': '2021-01-04 00:00:00',
                    'first_commit_timestamp': 1609632000,
                    'last_commit_timestamp': 1609718400
                }
            }
        }
        
        # Создаем объект анализатора
        self.analyzer = DevActivityAnalyzer(self.test_git_data)
    
    def test_analyze_commit(self):
        # Создаем словарь статистики разработчиков для тестирования
        dev_stats = {}
        
        # Анализируем первый коммит Developer 1
        self.analyzer._analyze_commit(self.test_git_data['commits'][0], dev_stats)
        
        # Проверяем, что статистика Developer 1 правильно обновлена
        self.assertIn('dev1@example.com', dev_stats)
        self.assertEqual(dev_stats['dev1@example.com']['name'], 'Developer 1')
        self.assertEqual(dev_stats['dev1@example.com']['total_commits'], 1)
        self.assertEqual(dev_stats['dev1@example.com']['substantial_commits'], 1)
        self.assertEqual(dev_stats['dev1@example.com']['lines_added'], 150)
        self.assertEqual(dev_stats['dev1@example.com']['lines_removed'], 50)
        self.assertEqual(len(dev_stats['dev1@example.com']['files_modified']), 3)
        
        # Анализируем revert-коммит Developer 2
        self.analyzer._analyze_commit(self.test_git_data['commits'][3], dev_stats)
        
        # Проверяем, что статистика Developer 2 правильно обновлена
        self.assertIn('dev2@example.com', dev_stats)
        self.assertEqual(dev_stats['dev2@example.com']['name'], 'Developer 2')
        self.assertEqual(dev_stats['dev2@example.com']['total_commits'], 1)
        self.assertEqual(dev_stats['dev2@example.com']['reverts_count'], 1)
        self.assertEqual(dev_stats['dev2@example.com']['lines_added'], 150)
        self.assertEqual(dev_stats['dev2@example.com']['lines_removed'], 200)
    
    def test_analyze(self):
        # Запускаем полный анализ
        results = self.analyzer.analyze()
        
        # Проверяем, что результаты содержат статистику для обоих разработчиков
        self.assertIn('dev1@example.com', results)
        self.assertIn('dev2@example.com', results)
        
        # Проверяем суммарные метрики Developer 1
        dev1 = results['dev1@example.com']
        self.assertEqual(dev1['total_commits'], 2)
        self.assertEqual(dev1['substantial_commits'], 2)
        self.assertEqual(dev1['lines_added'], 160)
        self.assertEqual(dev1['lines_removed'], 55)
        
        # Проверяем активный период Developer 1
        self.assertEqual(dev1['active_days'], 1)  # 1 день между первым и последним коммитом
        
        # Проверяем суммарные метрики Developer 2
        dev2 = results['dev2@example.com']
        self.assertEqual(dev2['total_commits'], 2)
        self.assertEqual(dev2['substantial_commits'], 2)
        self.assertEqual(dev2['lines_added'], 350)
        self.assertEqual(dev2['lines_removed'], 350)
        self.assertEqual(dev2['reverts_count'], 1)
        
        # Проверяем распределение коммитов по времени
        self.assertIn('2021-01', dev1['commit_distribution'])
        self.assertEqual(dev1['commit_distribution']['2021-01'], 2)
        
    def test_calculate_file_complexity(self):
        # Проверяем сложность различных типов файлов
        py_complexity = self.analyzer._calculate_file_complexity('src/module.py')
        html_complexity = self.analyzer._calculate_file_complexity('templates/index.html')
        txt_complexity = self.analyzer._calculate_file_complexity('docs/readme.txt')
        
        # Python файлы должны иметь более высокую сложность
        self.assertGreater(py_complexity, html_complexity)
        self.assertGreater(py_complexity, txt_complexity)

if __name__ == '__main__':
    unittest.main()
