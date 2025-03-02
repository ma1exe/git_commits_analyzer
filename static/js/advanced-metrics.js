/**
 * Модуль для отображения расширенных метрик разработчиков
 */

/**
 * Создает DOM-секцию с расширенными метриками для разработчика
 * @param {Object} developer - данные о разработчике
 * @returns {string} - HTML разметка секции с расширенными метриками
 */
function createAdvancedMetricsSection(developer) {
    if (!developer.advanced_metrics) {
        return '';
    }
    
    const metrics = developer.advanced_metrics;
    const devIdSafe = developer.email ? developer.email.replace('@', '-').replace(/\./g, '-') : 'dev';
    
    // Создаем контейнер для дополнительных метрик
    const section = `
    <div class="advanced-metrics-section">
        <h3>Расширенная аналитика</h3>
        
        <div class="metrics-grid">
            <!-- Распределение по типам файлов -->
            <div class="metric-card" id="file-types-${devIdSafe}">
                <h4>Типы файлов</h4>
                <canvas class="chart-canvas"></canvas>
            </div>
            
            <!-- Распределение по времени суток -->
            <div class="metric-card" id="time-dist-${devIdSafe}">
                <h4>Активность по времени суток</h4>
                <canvas class="chart-canvas"></canvas>
            </div>
            
            <!-- Размеры коммитов -->
            <div class="metric-card" id="commit-sizes-${devIdSafe}">
                <h4>Размеры коммитов</h4>
                <canvas class="chart-canvas"></canvas>
            </div>
            
            <!-- Дополнительные метрики -->
            <div class="metric-card">
                <h4>Ключевые показатели</h4>
                <div class="key-metrics">
                    ${metrics.avg_commit_interval_hours ? 
                      `<div class="key-metric">
                         <span class="metric-label">Среднее время между коммитами:</span>
                         <span class="metric-value">${metrics.avg_commit_interval_hours} ч.</span>
                       </div>` : ''}
                    
                    ${metrics.commit_variability ? 
                      `<div class="key-metric">
                         <span class="metric-label">Коэффициент равномерности вкладов:</span>
                         <span class="metric-value">${metrics.commit_variability}</span>
                         <div class="metric-info">
                            ${metrics.commit_variability < 0.5 ? 
                              'Очень равномерная активность' : 
                              metrics.commit_variability < 1.0 ? 
                              'Умеренно равномерная активность' : 
                              'Неравномерная активность'}
                         </div>
                       </div>` : ''}
                </div>
            </div>
        </div>
    </div>
    `;
    
    // Добавляем код инициализации графиков
    setTimeout(() => {
        initAdvancedMetricsCharts(developer);
    }, 100);
    
    return section;
}

/**
 * Инициализирует графики для расширенных метрик
 * @param {Object} developer - данные о разработчике
 */
function initAdvancedMetricsCharts(developer) {
    if (!developer.advanced_metrics) return;
    
    const metrics = developer.advanced_metrics;
    const devIdSafe = developer.email ? developer.email.replace('@', '-').replace(/\./g, '-') : 'dev';
    
    // Инициализация графика типов файлов
    initFileTypesChart(devIdSafe, metrics);
    
    // Инициализация графика активности по времени суток
    initTimeDistributionChart(devIdSafe, metrics);
    
    // Инициализация графика размеров коммитов
    initCommitSizesChart(devIdSafe, metrics);
}

/**
 * Инициализирует график распределения типов файлов
 * @param {string} devIdSafe - безопасный идентификатор разработчика
 * @param {Object} metrics - метрики разработчика
 */
function initFileTypesChart(devIdSafe, metrics) {
    if (!metrics.file_type_distribution) return;
    
    const fileTypesEl = document.getElementById(`file-types-${devIdSafe}`);
    if (!fileTypesEl) return;
    
    const canvas = fileTypesEl.querySelector('canvas');
    if (!canvas || !canvas.getContext) return;
    
    const ctx = canvas.getContext('2d');
    
    // Подготавливаем данные для графика (топ-7 типов файлов)
    const data = Object.entries(metrics.file_type_distribution)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 7);
    
    // Цветовая палитра для графика
    const colors = [
        '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', 
        '#e74a3b', '#858796', '#5a5c69'
    ];
    
    // Создаем график
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.map(([ext]) => ext),
            datasets: [{
                data: data.map(([_, count]) => count),
                backgroundColor: colors.slice(0, data.length)
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 12
                    }
                }
            }
        }
    });
}

/**
 * Инициализирует график распределения активности по времени суток
 * @param {string} devIdSafe - безопасный идентификатор разработчика
 * @param {Object} metrics - метрики разработчика
 */
function initTimeDistributionChart(devIdSafe, metrics) {
    if (!metrics.time_distribution) return;
    
    const timeDistEl = document.getElementById(`time-dist-${devIdSafe}`);
    if (!timeDistEl) return;
    
    const canvas = timeDistEl.querySelector('canvas');
    if (!canvas || !canvas.getContext) return;
    
    const ctx = canvas.getContext('2d');
    
    // Периоды дня
    const periods = {
        'morning': 'Утро (6-12)',
        'afternoon': 'День (12-18)',
        'evening': 'Вечер (18-23)',
        'night': 'Ночь (23-6)'
    };
    
    // Цветовая палитра для периодов дня
    const colors = [
        '#f8c291', '#1cc88a', '#4e73df', '#5a5c69'
    ];
    
    // Создаем график
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.values(periods),
            datasets: [{
                label: '% коммитов',
                data: Object.keys(periods).map(key => metrics.time_distribution[key] || 0),
                backgroundColor: colors
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Процент коммитов'
                    },
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Инициализирует график распределения размеров коммитов
 * @param {string} devIdSafe - безопасный идентификатор разработчика
 * @param {Object} metrics - метрики разработчика
 */
function initCommitSizesChart(devIdSafe, metrics) {
    if (!metrics.commit_size_distribution) return;
    
    const commitSizesEl = document.getElementById(`commit-sizes-${devIdSafe}`);
    if (!commitSizesEl) return;
    
    const canvas = commitSizesEl.querySelector('canvas');
    if (!canvas || !canvas.getContext) return;
    
    const ctx = canvas.getContext('2d');
    
    // Категории размеров коммитов
    const sizes = {
        'small': 'Маленькие (<10)',
        'medium': 'Средние (10-50)',
        'large': 'Большие (>50)'
    };
    
    // Цветовая палитра для размеров коммитов
    const colors = [
        '#1cc88a', '#4e73df', '#e74a3b'
    ];
    
    // Создаем график
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.values(sizes),
            datasets: [{
                data: Object.keys(sizes).map(key => metrics.commit_size_distribution[key] || 0),
                backgroundColor: colors
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 12
                    }
                }
            }
        }
    });
}