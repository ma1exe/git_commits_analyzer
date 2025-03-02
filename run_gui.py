#!/usr/bin/env python3
"""
Скрипт запуска графического интерфейса для Git Developer Productivity Analyzer.
"""

import tkinter as tk
import sys
import os
import platform

# Проверяем наличие необходимых модулей
try:
    import tkinter.ttk
    import tkinter.filedialog
    import tkinter.messagebox
    import tkinter.scrolledtext
except ImportError:
    print("Ошибка: Не установлен модуль tkinter.")
    print("Для установки:")
    if platform.system() == "Windows":
        print("  - Переустановите Python, отметив пункт 'tcl/tk and IDLE' во время установки")
    elif platform.system() == "Linux":
        print("  - Ubuntu/Debian: sudo apt-get install python3-tk")
        print("  - Fedora: sudo dnf install python3-tkinter")
        print("  - CentOS/RHEL: sudo yum install python3-tkinter")
    elif platform.system() == "Darwin":  # macOS
        print("  - Используйте Python.org установщик, включающий tkinter")
        print("  - Или через Homebrew: brew install python-tk")
    sys.exit(1)

# Добавляем текущую директорию в путь для импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Проверяем наличие требуемых файлов
required_files = ['gui.py', 'git_collector.py', 'analyzer.py', 'output_generator.py', 'html_generator.py']
missing_files = []
for file in required_files:
    if not os.path.exists(os.path.join(current_dir, file)):
        missing_files.append(file)

if missing_files:
    print(f"Ошибка: Не найдены следующие файлы: {', '.join(missing_files)}")
    print("Убедитесь, что вы запускаете скрипт из корректной директории.")
    sys.exit(1)

# Импортируем GUI
try:
    from gui import GitDevProductivityGUI
except ImportError as e:
    print(f"Ошибка при импорте модуля gui.py: {str(e)}")
    sys.exit(1)

def main():
    """Запускает графический интерфейс"""
    print("Запуск графического интерфейса Git Developer Productivity Analyzer...")
    
    try:
        root = tk.Tk()
        app = GitDevProductivityGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Ошибка при запуске GUI: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())