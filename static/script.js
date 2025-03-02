// Код для визуализации статистики Git
document.addEventListener('DOMContentLoaded', function() {
    // Функция будет вызвана при загрузке HTML-документа
    console.log('Git Developer Statistics Visualization loaded');
    
    // Функция для загрузки JSON-данных
    function loadData(jsonUrl) {
        fetch(jsonUrl)
            .then(response => response.json())
            .then(data => {
                displayData(data);
            })
            .catch(error => {
                console.error('Error loading data:', error);
                document.getElementById('error-message').textContent = 
                    `Не удалось загрузить данные: ${error.message}`;
                document.getElementById('error-container').style.display = 'block';
            });
    }
    
    // Функция для отображения данных
    function displayData(data) {
        // Отображаем метаданные
        displayMetadata(data.metadata);
        
        // Отображаем статистику команды
        displayTeamStats(data.team_stats);
        
        // Отображаем рейтинг полезности
        displayUsefulnessRating(data.usefulness_rating, data.developers);
        
        // Отображаем статистику разработчиков
        displayDeveloperStats(data.developers);
        
        // Создаем графики
        createCommitChart(data);
        createImpactChart(data);
        createContributionTimeline(data);
    }
    
    // Функция для отображения метаданных
    function displayMetadata(metadata) {
        const metadataDiv = document.getElementById('metadata');
        if (!metadataDiv) return;
        
        metadataDiv.innerHTML = `
            <p>Сгенерировано: ${metadata.generated_at}</p>
            <p>Количество разработчиков: ${metadata.developer_count}</p>
        `;
    }
    
    // Функция для отображения статистики команды
    function displayTeamStats(teamStats) {
        const teamStatsDiv = document.getElementById('team-stats');
        if (!teamStatsDiv) return;
        
        let html = `
            <h2>Статистика команды</h2>
            <div class="stat-grid">
                <div class="stat-box">
                    <div class="title">Всего коммитов</div>
                    <div class="value">${teamStats.total_commits}</div>
                </div>
                <div class="stat-box">
                    <div class="title">Существенные коммиты</div>
                    <div class="value">${teamStats.total_substantial_commits}</div>
                </div>
                <div class="stat-box">
                    <div class="title">Добавлено строк</div>
                    <div class="value">${teamStats.total_lines_added}</div>
                </div>
                <div class="stat-box">
                    <div class="title">Удалено строк</div>
                    <div class="value">${teamStats.total_lines_removed}</div>
                </div>
            </div>
            
            <h3>Ключевые разработчики</h3>
            <table>
                <tr>
                    <th>Категория</th>
                    <th>Разработчик</th>
                    <th>Показатель</th>
                </tr>
                <tr>
                    <td>Наиболее активный</td>
                    <td>${teamStats.most_active_developer.name}</td>
                    <td>${teamStats.most_active_developer.commits} коммитов</td>
                </tr>
                <tr>
                    <td>Наиболее влиятельный</td>
                    <td>${teamStats.most_impactful_developer.name}</td>
                    <td>Влияние: ${Math.round(teamStats.most_impactful_developer.impact)}</td>
                </tr>
                <tr>
                    <td>Наиболее продуктивный</td>
                    <td>${teamStats.most_prolific_developer.name}</td>
                    <td>${teamStats.most_prolific_developer.lines_added} строк кода</td>
                </tr>
            </table>
        `;
        
        teamStatsDiv.innerHTML = html;
    }
    
    // Функция для отображения рейтинга полезности
    function displayUsefulnessRating(usefulnessRating, developers) {
        const ratingDiv = document.getElementById('usefulness-rating');
        if (!ratingDiv) return;
        
        let html = `<h2>Рейтинг полезности разработчиков</h2>`;
        
        html += `<table>
            <tr>
                <th>Место</th>
                <th>Разработчик</th>
                <th>Рейтинг</th>
                <th>Факторы</th>
            </tr>`;
            
        let rank = 1;
        for (const [devId, rating] of Object.entries(usefulnessRating)) {
            const devName = developers[devId] ? developers[devId].name : devId;
            
            html += `
                <tr>
                    <td>${rank}</td>
                    <td>${devName}</td>
                    <td>
                        <div class="usefulness-meter">
                            <div class="fill" style="width: ${rating.score}%"></div>
                        </div>
                        <div>${rating.score.toFixed(2)}</div>
                    </td>
                    <td>
                        <details>
                            <summary>Детали</summary>
                            <ul>
                                <li>Существенные коммиты: ${rating.factors.substantial_commits}%</li>
                                <li>Вклад в строки кода: ${rating.factors.lines_contributed}%</li>
                                <li>Влияние коммитов: ${rating.factors.commit_impact}%</li>
                                <li>Соотношение значимых коммитов: ${rating.factors.substantive_ratio}%</li>
                                <li>Штраф за реверты: ${rating.factors.revert_penalty}%</li>
                                <li>Ежедневная активность: ${rating.factors.daily_activity}%</li>
                            </ul>
                        </details>
                    </td>
                </tr>
            `;
            
            rank++;
        }
        
        html += `</table>`;
        ratingDiv.innerHTML = html;
    }
    
    // Функция для отображения статистики разработчиков
    function displayDeveloperStats(developers) {
        const developerStatsDiv = document.getElementById('developer-stats');
        if (!developerStatsDiv) return;
        
        let html = '<h2>Статистика по разработчикам</h2>';
        
        // Сортируем разработчиков по количеству коммитов (по убыванию)
        const sortedDevelopers = Object.entries(developers).sort((a, b) => b[1].total_commits - a[1].total_commits);
        
        for (const [devId, stats] of sortedDevelopers) {
            const substantivePercentage = stats.total_commits > 0 
                ? Math.round(stats.substantial_commits / stats.total_commits * 100) 
                : 0;
                
            html += `
                <div class="developer-card">
                    <h3>${stats.name} &lt;${devId}&gt;</h3>
                    <div class="stat-grid">
                        <div class="stat-box">
                            <div class="title">Период активности</div>
                            <div class="value">${stats.active_days} дней</div>
                            <div class="subtitle">${stats.first_commit_date} — ${stats.last_commit_date}</div>
                        </div>
                        <div class="stat-box">
                            <div class="title">Всего коммитов</div>
                            <div class="value">${stats.total_commits}</div>
                        </div>
                        <div class="stat-box">
                            <div class="title">Существенные коммиты</div>
                            <div class="value">${stats.substantial_commits}</div>
                            <div class="subtitle">${substantivePercentage}% от общего числа</div>
                        </div>
                        <div class="stat-box">
                            <div class="title">Добавлено строк</div>
                            <div class="value">${stats.lines_added}</div>
                        </div>
                    </div>
                    
                    <h4>Детальная статистика</h4>
                    <table>
                        <tr>
                            <th>Показатель</th>
                            <th>Значение</th>
                        </tr>
                        <tr>
                            <td>Удалено строк</td>
                            <td>${stats.lines_removed}</td>
                        </tr>
                        <tr>
                            <td>Влияние коммитов</td>
                            <td>${Math.round(stats.commit_impact)}</td>
                        </tr>
                        <tr>
                            <td>Средний размер коммита</td>
                            <td>${Math.round(stats.average_commit_size)} строк</td>
                        </tr>
                        <tr>
                            <td>Revert-коммиты</td>
                            <td>${stats.reverts_count}</td>
                        </tr>
                        <tr>
                            <td>Потенциальные squash-коммиты</td>
                            <td>${stats.squash_count || 0}</td>
                        </tr>
                    </table>
                </div>
            `;
        }
        
        developerStatsDiv.innerHTML = html;
    }
    
    // Функция для создания графика коммитов
    function createCommitChart(data) {
        const chartDiv = document.getElementById('commit-chart');
        if (!chartDiv || typeof Chart === 'undefined') return;
        
        // Извлекаем данные для графика
        const developers = Object.keys(data.developers);
        const developerNames = developers.map(dev => data.developers[dev].name);
        const commitCounts = developers.map(dev => data.developers[dev].total_commits);
        const substantialCommitCounts = developers.map(dev => data.developers[dev].substantial_commits);
        
        // Создаем график с помощью Chart.js
        const ctx = document.createElement('canvas');
        chartDiv.appendChild(ctx);
        
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
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Количество коммитов по разработчикам'
                    },
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Количество коммитов'
                        }
                    }
                }
            }
        });
    }
    
    // Функция для создания графика влияния
    function createImpactChart(data) {
        const chartDiv = document.getElementById('impact-chart');
        if (!chartDiv || typeof Chart === 'undefined') return;
        
        // Извлекаем данные для графика
        const developers = Object.keys(data.developers);
        const developerNames = developers.map(dev => data.developers[dev].name);
        const impactValues = developers.map(dev => data.developers[dev].commit_impact);
        const linesAdded = developers.map(dev => data.developers[dev].lines_added);
        const linesRemoved = developers.map(dev => data.developers[dev].lines_removed);
        
        // Создаем график с помощью Chart.js
        const ctx = document.createElement('canvas');
        chartDiv.appendChild(ctx);
        
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
                plugins: {
                    title: {
                        display: true,
                        text: 'Влияние разработчиков'
                    },
                    legend: {
                        position: 'top'
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
                    }
                }
            }
        });
    }
    
    // Функция для создания временной шкалы вклада
    function createContributionTimeline(data) {
        const chartDiv = document.getElementById('timeline-chart');
        if (!chartDiv || typeof Chart === 'undefined') return;
        
        // Извлекаем данные для графика временной шкалы
        const commitDistributions = {};
        const developerNames = {};
        
        for (const [devId, stats] of Object.entries(data.developers)) {
            developerNames[devId] = stats.name;
            
            // Добавляем распределение коммитов этого разработчика
            for (const [month, count] of Object.entries(stats.commit_distribution)) {
                if (!commitDistributions[month]) {
                    commitDistributions[month] = {};
                }
                commitDistributions[month][devId] = count;
            }
        }
        
        // Собираем все месяцы и сортируем их
        const months = Object.keys(commitDistributions).sort();
        
        // Создаем наборы данных для каждого разработчика
        const datasets = [];
        const colorPalette = [
            'rgba(54, 162, 235, 0.7)',
            'rgba(255, 99, 132, 0.7)',
            'rgba(75, 192, 192, 0.7)',
            'rgba(255, 159, 64, 0.7)',
            'rgba(153, 102, 255, 0.7)',
            'rgba(255, 205, 86, 0.7)',
            'rgba(201, 203, 207, 0.7)',
            'rgba(255, 99, 71, 0.7)',
            'rgba(46, 139, 87, 0.7)',
            'rgba(106, 90, 205, 0.7)'
        ];
        
        let colorIndex = 0;
        for (const devId of Object.keys(developerNames)) {
            const data = months.map(month => commitDistributions[month][devId] || 0);
            
            datasets.push({
                label: developerNames[devId],
                data: data,
                backgroundColor: colorPalette[colorIndex % colorPalette.length],
                borderColor: colorPalette[colorIndex % colorPalette.length].replace('0.7', '1'),
                borderWidth: 1
            });
            
            colorIndex++;
        }
        
        // Создаем график с помощью Chart.js
        const ctx = document.createElement('canvas');
        chartDiv.appendChild(ctx);
        
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
                plugins: {
                    title: {
                        display: true,
                        text: 'Активность разработчиков по времени'
                    },
                    legend: {
                        position: 'top'
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
                        }
                    }
                }
            }
        });
    }
    
    // Пытаемся загрузить данные, если указан URL JSON
    const jsonUrl = document.getElementById('data-url');
    if (jsonUrl && jsonUrl.value) {
        loadData(jsonUrl.value);
    }
});
