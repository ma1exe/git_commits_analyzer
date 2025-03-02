/**
 * Модуль для отображения статистики по разработчикам
 */

/**
 * Отображает статистику разработчиков
 * @param {Object} developers - данные о разработчиках
 */
function displayDeveloperStats(developers) {
    const developerStatsDiv = document.getElementById('developer-stats');
    if (!developerStatsDiv) return;
    
    // Сортируем разработчиков по количеству коммитов (по убыванию)
    const sortedDevelopers = Object.entries(developers)
        .filter(([devId, _]) => !window.hiddenDevelopers.has(devId))
        .sort((a, b) => b[1].total_commits - a[1].total_commits);
    
    // Если нет видимых разработчиков, показываем сообщение
    if (sortedDevelopers.length === 0) {
        developerStatsDiv.innerHTML = '<h2>Статистика по разработчикам</h2><p>Нет видимых разработчиков для отображения статистики</p>';
        return;
    }
    
    let html = '<h2>Статистика по разработчикам</h2>';
    
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
                    ${stats.merge_count !== undefined ? `
                    <tr>
                        <td>Merge-коммиты</td>
                        <td>${stats.merge_count}</td>
                    </tr>` : ''}
                </table>
            </div>
            
            ${stats.advanced_metrics ? createAdvancedMetricsSection(stats) : ""}
        `;
    }
    
    developerStatsDiv.innerHTML = html;
}

/**
 * Отображает рейтинг полезности разработчиков
 * @param {Object} usefulnessRating - данные о рейтинге полезности
 * @param {Object} developers - данные о разработчиках
 */
function displayUsefulnessRating(usefulnessRating, developers) {
    const ratingDiv = document.getElementById('usefulness-rating');
    if (!ratingDiv) return;
    
    // Фильтруем и сортируем рейтинг
    const filteredRating = Object.entries(usefulnessRating)
        .filter(([devId, _]) => !window.hiddenDevelopers.has(devId))
        .sort((a, b) => b[1].score - a[1].score);
    
    // Если нет видимых разработчиков, показываем сообщение
    if (filteredRating.length === 0) {
        ratingDiv.innerHTML = '<h2>Рейтинг полезности разработчиков</h2><p>Нет видимых разработчиков для отображения рейтинга</p>';
        return;
    }
    
    let html = `<h2>Рейтинг полезности разработчиков</h2>`;
    
    html += `<table>
        <tr>
            <th>Место</th>
            <th>Разработчик</th>
            <th>Рейтинг</th>
            <th>Факторы</th>
        </tr>`;
        
    let rank = 1;
    
    for (const [devId, rating] of filteredRating) {
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

/**
 * Отображает информацию о параметрах оценки полезности
 * @param {Object} data - данные Git-статистики
 */
function displayWeightsInfo(data) {
    // Ищем контейнер или создаем новый
    let weightInfoDiv = document.querySelector('.weight-info');
    
    if (!weightInfoDiv) {
        weightInfoDiv = createElement('div', {
            class: 'weight-info'
        });
    }
    
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
    
    // Создаем HTML для таблицы весов
    let html = `
        <h2>Параметры оценки полезности разработчиков</h2>
        <p>Рейтинг полезности рассчитывается на основе следующих параметров с указанными весами:</p>
        <table>
            <thead>
                <tr>
                    <th>Параметр</th>
                    <th>Вес</th>
                    <th>Описание</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    // Добавляем строки с параметрами
    Object.entries(weights).forEach(([param, value]) => {
        html += `
            <tr>
                <td>${paramNames[param] || param}</td>
                <td>${value.toFixed(2)}</td>
                <td>${factorDescriptions[param] || defaultDescriptions[param] || ''}</td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
        </table>
    `;
    
    weightInfoDiv.innerHTML = html;
    
    // Вставляем в начало контейнера, сразу после заголовка
    const container = document.querySelector('.container');
    const heading = container.querySelector('h1');
    
    if (heading && !weightInfoDiv.parentNode) {
        container.insertBefore(weightInfoDiv, heading.nextSibling);
    }
}