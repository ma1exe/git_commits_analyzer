// Скрипт для автономного HTML-отчета
document.addEventListener('DOMContentLoaded', function() {
    console.log('Git Developer Statistics Visualization loaded');
    
    // Загружаем данные из встроенного JSON
    const data = window.gitAnalysisData;
    if (data) {
        // Установка скрытых разработчиков из метаданных
        window.hiddenDevelopers = new Set(data.metadata.excluded_developers || []);
        
        // Добавляем панель управления видимостью разработчиков
        addDeveloperVisibilityControls(data);
        
        // Отображаем данные
        displayData(data);
    } else {
        console.error('Data not found!');
        document.getElementById('error-message').textContent = 'Ошибка: Данные не найдены!';
        document.getElementById('error-container').style.display = 'block';
    }
    
// Функция для добавления элементов управления видимостью разработчиков
    function addDeveloperVisibilityControls(data) {
        // Создаем контейнер для элементов управления
        const controlsDiv = document.createElement('div');
        controlsDiv.className = 'developer-visibility-controls';
        controlsDiv.style.margin = '20px 0';
        controlsDiv.style.padding = '15px';
        controlsDiv.style.background = '#f8f9fa';
        controlsDiv.style.borderRadius = '8px';
        controlsDiv.style.border = '1px solid #e1e4e8';
        
        // Заголовок
        const title = document.createElement('h3');
        title.textContent = 'Управление видимостью разработчиков';
        title.style.marginTop = '0';
        controlsDiv.appendChild(title);
        
        // Контейнер для чекбоксов
        const checkboxesDiv = document.createElement('div');
        checkboxesDiv.style.display = 'flex';
        checkboxesDiv.style.flexWrap = 'wrap';
        checkboxesDiv.style.gap = '10px';
        
        // Получаем список всех разработчиков
        const developers = Object.entries(data.developers).map(([email, dev]) => ({
            email: email,
            name: dev.name
        }));
        
        // Сортируем разработчиков по имени
        developers.sort((a, b) => a.name.localeCompare(b.name));
        
        // Создаем чекбоксы для каждого разработчика
        developers.forEach(dev => {
            const label = document.createElement('label');
            label.style.display = 'flex';
            label.style.alignItems = 'center';
            label.style.padding = '5px 10px';
            label.style.background = '#fff';
            label.style.border = '1px solid #ddd';
            label.style.borderRadius = '4px';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = dev.email;
            checkbox.checked = !window.hiddenDevelopers.has(dev.email);
            checkbox.style.marginRight = '5px';
            
            // Обработчик изменения видимости
            checkbox.addEventListener('change', function() {
                if (this.checked) {
                    window.hiddenDevelopers.delete(dev.email);
                } else {
                    window.hiddenDevelopers.add(dev.email);
                }
                
                // Обновляем отображение всех данных
                updateVisibility(data);
            });
            
            label.appendChild(checkbox);
            label.appendChild(document.createTextNode(`${dev.name} <${dev.email}>`));
            
            checkboxesDiv.appendChild(label);
        });
        
        controlsDiv.appendChild(checkboxesDiv);
        
        // Кнопки "Показать всех" и "Скрыть всех"
        const buttonsDiv = document.createElement('div');
        buttonsDiv.style.marginTop = '10px';
        
        const showAllButton = document.createElement('button');
        showAllButton.textContent = 'Показать всех';
        showAllButton.style.marginRight = '10px';
        showAllButton.style.padding = '5px 10px';
        showAllButton.addEventListener('click', function() {
            window.hiddenDevelopers.clear();
            document.querySelectorAll('.developer-visibility-controls input[type="checkbox"]').forEach(cb => {
                cb.checked = true;
            });
            updateVisibility(data);
        });
        
        const hideAllButton = document.createElement('button');
        hideAllButton.textContent = 'Скрыть всех';
        hideAllButton.style.padding = '5px 10px';
        hideAllButton.addEventListener('click', function() {
            developers.forEach(dev => {
                window.hiddenDevelopers.add(dev.email);
            });
            document.querySelectorAll('.developer-visibility-controls input[type="checkbox"]').forEach(cb => {
                cb.checked = false;
            });
            updateVisibility(data);
        });
        
        buttonsDiv.appendChild(showAllButton);
        buttonsDiv.appendChild(hideAllButton);
        
        controlsDiv.appendChild(buttonsDiv);
        
        // Вставляем контейнер сразу после информации о весах
        const weightInfo = document.querySelector('.weight-info');
        if (weightInfo) {
            weightInfo.parentNode.insertBefore(controlsDiv, weightInfo.nextSibling);
        } else {
            // Если нет информации о весах, вставляем в начало секции с графиками
            const chartSection = document.querySelector('.chart-section');
            if (chartSection) {
                chartSection.insertBefore(controlsDiv, chartSection.firstChild.nextSibling);
            }
        }
    }
    
    // Функция для обновления видимости всех элементов
    function updateVisibility(data) {
        // Перерисовываем графики
        redrawCharts(data);
        
        // Обновляем рейтинг полезности
        updateUsefulnessRatingVisibility(data);
        
        // Обновляем статистику разработчиков
        updateDeveloperStatsVisibility(data);
    }
    
    // Функция для обновления видимости рейтинга полезности
    function updateUsefulnessRatingVisibility(data) {
        const ratingDiv = document.getElementById('usefulness-rating');
        if (!ratingDiv) return;
        
        // Очищаем текущее содержимое
        ratingDiv.innerHTML = '';
        
        // Заново отображаем рейтинг, учитывая скрытых разработчиков
        let html = `<h2>Рейтинг полезности разработчиков</h2>`;
        
        html += `<table>
            <tr>
                <th>Место</th>
                <th>Разработчик</th>
                <th>Рейтинг</th>
                <th>Факторы</th>
            </tr>`;
            
        let rank = 1;
        // Фильтруем и сортируем рейтинг
        const filteredRating = Object.entries(data.usefulness_rating)
            .filter(([devId, _]) => !window.hiddenDevelopers.has(devId))
            .sort((a, b) => b[1].score - a[1].score);
            
        for (const [devId, rating] of filteredRating) {
            const devName = data.developers[devId] ? data.developers[devId].name : devId;
            
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
                                ${rating.factors.merge_penalty !== undefined ? 
                                `<li>Штраф за мерджи: ${rating.factors.merge_penalty}%</li>` : ''}
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
    
    // Функция для обновления видимости статистики разработчиков
    function updateDeveloperStatsVisibility(data) {
        const developerStatsDiv = document.getElementById('developer-stats');
        if (!developerStatsDiv) return;
        
        // Очищаем текущее содержимое
        developerStatsDiv.innerHTML = '';
        
        let html = '<h2>Статистика по разработчикам</h2>';
        
        // Фильтруем и сортируем разработчиков
        const filteredDevelopers = Object.entries(data.developers)
            .filter(([devId, _]) => !window.hiddenDevelopers.has(devId))
            .sort((a, b) => b[1].total_commits - a[1].total_commits);
        
        for (const [devId, stats] of filteredDevelopers) {
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
                        ${stats.merge_count !== undefined ? `
                        <tr>
                            <td>Merge-коммиты</td>
                            <td>${stats.merge_count}</td>
                        </tr>` : ''}
                    </table>
                </div>
            `;
        }
        
        developerStatsDiv.innerHTML = html;
    }
    
    // Функция для перерисовки графиков
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
    
    // Функция для отображения данных
    function displayData(data) {
        // Установка скрытых разработчиков из метаданных
        window.hiddenDevelopers = new Set(data.metadata.excluded_developers || []);
        
        // Добавление информации о весах параметров в начало страницы
        displayWeightsInfo(data);
        
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

    // Функция для добавления информации о весах параметров
    function displayWeightsInfo(data) {
        const weightInfoDiv = document.createElement('div');
        weightInfoDiv.className = 'weight-info';
        weightInfoDiv.style.margin = '20px 0';
        weightInfoDiv.style.padding = '15px';
        weightInfoDiv.style.background = '#f8f9fa';
        weightInfoDiv.style.borderRadius = '8px';
        weightInfoDiv.style.border = '1px solid #e1e4e8';
        
        const weightTitle = document.createElement('h2');
        weightTitle.textContent = 'Параметры оценки полезности разработчиков';
        weightTitle.style.marginTop = '0';
        weightInfoDiv.appendChild(weightTitle);
        
        const weightText = document.createElement('p');
        weightText.textContent = 'Рейтинг полезности рассчитывается на основе следующих параметров с указанными весами:';
        weightInfoDiv.appendChild(weightText);
        
        // Получаем используемые веса
        const weights = data.weights_used || {
            substantial_commits: 0.3,
            lines: 0.15,
            impact: 0.25,
            substantive_ratio: 0.2,
            revert_penalty: -0.1,
            daily_activity: 0.2,
            merge_penalty: -0.05
        };
        
        // Получаем описания факторов
        let factorDescriptions = {};
        if (data.usefulness_rating && Object.keys(data.usefulness_rating).length > 0) {
            const firstDevId = Object.keys(data.usefulness_rating)[0];
            factorDescriptions = data.usefulness_rating[firstDevId].factor_descriptions || {};
        }
        
        // Стандартные описания на случай, если их нет в данных
        const defaultDescriptions = {
            substantial_commits: 'Коммиты с существенными изменениями. Отражает способность разработчика делать осмысленные, значимые изменения.',
            lines: 'Общее количество строк, добавленных и удаленных. Отражает объем выполненной работы.',
            impact: 'Влияние коммитов на кодовую базу. Учитывает как количество измененных файлов, так и объем изменений.',
            substantive_ratio: 'Доля существенных коммитов к общему числу. Отражает качество и значимость вносимых изменений.',
            revert_penalty: 'Штраф за отмену коммитов (revert). Отражает стабильность и надежность вносимых изменений.',
            daily_activity: 'Регулярность и стабильность активности. Учитывает равномерность вклада во времени.',
            merge_penalty: 'Штраф за merge-коммиты. Отражает работу по интеграции чужого кода.'
        };
        
        // Создаем таблицу весов
        const table = document.createElement('table');
        table.style.width = '100%';
        table.style.borderCollapse = 'collapse';
        table.style.marginTop = '10px';
        
        // Заголовок таблицы
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        ['Параметр', 'Вес', 'Описание'].forEach(text => {
            const th = document.createElement('th');
            th.textContent = text;
            th.style.padding = '8px';
            th.style.textAlign = 'left';
            th.style.borderBottom = '2px solid #ddd';
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);
        
        // Тело таблицы
        const tbody = document.createElement('tbody');
        
        // Человеко-читаемые названия параметров
        const paramNames = {
            substantial_commits: 'Существенные коммиты',
            lines: 'Количество строк',
            impact: 'Влияние коммитов',
            substantive_ratio: 'Доля значимых коммитов',
            revert_penalty: 'Штраф за реверты',
            daily_activity: 'Регулярность активности',
            merge_penalty: 'Штраф за мерджи'
        };
        
        // Добавляем строки с параметрами
        Object.entries(weights).forEach(([param, value]) => {
            const tr = document.createElement('tr');
            
            // Название параметра
            const tdName = document.createElement('td');
            tdName.textContent = paramNames[param] || param;
            tdName.style.padding = '8px';
            tdName.style.borderBottom = '1px solid #ddd';
            tr.appendChild(tdName);
            
            // Вес параметра
            const tdWeight = document.createElement('td');
            tdWeight.textContent = value.toFixed(2);
            tdWeight.style.padding = '8px';
            tdWeight.style.borderBottom = '1px solid #ddd';
            tr.appendChild(tdWeight);
            
            // Описание параметра
            const tdDesc = document.createElement('td');
            tdDesc.textContent = factorDescriptions[param] || defaultDescriptions[param] || '';
            tdDesc.style.padding = '8px';
            tdDesc.style.borderBottom = '1px solid #ddd';
            tr.appendChild(tdDesc);
            
            tbody.appendChild(tr);
        });
        
        table.appendChild(tbody);
        weightInfoDiv.appendChild(table);
        
        // Вставляем в начало контейнера, сразу после заголовка
        const container = document.querySelector('.container');
        const heading = container.querySelector('h1');
        container.insertBefore(weightInfoDiv, heading.nextSibling);
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
            

                ${metrics && metrics.advanced_metrics ? createAdvancedMetricsSection(stats) : ""}`;
        }
        
        developerStatsDiv.innerHTML = html;
    }

// Функция для создания графика коммитов
    function createCommitChart(data) {
        const chartDiv = document.getElementById('commit-chart');
        if (!chartDiv || typeof Chart === 'undefined') return;
        
        // Извлекаем данные для графика, исключая скрытых разработчиков
        const developers = Object.keys(data.developers).filter(dev => !window.hiddenDevelopers.has(dev));
        const developerNames = developers.map(dev => data.developers[dev].name);
        const commitCounts = developers.map(dev => data.developers[dev].total_commits);
        const substantialCommitCounts = developers.map(dev => data.developers[dev].substantial_commits);
        const squashCommitCounts = developers.map(dev => data.developers[dev].squash_count || 0);
        const mergeCommitCounts = developers.map(dev => data.developers[dev].merge_count || 0);
        
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
                    },
                    zoom: {
                        pan: {
                            enabled: true,
                            mode: 'xy'
                        },
                        zoom: {
                            wheel: {
                                enabled: true,
                            },
                            pinch: {
                                enabled: true
                            },
                            mode: 'xy'
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
                            autoSkip: false,
                            maxRotation: 45,
                            minRotation: 45
                        }
                    }
                }
            }
        });
        
        // Устанавливаем высоту графика
        ctx.parentNode.style.height = '400px';
    }
    
    // Функция для создания графика влияния
    function createImpactChart(data) {
        const chartDiv = document.getElementById('impact-chart');
        if (!chartDiv || typeof Chart === 'undefined') return;
        
        // Извлекаем данные для графика, исключая скрытых разработчиков
        const developers = Object.keys(data.developers).filter(dev => !window.hiddenDevelopers.has(dev));
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
            // Пропускаем скрытых разработчиков
            if (window.hiddenDevelopers.has(devId)) continue;
            
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
});

// Функция для создания секции с расширенными метриками
function createAdvancedMetricsSection(developer) {
    if (!developer.advanced_metrics) {
        return '';
    }
    
    const metrics = developer.advanced_metrics;
    
    // Создаем контейнер для дополнительных метрик
    const section = `
    <div class="advanced-metrics-section">
        <h3>Расширенная аналитика</h3>
        
        <div class="metrics-grid">
            <!-- Распределение по типам файлов -->
            <div class="metric-card" id="file-types-${developer.email.replace('@', '-').replace('.', '-')}">
                <h4>Типы файлов</h4>
                <canvas class="chart-canvas"></canvas>
            </div>
            
            <!-- Распределение по времени суток -->
            <div class="metric-card" id="time-dist-${developer.email.replace('@', '-').replace('.', '-')}">
                <h4>Активность по времени суток</h4>
                <canvas class="chart-canvas"></canvas>
            </div>
            
            <!-- Размеры коммитов -->
            <div class="metric-card" id="commit-sizes-${developer.email.replace('@', '-').replace('.', '-')}">
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
    
    // Добавляем скрипт для инициализации графиков после создания DOM
    setTimeout(() => {
        // График типов файлов
        if (metrics.file_type_distribution) {
            const fileTypesEl = document.getElementById(`file-types-${developer.email.replace('@', '-').replace('.', '-')}`);
            if (fileTypesEl) {
                const canvas = fileTypesEl.querySelector('canvas');
                const ctx = canvas.getContext('2d');
                
                const data = Object.entries(metrics.file_type_distribution)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 7); // Показываем топ-7 типов файлов
                
                new Chart(ctx, {
                    type: 'pie',
                    data: {
                        labels: data.map(([ext]) => ext),
                        datasets: [{
                            data: data.map(([_, count]) => count),
                            backgroundColor: [
                                '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', 
                                '#e74a3b', '#858796', '#5a5c69'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        legend: {
                            position: 'right',
                            labels: {
                                boxWidth: 12
                            }
                        }
                    }
                });
            }
        }
        
        // График активности по времени суток
        if (metrics.time_distribution) {
            const timeDistEl = document.getElementById(`time-dist-${developer.email.replace('@', '-').replace('.', '-')}`);
            if (timeDistEl) {
                const canvas = timeDistEl.querySelector('canvas');
                const ctx = canvas.getContext('2d');
                
                const periods = {
                    'morning': 'Утро (6-12)',
                    'afternoon': 'День (12-18)',
                    'evening': 'Вечер (18-23)',
                    'night': 'Ночь (23-6)'
                };
                
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: Object.values(periods),
                        datasets: [{
                            label: '% коммитов',
                            data: Object.keys(periods).map(key => metrics.time_distribution[key] || 0),
                            backgroundColor: [
                                '#f8c291', '#1cc88a', '#4e73df', '#5a5c69'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        legend: {
                            display: false
                        },
                        scales: {
                            yAxes: [{
                                ticks: {
                                    beginAtZero: true,
                                    callback: function(value) {
                                        return value + '%';
                                    }
                                }
                            }]
                        }
                    }
                });
            }
        }
        
        // График размеров коммитов
        if (metrics.commit_size_distribution) {
            const commitSizesEl = document.getElementById(`commit-sizes-${developer.email.replace('@', '-').replace('.', '-')}`);
            if (commitSizesEl) {
                const canvas = commitSizesEl.querySelector('canvas');
                const ctx = canvas.getContext('2d');
                
                const sizes = {
                    'small': 'Маленькие (<10)',
                    'medium': 'Средние (10-50)',
                    'large': 'Большие (>50)'
                };
                
                new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: Object.values(sizes),
                        datasets: [{
                            data: Object.keys(sizes).map(key => metrics.commit_size_distribution[key] || 0),
                            backgroundColor: [
                                '#1cc88a', '#4e73df', '#e74a3b'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        legend: {
                            position: 'right',
                            labels: {
                                boxWidth: 12
                            }
                        }
                    }
                });
            }
        }
    }, 100);
    
    return section;
}

// Функция для интеграции расширенных метрик в карточку разработчика
function enhanceDeveloperCard(developerCard, developerData) {
    if (!developerData.advanced_metrics) {
        return developerCard;
    }
    
    // Добавляем секцию с расширенными метриками
    const advancedSection = createAdvancedMetricsSection(developerData);
    
    // Находим конец карточки (перед закрывающим div)
    const insertIndex = developerCard.lastIndexOf('</div>');
    
    // Вставляем секцию с расширенными метриками
    return developerCard.substring(0, insertIndex) + advancedSection + developerCard.substring(insertIndex);
}

// Модификации для файла standalone_script.js
function modifyStandaloneScript(scriptContent) {
    // Добавляем стили для расширенных метрик
    const styleInsertPoint = scriptContent.indexOf('// Скрипт для автономного HTML-отчета');
    const modifiedScript = scriptContent.substring(0, styleInsertPoint) + 
                           `// Стили для расширенных метрик\n${advancedMetricsStyles}\n\n` + 
                           scriptContent.substring(styleInsertPoint);
    
    // Интегрируем отображение расширенных метрик
    const developerCardStart = modifiedScript.indexOf('function displayDeveloperStats(');
    const developerCardEnd = modifiedScript.indexOf('developerStatsDiv.innerHTML = html;', developerCardStart);
    
    // Находим шаблон карточки разработчика
    const cardTemplateStart = modifiedScript.indexOf('html += `', developerCardStart);
    const cardTemplateEnd = modifiedScript.indexOf('`;', cardTemplateStart);
    
    // Получаем текущий шаблон
    const cardTemplate = modifiedScript.substring(cardTemplateStart + 8, cardTemplateEnd);
    
    // Модифицируем шаблон для включения расширенных метрик
    const modifiedCardTemplate = cardTemplate + '\n${createAdvancedMetricsSection(stats)}';
    
    // Заменяем шаблон в скрипте
    const finalScript = modifiedScript.substring(0, cardTemplateStart + 8) + 
                        modifiedCardTemplate + 
                        modifiedScript.substring(cardTemplateEnd);
    
    // Добавляем функцию создания расширенных метрик
    return finalScript + '\n\n' + createAdvancedMetricsSection.toString();
}