/**
 * Модуль для создания и обновления графиков
 */

/**
 * Функция для перерисовки всех графиков
 * @param {Object} data - данные Git-статистики
 */
function redrawCharts(data) {
    // Очищаем существующие графики
    document.getElementById('commit-chart').innerHTML = '';
    document.getElementById('impact-chart').innerHTML = '';
    document.getElementById('timeline-chart').innerHTML = '';
    
    // Создаем графики заново
    createCommitChart(data);
    createImpactChart(data);
    createContributionTimeline(data);
}

/**
 * Создает график с распределением коммитов по разработчикам
 * @param {Object} data - данные Git-статистики
 */
function createCommitChart(data) {
    const chartDiv = document.getElementById('commit-chart');
    if (!chartDiv || typeof Chart === 'undefined') return;
    
    // Извлекаем данные для графика, исключая скрытых разработчиков
    const developers = Object.keys(data.developers).filter(dev => !window.hiddenDevelopers.has(dev));
    
    // Если нет видимых разработчиков, показываем сообщение
    if (developers.length === 0) {
        chartDiv.innerHTML = '<p>Нет видимых разработчиков для отображения графика</p>';
        return;
    }
    
    const developerNames = developers.map(dev => data.developers[dev].name);
    const commitCounts = developers.map(dev => data.developers[dev].total_commits);
    const substantialCommitCounts = developers.map(dev => data.developers[dev].substantial_commits);
    const squashCommitCounts = developers.map(dev => data.developers[dev].squash_count || 0);
    const mergeCommitCounts = developers.map(dev => data.developers[dev].merge_count || 0);
    
    // Создаем обертку для канваса с фиксированной высотой
    const chartWrapper = document.createElement('div');
    chartWrapper.style.height = '400px';
    chartWrapper.style.width = '100%';
    chartDiv.appendChild(chartWrapper);
    
    // Создаем график с помощью Chart.js
    const ctx = document.createElement('canvas');
    chartWrapper.appendChild(ctx);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: developerNames,
            datasets: [
                {
                    label: 'Все коммиты',
                    data: commitCounts,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Существенные коммиты',
                    data: substantialCommitCounts,
                    backgroundColor: 'rgba(255, 99, 132, 0.5)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Squash-коммиты',
                    data: squashCommitCounts,
                    backgroundColor: 'rgba(255, 205, 86, 0.5)',
                    borderColor: 'rgba(255, 205, 86, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Merge-коммиты',
                    data: mergeCommitCounts,
                    backgroundColor: 'rgba(153, 102, 255, 0.5)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Количество коммитов по разработчикам'
                },
                legend: {
                    position: 'top',
                    labels: {
                        boxWidth: 15,
                        font: {
                            size: 11
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Количество коммитов'
                    }
                },
                x: {
                    ticks: {
                        autoSkip: true,
                        maxRotation: 45,
                        minRotation: 45,
                        font: {
                            size: 10
                        }
                    }
                }
            }
        }
    });
}

/**
 * Создает график влияния разработчиков на кодовую базу
 * @param {Object} data - данные Git-статистики
 */
function createImpactChart(data) {
    const chartDiv = document.getElementById('impact-chart');
    if (!chartDiv || typeof Chart === 'undefined') return;
    
    // Извлекаем данные для графика, исключая скрытых разработчиков
    const developers = Object.keys(data.developers).filter(dev => !window.hiddenDevelopers.has(dev));
    
    // Если нет видимых разработчиков, показываем сообщение
    if (developers.length === 0) {
        chartDiv.innerHTML = '<p>Нет видимых разработчиков для отображения графика</p>';
        return;
    }
    
    const developerNames = developers.map(dev => data.developers[dev].name);
    const impactValues = developers.map(dev => data.developers[dev].commit_impact);
    const linesAdded = developers.map(dev => data.developers[dev].lines_added);
    const linesRemoved = developers.map(dev => data.developers[dev].lines_removed);
    
    // Создаем обертку для канваса с фиксированной высотой
    const chartWrapper = document.createElement('div');
    chartWrapper.style.height = '400px';
    chartWrapper.style.width = '100%';
    chartDiv.appendChild(chartWrapper);
    
    // Создаем график с помощью Chart.js
    const ctx = document.createElement('canvas');
    chartWrapper.appendChild(ctx);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: developerNames,
            datasets: [
                {
                    label: 'Влияние коммитов',
                    data: impactValues,
                    backgroundColor: 'rgba(75, 192, 192, 0.5)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    type: 'bar'
                },
                {
                    label: 'Добавлено строк',
                    data: linesAdded,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                    type: 'bar',
                    hidden: true
                },
                {
                    label: 'Удалено строк',
                    data: linesRemoved,
                    backgroundColor: 'rgba(255, 99, 132, 0.5)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1,
                    type: 'bar',
                    hidden: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Влияние разработчиков'
                },
                legend: {
                    position: 'top',
                    labels: {
                        boxWidth: 15,
                        font: {
                            size: 11
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += Math.round(context.parsed.y);
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Значение'
                    }
                },
                x: {
                    ticks: {
                        autoSkip: true,
                        maxRotation: 45,
                        minRotation: 45,
                        font: {
                            size: 10
                        }
                    }
                }
            }
        }
    });
}

/**
 * Создает график распределения активности разработчиков по времени
 * @param {Object} data - данные Git-статистики
 */
function createContributionTimeline(data) {
    const chartDiv = document.getElementById('timeline-chart');
    if (!chartDiv || typeof Chart === 'undefined') return;
    
    // Извлекаем данные для графика временной шкалы
    const commitDistributions = {};
    const developerNames = {};
    
    for (const [devId, stats] of Object.entries(data.developers)) {
        // Пропускаем скрытых разработчиков
        if (window.hiddenDevelopers.has(devId)) continue;
        
        developerNames[devId] = stats.name;
        
        // Добавляем распределение коммитов этого разработчика
        if (stats.commit_distribution) {
            for (const [month, count] of Object.entries(stats.commit_distribution)) {
                if (!commitDistributions[month]) {
                    commitDistributions[month] = {};
                }
                commitDistributions[month][devId] = count;
            }
        }
    }
    
    // Если нет видимых разработчиков, показываем сообщение
    if (Object.keys(developerNames).length === 0) {
        chartDiv.innerHTML = '<p>Нет видимых разработчиков для отображения графика</p>';
        return;
    }
    
    // Если нет данных распределения, показываем сообщение
    if (Object.keys(commitDistributions).length === 0) {
        chartDiv.innerHTML = '<p>Нет данных о распределении коммитов по времени</p>';
        return;
    }
    
    // Собираем все месяцы и сортируем их
    const months = Object.keys(commitDistributions).sort();
    
    // Создаем наборы данных для каждого разработчика
    const datasets = [];
    const colorPalette = generateColorPalette(Object.keys(developerNames).length);
    
    let colorIndex = 0;
    for (const devId of Object.keys(developerNames)) {
        const data = months.map(month => commitDistributions[month][devId] || 0);
        
        datasets.push({
            label: developerNames[devId],
            data: data,
            backgroundColor: colorPalette[colorIndex],
            borderColor: adjustColorAlpha(colorPalette[colorIndex], 1),
            borderWidth: 1,
            fill: false,
            tension: 0.1 // Небольшое сглаживание линии
        });
        
        colorIndex++;
    }
    
    // Создаем обертку для канваса с фиксированной высотой
    const chartWrapper = document.createElement('div');
    chartWrapper.style.height = '400px';
    chartWrapper.style.width = '100%';
    chartDiv.appendChild(chartWrapper);
    
    // Создаем график с помощью Chart.js
    const ctx = document.createElement('canvas');
    chartWrapper.appendChild(ctx);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: months.map(m => {
                const [year, month] = m.split('-');
                return `${month}.${year}`;
            }),
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Активность разработчиков по времени'
                },
                legend: {
                    position: 'top',
                    labels: {
                        boxWidth: 15,
                        font: {
                            size: 11
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Количество коммитов'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Месяц'
                    },
                    ticks: {
                        autoSkip: true,
                        maxTicksLimit: 12,
                        font: {
                            size: 10
                        }
                    }
                }
            },
            interaction: {
                mode: 'index',
                intersect: false
            }
        }
    });
    
    // Добавляем кнопку для переключения между видами графика
    const toggleButton = document.createElement('button');
    toggleButton.textContent = 'Переключить вид графика';
    toggleButton.style.margin = '10px 0';
    toggleButton.style.padding = '5px 10px';
    toggleButton.style.cursor = 'pointer';
    toggleButton.addEventListener('click', function() {
        const chart = Chart.getChart(ctx);
        if (chart) {
            // Переключаем тип графика между линейным и столбчатым
            const newType = chart.config.type === 'line' ? 'bar' : 'line';
            chart.config.type = newType;
            chart.update();
        }
    });
    
    chartDiv.appendChild(toggleButton);
}