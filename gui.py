#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import subprocess
import datetime
import json
import calendar
import os
import sys

class DatePicker:
    """Простой виджет выбора даты"""
    def __init__(self, parent, callback, initial_date=None):
        self.parent = parent
        self.callback = callback
        self.window = tk.Toplevel(parent)
        self.window.title("Выберите дату")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Установка текущей даты или начальной даты
        if initial_date:
            try:
                self.current_date = datetime.datetime.strptime(initial_date, "%Y-%m-%d").date()
            except ValueError:
                self.current_date = datetime.date.today()
        else:
            self.current_date = datetime.date.today()
        
        self.year = self.current_date.year
        self.month = self.current_date.month
        
        # Создаем виджеты
        self.setup_ui()
        
        # Центрируем окно
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
    def setup_ui(self):
        """Настраивает пользовательский интерфейс"""
        # Верхняя панель с навигацией
        nav_frame = ttk.Frame(self.window)
        nav_frame.pack(fill=tk.X, padx=5, pady=5)
        
        prev_year = ttk.Button(nav_frame, text="<<", width=3, command=self.prev_year)
        prev_year.pack(side=tk.LEFT)
        
        prev_month = ttk.Button(nav_frame, text="<", width=3, command=self.prev_month)
        prev_month.pack(side=tk.LEFT, padx=5)
        
        self.month_year_label = ttk.Label(nav_frame, text=self.get_month_year_str())
        self.month_year_label.pack(side=tk.LEFT, padx=5)
        
        next_month = ttk.Button(nav_frame, text=">", width=3, command=self.next_month)
        next_month.pack(side=tk.LEFT, padx=5)
        
        next_year = ttk.Button(nav_frame, text=">>", width=3, command=self.next_year)
        next_year.pack(side=tk.LEFT)
        
        # Календарь
        calendar_frame = ttk.Frame(self.window)
        calendar_frame.pack(padx=5, pady=5)
        
        # Дни недели
        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for i, day in enumerate(days):
            ttk.Label(calendar_frame, text=day, width=4).grid(row=0, column=i)
        
        # Заполняем календарь днями
        self.day_buttons = []
        for i in range(6):  # 6 строк
            for j in range(7):  # 7 дней в неделе
                btn = ttk.Button(calendar_frame, text="", width=4, command=lambda x=i, y=j: self.select_day(x, y))
                btn.grid(row=i+1, column=j)
                self.day_buttons.append(btn)
        
        self.update_calendar()
        
        # Кнопки внизу
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        today_button = ttk.Button(button_frame, text="Сегодня", command=self.set_today)
        today_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = ttk.Button(button_frame, text="Очистить", command=self.clear_date)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Отмена", command=self.window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
    def get_month_year_str(self):
        """Возвращает строку месяц и год"""
        months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", 
                  "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
        return f"{months[self.month-1]} {self.year}"
        
    def update_calendar(self):
        """Обновляет отображение календаря"""
        # Обновляем заголовок
        self.month_year_label.config(text=self.get_month_year_str())
        
        # Очищаем кнопки
        for btn in self.day_buttons:
            btn.config(text="")
            btn.state(['!disabled', '!pressed'])  # Сбрасываем все состояния
        
        # Получаем первый день месяца и количество дней
        first_day = datetime.date(self.year, self.month, 1)
        # Корректируем индекс дня недели (0 - понедельник, 6 - воскресенье)
        first_weekday = first_day.weekday()
        month_range = calendar.monthrange(self.year, self.month)[1]
        
        # Заполняем календарь
        for i in range(month_range):
            day = i + 1
            index = first_weekday + i
            
            # Проверяем, не выходит ли индекс за границы массива
            if index < len(self.day_buttons):
                self.day_buttons[index].config(text=str(day))
                
                # Подсвечиваем текущую дату
                if day == self.current_date.day and self.month == self.current_date.month and self.year == self.current_date.year:
                    try:
                        self.day_buttons[index].state(['pressed'])
                    except Exception:
                        # Обрабатываем возможную ошибку при установке состояния
                        pass
            # Если индекс выходит за границы, просто пропускаем этот день
    
    def prev_year(self):
        """Переход к предыдущему году"""
        self.year -= 1
        self.update_calendar()
    
    def next_year(self):
        """Переход к следующему году"""
        self.year += 1
        self.update_calendar()
    
    def prev_month(self):
        """Переход к предыдущему месяцу"""
        self.month -= 1
        if self.month < 1:
            self.month = 12
            self.year -= 1
        self.update_calendar()
    
    def next_month(self):
        """Переход к следующему месяцу"""
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1
        self.update_calendar()
    
    def select_day(self, row, col):
        """Выбор дня календаря"""
        index = row * 7 + col
        if index < len(self.day_buttons) and self.day_buttons[index]['text']:
            day = int(self.day_buttons[index]['text'])
            selected_date = datetime.date(self.year, self.month, day)
            self.callback(selected_date.strftime("%Y-%m-%d"))
            self.window.destroy()
    
    def set_today(self):
        """Устанавливает текущую дату"""
        today = datetime.date.today()
        self.callback(today.strftime("%Y-%m-%d"))
        self.window.destroy()
    
    def clear_date(self):
        """Очищает выбранную дату"""
        self.callback("")
        self.window.destroy()

class RedirectText:
    """Класс для перенаправления stdout в текстовый виджет"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""
        self._updating = False

    def write(self, string):
        self.buffer += string
        # Обновляем виджет только при полной строке для уменьшения мерцания
        if '\n' in self.buffer and not self._updating:
            self.update_widget()
        
    def update_widget(self):
        """Обновляет текстовый виджет безопасным образом"""
        self._updating = True
        try:
            if not self.buffer:
                return
                
            # Используем after_idle для безопасного обновления UI из другого потока
            self.text_widget.after_idle(self._safe_update_widget)
        except Exception:
            # В случае ошибки сбрасываем флаг обновления
            self._updating = False
    
    def _safe_update_widget(self):
        """Безопасно обновляет виджет из основного потока"""
        try:
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, self.buffer)
            self.text_widget.see(tk.END)
            self.text_widget.configure(state='disabled')
            self.buffer = ""
        except Exception as e:
            print(f"Ошибка при обновлении текстового виджета: {str(e)}", file=sys.__stdout__)
        finally:
            self._updating = False

    def flush(self):
        """Сбрасывает буфер"""
        if self.buffer and not self._updating:
            self.update_widget()

class GitDevProductivityGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Git Developer Productivity Analyzer")
        self.root.geometry("1000x800")  # Увеличен размер окна
        
        # Устанавливаем минимальный размер окна
        self.root.minsize(900, 800)  # Увеличен минимальный размер окна
        
        # Создаем основной фрейм с отступами
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем notebook (вкладки)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Инициализируем состояние приложения
        self.initialize_state()  # Сначала создаем self.weight_vars

        # Создаем вкладки
        self.setup_analysis_tab()
        self.setup_weights_tab()  # Теперь self.weight_vars уже существует
        self.setup_exclude_tab()
        self.setup_log_tab()
        
        # Создаем строку статуса
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к анализу")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(fill=tk.X)
        
        # Создаем кнопки внизу
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.run_button = ttk.Button(button_frame, text="Запустить анализ", command=self.run_analysis)
        self.run_button.pack(side=tk.RIGHT, padx=5)
        
    def initialize_state(self):
        # Устанавливаем начальные значения для весов
        self.weight_vars = {
            'substantial_commits': tk.DoubleVar(value=0.3),
            'lines': tk.DoubleVar(value=0.15),
            'impact': tk.DoubleVar(value=0.25),
            'substantive_ratio': tk.DoubleVar(value=0.2),
            'revert_penalty': tk.DoubleVar(value=-0.1),
            'daily_activity': tk.DoubleVar(value=0.2),
            'merge_penalty': tk.DoubleVar(value=-0.05)
        }
        
        # Список исключаемых разработчиков
        self.excluded_developers = []

    def show_date_picker(self, date_var):
        """Показывает виджет выбора даты"""
        def set_date(date_str):
            date_var.set(date_str)
            
        DatePicker(self.root, set_date, date_var.get())
        
    def setup_analysis_tab(self):
        analysis_tab = ttk.Frame(self.notebook)
        self.notebook.add(analysis_tab, text="Параметры анализа")
        
        # Создаем фрейм с параметрами
        params_frame = ttk.LabelFrame(analysis_tab, text="Основные параметры", padding=10)
        params_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Путь к репозиторию
        repo_frame = ttk.Frame(params_frame)
        repo_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(repo_frame, text="Путь к Git-репозиторию:").pack(side=tk.LEFT, padx=(0, 10))
        self.repo_path_var = tk.StringVar()
        repo_entry = ttk.Entry(repo_frame, textvariable=self.repo_path_var, width=50)
        repo_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_button = ttk.Button(repo_frame, text="Обзор...", command=self.browse_repo)
        browse_button.pack(side=tk.LEFT, padx=5)
        
        # Путь к выходному файлу
        output_frame = ttk.Frame(params_frame)
        output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_frame, text="Путь к выходному JSON:").pack(side=tk.LEFT, padx=(0, 10))
        self.output_file_var = tk.StringVar(value="developer_stats.json")
        output_entry = ttk.Entry(output_frame, textvariable=self.output_file_var, width=50)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        output_browse = ttk.Button(output_frame, text="Обзор...", command=self.browse_output)
        output_browse.pack(side=tk.LEFT, padx=5)
        
        # Дополнительные параметры анализа
        options_frame = ttk.LabelFrame(analysis_tab, text="Дополнительные параметры", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Период анализа
        dates_frame = ttk.Frame(options_frame)
        dates_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(dates_frame, text="Период анализа:").pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(dates_frame, text="С:").pack(side=tk.LEFT, padx=(0, 5))
        self.start_date_var = tk.StringVar()
        self.start_date_entry = ttk.Entry(dates_frame, textvariable=self.start_date_var, width=10)
        self.start_date_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        start_date_picker = ttk.Button(dates_frame, text="📅", width=3, 
                                     command=lambda: self.show_date_picker(self.start_date_var))
        start_date_picker.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(dates_frame, text="По:").pack(side=tk.LEFT, padx=(0, 5))
        self.end_date_var = tk.StringVar()
        self.end_date_entry = ttk.Entry(dates_frame, textvariable=self.end_date_var, width=10)
        self.end_date_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        end_date_picker = ttk.Button(dates_frame, text="📅", width=3, 
                                   command=lambda: self.show_date_picker(self.end_date_var))
        end_date_picker.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(dates_frame, text="(формат: YYYY-MM-DD)").pack(side=tk.LEFT, padx=5)        

        # Минимальные изменения
        min_changes_frame = ttk.Frame(options_frame)
        min_changes_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(min_changes_frame, text="Мин. кол-во изменений для существенного коммита:").pack(side=tk.LEFT, padx=(0, 10))
        self.min_changes_var = tk.IntVar(value=5)
        min_changes_spinbox = ttk.Spinbox(min_changes_frame, from_=1, to=100, textvariable=self.min_changes_var, width=5)
        min_changes_spinbox.pack(side=tk.LEFT)
        
        # Чекбоксы для опций
        checkboxes_frame = ttk.Frame(options_frame)
        checkboxes_frame.pack(fill=tk.X, pady=5)
        
        self.ignore_reverts_var = tk.BooleanVar(value=True)
        ignore_reverts_check = ttk.Checkbutton(checkboxes_frame, text="Игнорировать revert-коммиты", variable=self.ignore_reverts_var)
        ignore_reverts_check.pack(side=tk.LEFT, padx=(0, 20))
        
        self.ignore_merges_var = tk.BooleanVar(value=True)  # По умолчанию включено
        ignore_merges_check = ttk.Checkbutton(checkboxes_frame, text="Игнорировать merge-коммиты", variable=self.ignore_merges_var)
        ignore_merges_check.pack(side=tk.LEFT)
        
        # Настройки вывода HTML
        html_frame = ttk.LabelFrame(analysis_tab, text="Настройки HTML-отчета", padding=10)
        html_frame.pack(fill=tk.X, padx=10, pady=10)
        
        html_options_frame = ttk.Frame(html_frame)
        html_options_frame.pack(fill=tk.X, pady=5)
        
        self.generate_html_var = tk.BooleanVar(value=True)
        generate_html_check = ttk.Checkbutton(html_options_frame, text="Генерировать HTML-отчет", 
                                            variable=self.generate_html_var,
                                            command=self.toggle_html_options)
        generate_html_check.pack(side=tk.LEFT, padx=(0, 20))
        
        self.inline_html_var = tk.BooleanVar(value=True)
        self.inline_html_check = ttk.Checkbutton(html_options_frame, text="Встроить CSS и JS (рекомендуется)", 
                                               variable=self.inline_html_var)
        self.inline_html_check.pack(side=tk.LEFT)
        
        # Директория для HTML
        html_dir_frame = ttk.Frame(html_frame)
        html_dir_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(html_dir_frame, text="Директория для HTML-отчета:").pack(side=tk.LEFT, padx=(0, 10))
        self.html_dir_var = tk.StringVar(value="git_stats_report")
        self.html_dir_entry = ttk.Entry(html_dir_frame, textvariable=self.html_dir_var, width=50)
        self.html_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.html_dir_browse = ttk.Button(html_dir_frame, text="Обзор...", command=self.browse_html_dir)
        self.html_dir_browse.pack(side=tk.LEFT, padx=5)
        
    def setup_weights_tab(self):
        weights_tab = ttk.Frame(self.notebook)
        self.notebook.add(weights_tab, text="Веса параметров")
        
        # Верхняя часть с описанием
        info_frame = ttk.Frame(weights_tab, padding=10)
        info_frame.pack(fill=tk.X)
        
        info_text = "Настройте веса параметров, используемых для расчета рейтинга полезности разработчиков."
        ttk.Label(info_frame, text=info_text, wraplength=600).pack(anchor=tk.W)
        
        # Создаем фрейм с ползунками весов
        weights_frame = ttk.LabelFrame(weights_tab, text="Настройка весов", padding=10)
        weights_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Описания весов
        descriptions = {
            'substantial_commits': 'Коммиты с существенными изменениями. Отражает способность делать осмысленные изменения.',
            'lines': 'Общее количество строк, добавленных и удаленных. Отражает объем выполненной работы.',
            'impact': 'Влияние коммитов на кодовую базу. Учитывает количество файлов и объем изменений.',
            'substantive_ratio': 'Доля существенных коммитов к общему числу. Отражает качество вносимых изменений.',
            'revert_penalty': 'Штраф за отмену коммитов (revert). Отражает стабильность и надежность изменений.',
            'daily_activity': 'Регулярность и стабильность активности. Равномерность вклада во времени.'
        }
        
        # Человеко-читаемые названия
        weight_names = {
            'substantial_commits': 'Существенные коммиты',
            'lines': 'Количество строк',
            'impact': 'Влияние коммитов',
            'substantive_ratio': 'Доля значимых коммитов',
            'revert_penalty': 'Штраф за реверты',
            'daily_activity': 'Регулярность активности'
        }
        
        # Словарь для хранения меток со значениями весов
        self.weight_labels = {}
        
        # Создаем слайдеры для каждого веса
        for i, (weight_id, name) in enumerate(weight_names.items()):
            frame = ttk.Frame(weights_frame, padding=(0, 5))
            frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Название параметра
            ttk.Label(frame, text=name, width=20).pack(side=tk.LEFT, padx=(0, 10))
            
            # Если это штраф за реверты, используем другие границы
            if weight_id == 'revert_penalty':
                slider = ttk.Scale(frame, from_=-1.0, to=0.0, variable=self.weight_vars[weight_id], 
                                  command=lambda val, id=weight_id: self.update_weight_label(id))
            else:
                slider = ttk.Scale(frame, from_=0.0, to=1.0, variable=self.weight_vars[weight_id], 
                                  command=lambda val, id=weight_id: self.update_weight_label(id))
            slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            # Метка с текущим значением
            value_label = ttk.Label(frame, text=f"{self.weight_vars[weight_id].get():.2f}", width=5)
            value_label.pack(side=tk.LEFT, padx=5)
            self.weight_labels[weight_id] = value_label
            
            # Кнопка сброса
            reset_button = ttk.Button(frame, text="Сброс", 
                                     command=lambda id=weight_id, default=self.weight_vars[weight_id].get(): 
                                     self.reset_weight(id, default))
            reset_button.pack(side=tk.LEFT, padx=5)
            
            # Добавляем описание
            desc_frame = ttk.Frame(weights_frame)
            desc_frame.pack(fill=tk.X, padx=5)
            ttk.Label(desc_frame, text=descriptions[weight_id], 
                     wraplength=600, font=('TkDefaultFont', 9, 'italic')).pack(side=tk.LEFT, padx=(30, 0))
            
            # Добавляем разделитель между параметрами
            if i < len(weight_names) - 1:
                ttk.Separator(weights_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5, pady=5)
                
        # Кнопки управления весами
        buttons_frame = ttk.Frame(weights_tab, padding=10)
        buttons_frame.pack(fill=tk.X, pady=5)
        
        reset_all_button = ttk.Button(buttons_frame, text="Сбросить все веса", command=self.reset_all_weights)
        reset_all_button.pack(side=tk.RIGHT, padx=5)
        
        save_weights_button = ttk.Button(buttons_frame, text="Сохранить веса", command=self.save_weights)
        save_weights_button.pack(side=tk.RIGHT, padx=5)
        
        load_weights_button = ttk.Button(buttons_frame, text="Загрузить веса", command=self.load_weights)
        load_weights_button.pack(side=tk.RIGHT, padx=5)
        
    def setup_exclude_tab(self):
        exclude_tab = ttk.Frame(self.notebook)
        self.notebook.add(exclude_tab, text="Исключение разработчиков")
        
        # Верхняя часть с описанием
        info_frame = ttk.Frame(exclude_tab, padding=10)
        info_frame.pack(fill=tk.X)
        
        info_text = "Укажите, каких разработчиков нужно исключить из отчета и графиков."
        ttk.Label(info_frame, text=info_text, wraplength=600).pack(anchor=tk.W)
        
        # Предупреждение о необходимости анализа репозитория
        self.repo_warning = ttk.Label(info_frame, 
                                     text="Для автоматической загрузки списка разработчиков сначала выполните анализ репозитория.",
                                     foreground="orange", wraplength=600)
        self.repo_warning.pack(anchor=tk.W, pady=10)
        
        # Фрейм для ввода email разработчика
        input_frame = ttk.Frame(exclude_tab, padding=10)
        input_frame.pack(fill=tk.X)
        
        ttk.Label(input_frame, text="Email разработчика:").pack(side=tk.LEFT, padx=(0, 10))
        self.dev_email_var = tk.StringVar()
        dev_email_entry = ttk.Entry(input_frame, textvariable=self.dev_email_var, width=40)
        dev_email_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        self.add_dev_button = ttk.Button(input_frame, text="Добавить", command=self.add_excluded_developer, state="normal")
        self.add_dev_button.pack(side=tk.LEFT)
        
        self.analyze_first_button = ttk.Button(input_frame, text="Анализировать репозиторий", 
                                            command=self.analyze_repo_for_devs)
        self.analyze_first_button.pack(side=tk.LEFT, padx=10)
        
        # Фрейм для списка разработчиков
        list_frame = ttk.LabelFrame(exclude_tab, text="Список разработчиков", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Список всех разработчиков
        self.excluded_list = tk.Listbox(list_frame, height=10, selectmode=tk.MULTIPLE)
        self.excluded_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Полоса прокрутки для списка
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.excluded_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.excluded_list.config(yscrollcommand=scrollbar.set)
        
        # Кнопки управления списком
        buttons_frame = ttk.Frame(exclude_tab, padding=10)
        buttons_frame.pack(fill=tk.X)
        
        exclude_selected_button = ttk.Button(buttons_frame, text="Исключить выбранные", 
                                          command=self.add_selected_to_exclusion)
        exclude_selected_button.pack(side=tk.LEFT, padx=(0, 10))
        
        exclude_all_button = ttk.Button(buttons_frame, text="Исключить всех", 
                                      command=self.exclude_all_developers)
        exclude_all_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Фрейм для списка исключенных разработчиков
        excluded_frame = ttk.LabelFrame(exclude_tab, text="Исключенные разработчики", padding=10)
        excluded_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Список исключенных разработчиков
        self.excluded_devs_list = tk.Listbox(excluded_frame, height=10)
        self.excluded_devs_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Полоса прокрутки для списка исключенных
        excluded_scrollbar = ttk.Scrollbar(excluded_frame, orient=tk.VERTICAL, command=self.excluded_devs_list.yview)
        excluded_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.excluded_devs_list.config(yscrollcommand=excluded_scrollbar.set)
        
        # Кнопки управления списком исключенных
        excluded_buttons_frame = ttk.Frame(exclude_tab, padding=10)
        excluded_buttons_frame.pack(fill=tk.X)
        
        remove_button = ttk.Button(excluded_buttons_frame, text="Удалить выбранное", command=self.remove_excluded_developer)
        remove_button.pack(side=tk.LEFT)
        
        clear_button = ttk.Button(excluded_buttons_frame, text="Очистить список", command=self.clear_excluded_developers)
        clear_button.pack(side=tk.LEFT, padx=10)
        
    def add_selected_to_exclusion(self):
        """Добавляет выбранных разработчиков в список исключений"""
        try:
            # Получаем все выбранные индексы
            selected_indices = self.excluded_list.curselection()
            if not selected_indices:
                messagebox.showwarning("Предупреждение", "Выберите разработчиков для исключения")
                return
                
            # Обрабатываем каждый выбранный элемент
            for index in selected_indices:
                selected_item = self.excluded_list.get(index)
                
                # Извлекаем email из строки вида "Name <email>"
                import re
                email_match = re.search(r'<([^>]+)>', selected_item)
                if email_match:
                    email = email_match.group(1)
                else:
                    email = selected_item
                    
                # Проверяем, не добавлен ли уже этот email
                if email in self.excluded_developers:
                    continue
                
                # Добавляем в список исключенных
                self.excluded_developers.append(email)
                self.excluded_devs_list.insert(tk.END, selected_item)
                
            print(f"Добавлено {len(selected_indices)} разработчиков в список исключений")
            messagebox.showinfo("Успех", f"Добавлено {len(selected_indices)} разработчиков в список исключений")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при добавлении разработчиков: {str(e)}")
            
    def exclude_all_developers(self):
        """Исключает всех разработчиков из списка"""
        try:
            # Получаем все элементы из списка
            all_items = [self.excluded_list.get(i) for i in range(self.excluded_list.size())]
            if not all_items:
                messagebox.showwarning("Предупреждение", "Список разработчиков пуст")
                return
                
            # Очищаем текущий список исключенных
            self.clear_excluded_developers()
            
            # Добавляем всех разработчиков в список исключений
            for item in all_items:
                # Извлекаем email из строки вида "Name <email>"
                import re
                email_match = re.search(r'<([^>]+)>', item)
                if email_match:
                    email = email_match.group(1)
                else:
                    email = item
                    
                # Добавляем в список исключенных
                self.excluded_developers.append(email)
                self.excluded_devs_list.insert(tk.END, item)
                
            print(f"Добавлены все {len(all_items)} разработчиков в список исключений")
            messagebox.showinfo("Успех", f"Добавлены все {len(all_items)} разработчиков в список исключений")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при добавлении всех разработчиков: {str(e)}")
            
    def remove_excluded_developer(self):
        """Удаляет выбранного разработчика из списка исключений"""
        try:
            selected_index = self.excluded_devs_list.curselection()[0]
            selected_item = self.excluded_devs_list.get(selected_index)
            
            # Извлекаем email из строки вида "Name <email>"
            import re
            email_match = re.search(r'<([^>]+)>', selected_item)
            if email_match:
                email = email_match.group(1)
            else:
                email = selected_item
                
            # Удаляем из списка в GUI
            self.excluded_devs_list.delete(selected_index)
            
            # Удаляем из списка хранимых email-ов, если он там есть
            if email in self.excluded_developers:
                self.excluded_developers.remove(email)
                print(f"Разработчик {email} удален из списка исключений")
            else:
                print(f"Предупреждение: email {email} не найден в списке исключений")
                
        except IndexError:
            messagebox.showwarning("Предупреждение", "Выберите разработчика для удаления")
        
    def setup_log_tab(self):
        log_tab = ttk.Frame(self.notebook)
        self.notebook.add(log_tab, text="Журнал")
        
        # Создаем текстовое поле для логов
        log_frame = ttk.Frame(log_tab, padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Текстовое поле с прокруткой
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Кнопки для управления логами
        buttons_frame = ttk.Frame(log_tab, padding=10)
        buttons_frame.pack(fill=tk.X)
        
        clear_log_button = ttk.Button(buttons_frame, text="Очистить журнал", command=self.clear_log)
        clear_log_button.pack(side=tk.RIGHT)
        
        save_log_button = ttk.Button(buttons_frame, text="Сохранить журнал", command=self.save_log)
        save_log_button.pack(side=tk.RIGHT, padx=10)
        
    def update_weight_label(self, weight_id):
        """Обновляет метку со значением веса при изменении слайдера"""
        self.weight_labels[weight_id].config(text=f"{self.weight_vars[weight_id].get():.2f}")
        
    def reset_weight(self, weight_id, default_value):
        """Сбрасывает вес параметра к значению по умолчанию"""
        self.weight_vars[weight_id].set(default_value)
        self.update_weight_label(weight_id)
        
    def reset_all_weights(self):
        """Сбрасывает все веса к значениям по умолчанию"""
        default_values = {
            'substantial_commits': 0.3,
            'lines': 0.15,
            'impact': 0.25,
            'substantive_ratio': 0.2,
            'revert_penalty': -0.1,
            'daily_activity': 0.2,
            'merge_penalty': -0.05
        }
        
        for weight_id, default in default_values.items():
            self.weight_vars[weight_id].set(default)
            self.update_weight_label(weight_id)
            
    def save_weights(self):
        """Сохраняет текущие веса в файл"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Сохранить настройки весов"
        )
        
        if not filename:
            return
            
        weights = {weight_id: var.get() for weight_id, var in self.weight_vars.items()}
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(weights, f, indent=2)
            messagebox.showinfo("Успех", "Настройки весов успешно сохранены")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {str(e)}")
            
    def load_weights(self):
        """Загружает веса из файла"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Загрузить настройки весов"
        )
        
        if not filename:
            return
            
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                weights = json.load(f)
                
            for weight_id, value in weights.items():
                if weight_id in self.weight_vars:
                    self.weight_vars[weight_id].set(value)
                    self.update_weight_label(weight_id)
                    
            messagebox.showinfo("Успех", "Настройки весов успешно загружены")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить настройки: {str(e)}")
            
    def add_excluded_developer(self):
        """Добавляет разработчика в список исключений"""
        email = self.dev_email_var.get().strip()
        if not email:
            messagebox.showwarning("Предупреждение", "Введите email разработчика")
            return
        
        # Проверяем, возможно email уже в формате "имя <email>"
        import re
        email_match = re.search(r'<([^>]+)>', email)
        if email_match:
            display_text = email  # Уже в нужном формате
            email = email_match.group(1)  # Извлекаем только email
        else:
            display_text = email  # Нет имени, просто отображаем email

        # Проверяем, не добавлен ли уже этот email
        if email in self.excluded_developers:
            messagebox.showwarning("Предупреждение", f"Разработчик {email} уже в списке исключений")
            return
        
        # Добавляем email в список исключений
        self.excluded_developers.append(email)
        
        # Добавляем отображаемый текст в список
        self.excluded_list.insert(tk.END, display_text)
        
        # Очищаем поле ввода
        self.dev_email_var.set("")
        
        print(f"Разработчик {email} добавлен в список исключений")
  
    def clear_excluded_developers(self):
        """Очищает весь список исключенных разработчиков"""
        self.excluded_devs_list.delete(0, tk.END)
        self.excluded_developers.clear()
        print("Список исключенных разработчиков очищен")
        
    def clear_log(self):
        """Очищает текстовое поле журнала"""
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state='disabled')
        
    def save_log(self):
        """Сохраняет содержимое журнала в файл"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Сохранить журнал"
        )
        
        if not filename:
            return
            
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.log_text.get(1.0, tk.END))
            messagebox.showinfo("Успех", "Журнал успешно сохранен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить журнал: {str(e)}")
            
    def browse_repo(self):
        """Открывает диалог выбора директории репозитория"""
        directory = filedialog.askdirectory(title="Выберите Git-репозиторий")
        if directory:
            self.repo_path_var.set(directory)
            
    def browse_output(self):
        """Открывает диалог выбора выходного JSON-файла"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Выберите место для сохранения отчета"
        )
        if filename:
            self.output_file_var.set(filename)
            
    def browse_html_dir(self):
        """Открывает диалог выбора директории для HTML-отчета"""
        directory = filedialog.askdirectory(title="Выберите директорию для HTML-отчета")
        if directory:
            self.html_dir_var.set(directory)
            
    def toggle_html_options(self):
        """Включает/выключает опции HTML в зависимости от состояния чекбокса"""
        state = "normal" if self.generate_html_var.get() else "disabled"
        self.inline_html_check.configure(state=state)
        self.html_dir_entry.configure(state=state)
        self.html_dir_browse.configure(state=state)        

    def analyze_repo_for_devs(self):
        """Анализирует репозиторий для получения списка разработчиков"""
        # Проверяем, указан ли путь к репозиторию
        repo_path = self.repo_path_var.get()
        if not repo_path or not os.path.exists(repo_path):
            messagebox.showerror("Ошибка", "Укажите корректный путь к Git-репозиторию")
            return
            
        # Проверяем, является ли указанный путь Git-репозиторием
        if not os.path.exists(os.path.join(repo_path, '.git')):
            messagebox.showerror("Ошибка", "Указанная директория не является Git-репозиторием")
            return
            
        self.status_var.set("Анализирую репозиторий для получения списка разработчиков...")
        self.analyze_first_button.configure(state="disabled")
        
        # Запускаем анализ в отдельном потоке
        thread = threading.Thread(target=self._analyze_repo_for_devs_thread)
        thread.daemon = True
        thread.start()
        
    def _analyze_repo_for_devs_thread(self):
        """Выполняет анализ репозитория для получения списка разработчиков в отдельном потоке"""
        try:
            # Импортируем необходимый модуль
            from git_collector import GitDataCollector
            
            # Создаем коллектор и собираем данные
            repo_path = self.repo_path_var.get()
            collector = GitDataCollector(repo_path)
            git_data = collector.collect_data()
            
            # Получаем список разработчиков
            developers = git_data['developer_info']
            
            # Обновляем интерфейс в основном потоке
            self._safe_update_ui(self._update_developer_list(developers))
            
        except Exception as e:
            # Обновляем интерфейс в основном потоке
            self._safe_update_ui(self.status_var.set("Ошибка при анализе репозитория"))
            self._safe_update_ui(self.analyze_first_button.configure(state="normal"))
            self._safe_update_ui(messagebox.showerror("Ошибка", f"Ошибка при анализе репозитория: {str(e)}"))
            
    def _update_developer_list(self, developers):
        """Обновляет список разработчиков"""
        # Очищаем предыдущий список
        self.clear_excluded_developers()
        
        # Сортируем разработчиков по имени
        sorted_devs = sorted(developers.values(), key=lambda x: x['name'])
        
        # Добавляем разработчиков в выпадающий список или аналогичный контрол
        dev_count = 0
        for dev in sorted_devs:
            email = dev['email']
            name = dev['name']
            
            # Форматируем строку для отображения
            display_text = f"{name} <{email}>"
            
            # Добавляем в список GUI
            self.excluded_list.insert(tk.END, display_text)
            
            # НЕ добавляем в список исключенных по умолчанию!
            # Пользователь должен выбрать, кого исключить
            
            dev_count += 1
            
        # Обновляем статус и кнопки
        self.status_var.set(f"Найдено {dev_count} разработчиков")
        self.analyze_first_button.configure(state="normal")
        self.repo_warning.configure(text=f"Найдено {dev_count} разработчиков. Выберите тех, кого нужно исключить из отчета.", foreground="green")
        
        # Показываем сообщение
        messagebox.showinfo("Успех", f"Найдено {dev_count} разработчиков в репозитории")
        
    def run_analysis(self):
        """Запускает анализ репозитория в отдельном потоке"""
        # Проверяем, указан ли путь к репозиторию
        repo_path = self.repo_path_var.get()
        if not repo_path or not os.path.exists(repo_path):
            messagebox.showerror("Ошибка", "Укажите корректный путь к Git-репозиторию")
            return
            
        # Проверяем, является ли указанный путь Git-репозиторием
        if not os.path.exists(os.path.join(repo_path, '.git')):
            messagebox.showerror("Ошибка", "Указанная директория не является Git-репозиторием")
            return
            
        # Отключаем кнопку запуска на время анализа
        self.run_button.configure(state="disabled")
        self.status_var.set("Анализ запущен...")
        
        # Очищаем журнал перед новым анализом
        self.clear_log()
        
        # Создаем объект для перенаправления вывода в текстовое поле журнала
        redirect = RedirectText(self.log_text)
        sys.stdout = redirect
        
        # Добавляем метку времени в начало лога
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, f"=== Начало анализа: {timestamp} ===\n\n")
        self.log_text.configure(state='disabled')
        
        # Переключаемся на вкладку журнала
        self.notebook.select(3)  # Индекс вкладки журнала
        
        # Запускаем анализ в отдельном потоке
        thread = threading.Thread(target=self._run_analysis_thread)
        thread.daemon = True  # Поток завершится при закрытии приложения
        thread.start()
        
    def _run_analysis_thread(self):
        """Выполняет анализ в отдельном потоке"""
        try:
            # Импортируем необходимые модули
            import importlib
            import time
            
            # Строго импортируем каждый модуль по отдельности, чтобы избежать конфликтов
            import config
            importlib.reload(config)  # Перезагрузка модуля для применения новых настроек
            
            from git_collector import GitDataCollector
            importlib.reload(sys.modules['git_collector'])  # Перезагрузка модуля

            from analyzer import DevActivityAnalyzer
            importlib.reload(sys.modules['analyzer'])  # Перезагрузка модуля
            
            from output_generator import JSONOutputGenerator
            importlib.reload(sys.modules['output_generator'])  # Перезагрузка модуля
            
            from html_generator import HTMLGenerator
            importlib.reload(sys.modules['html_generator'])  # Перезагрузка модуля
            
            # Получаем значения из GUI
            repo_path = self.repo_path_var.get()
            output_file = self.output_file_var.get()
            
            # Выводим информацию о начале анализа
            print(f"Анализ репозитория: {repo_path}")
            print(f"Выходной файл: {output_file}")
            print(f"Параметры:")
            print(f"  - Игнорировать revert-коммиты: {self.ignore_reverts_var.get()}")
            print(f"  - Игнорировать merge-коммиты: {self.ignore_merges_var.get()}")
            if self.start_date_var.get():
                print(f"  - Начальная дата: {self.start_date_var.get()}")
            if self.end_date_var.get():
                print(f"  - Конечная дата: {self.end_date_var.get()}")
            print(f"  - Мин. изменений для существенного коммита: {self.min_changes_var.get()}")
            
            # Настраиваем конфигурацию
            config.IGNORE_REVERTS = self.ignore_reverts_var.get()
            config.IGNORE_MERGES = self.ignore_merges_var.get()
            config.REPO_PATH = repo_path
            config.OUTPUT_FILE = output_file
            config.START_DATE = self.start_date_var.get() if self.start_date_var.get() else None
            config.END_DATE = self.end_date_var.get() if self.end_date_var.get() else None
            config.MIN_CODE_CHANGE_SIZE = self.min_changes_var.get()
            
            # Создаем директорию для выходного файла, если она не существует
            output_dir = os.path.dirname(os.path.abspath(output_file))
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                print(f"Создана директория для выходного файла: {output_dir}")
            
            print("\n=== Сбор данных из Git ===")
            
            # Собираем данные из Git
            collector = GitDataCollector(repo_path)
            git_data = collector.collect_data()
            
            print(f"Собрано {len(git_data['commits'])} коммитов")
            
            print("\n=== Анализ данных ===")
            
            # Анализируем данные
            analyzer = DevActivityAnalyzer(git_data)
            analysis_results = analyzer.analyze()
            
            print(f"Проанализировано {len(analysis_results)} разработчиков")
            
            print("\n=== Расчет рейтинга полезности ===")
            
            # Собираем пользовательские веса
            custom_weights = {
                weight_id: var.get() for weight_id, var in self.weight_vars.items()
            }
            
            print("Используемые веса для расчета:")
            for param, value in custom_weights.items():
                print(f"  - {param}: {value}")
            
            # Генерируем выходные данные
            output_generator = JSONOutputGenerator(analysis_results)
            output_data = output_generator.generate_output(
                output_file, 
                custom_weights=custom_weights,
                excluded_developers=self.excluded_developers if self.excluded_developers else None
            )
            
            print(f"Анализ завершен. Результаты сохранены в {output_file}")
            
            print("\n=== Состояние после анализа ===")
            print(f"Всего коммитов: {len(git_data['commits'])}")
            print(f"Активных разработчиков: {len(analysis_results)}")
            
            # Статистика по типам коммитов
            revert_commits = sum(1 for commit in git_data['commits'] if commit['is_revert'])
            merge_commits = sum(1 for commit in git_data['commits'] if commit.get('is_merge', False))
            print(f"Revert-коммитов: {revert_commits}")
            print(f"Merge-коммитов: {merge_commits}")
            
            # Суммарная статистика
            total_lines_added = sum(dev['lines_added'] for dev in analysis_results.values())
            total_lines_removed = sum(dev['lines_removed'] for dev in analysis_results.values())
            print(f"Всего строк добавлено: {total_lines_added}")
            print(f"Всего строк удалено: {total_lines_removed}")
            
            # Выводим топ-3 разработчика по полезности
            if output_data and 'usefulness_rating' in output_data:
                print("\nТоп-3 разработчика по полезности:")
                top_devs = sorted(
                    output_data['usefulness_rating'].items(), 
                    key=lambda x: x[1]['score'], 
                    reverse=True
                )[:3]
                
                for i, (dev_id, rating) in enumerate(top_devs, 1):
                    dev_name = analysis_results[dev_id]['name']
                    score = rating['score']
                    print(f"{i}. {dev_name} ({dev_id}) - {score:.2f} баллов")
            
            # Генерируем HTML-отчет, если это запрошено
            if self.generate_html_var.get():
                print("\n=== Генерация HTML-отчета ===")
                
                # Определяем имя HTML-файла на основе имени JSON-файла
                base_name = os.path.basename(output_file)
                name_without_ext = os.path.splitext(base_name)[0]
                html_filename = name_without_ext + ".html"
                
                # Используем директорию JSON-файла, если не указано иное
                html_output_dir = self.html_dir_var.get()
                if html_output_dir == 'git_stats_report':  # Если используется значение по умолчанию
                    html_output_dir = os.path.dirname(os.path.abspath(output_file))
                
                print(f"Директория для HTML: {html_output_dir}")
                print(f"Имя HTML-файла: {html_filename}")
                
                html_gen = HTMLGenerator(
                    output_file, 
                    html_output_dir,
                    html_filename=html_filename
                )
                html_gen.generate()
                
                html_path = os.path.join(html_output_dir, html_filename)
                print(f"HTML-отчет сгенерирован: {html_path}")
                
            # Добавляем метку времени в конец лога
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n=== Анализ завершен: {timestamp} ===")
            
            # Обновляем интерфейс в основном потоке
            self._safe_update_ui(self.status_var.set("Анализ завершен успешно"))
            self._safe_update_ui(self.run_button.configure(state="normal"))
            
            # Показываем диалог успешного завершения
            self._safe_update_ui(messagebox.showinfo("Успех", "Анализ успешно завершен!"))
            
            # Также сохраняем результаты анализа для возможного использования в разделе исключения разработчиков
            self._safe_update_ui(self._update_developer_list_if_needed(analysis_results))
            
        except Exception as e:
            print(f"Ошибка при анализе: {str(e)}")
            import traceback
            print(traceback.format_exc())
            
            # Обновляем интерфейс в основном потоке
            self._safe_update_ui(self.status_var.set("Ошибка при анализе"))
            self._safe_update_ui(self.run_button.configure(state="normal"))
            
            # Показываем диалог ошибки
            self._safe_update_ui(messagebox.showerror("Ошибка", f"Ошибка при анализе: {str(e)}"))
        
        finally:
            # Восстанавливаем стандартный вывод
            sys.stdout = sys.__stdout__
            
    def _update_developer_list_if_needed(self, analysis_results):
        """Обновляет список разработчиков после анализа, если список пуст"""
        if not self.excluded_developers:
            # Создаем словарь в формате developer_info для _update_developer_list
            dev_info = {}
            for dev_id, stats in analysis_results.items():
                dev_info[dev_id] = {
                    'name': stats['name'],
                    'email': dev_id,
                    'first_commit_date': stats['first_commit_date'],
                    'last_commit_date': stats['last_commit_date']
                }
            
            # Обновляем список разработчиков
            self._update_developer_list(dev_info)

    def _safe_update_ui(self, func, *args, **kwargs):
        """Безопасно обновляет UI из другого потока"""
        if not self.root.winfo_exists():
            return  # Окно было закрыто, ничего не делаем
        
        try:
            self.root.after_idle(lambda: func(*args, **kwargs))
        except Exception as e:
            print(f"Ошибка при обновлении UI: {str(e)}", file=sys.__stdout__)

if __name__ == "__main__":
    root = tk.Tk()
    app = GitDevProductivityGUI(root)
    root.mainloop()

    self.lock = threading.Lock()