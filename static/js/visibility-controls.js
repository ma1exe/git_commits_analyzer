/**
 * Модуль для управления видимостью разработчиков в отчете
 */

/**
 * Добавляет элементы управления видимостью разработчиков
 * @param {Object} data - данные Git-статистики
 */
function addDeveloperVisibilityControls(data) {
    if (!data || !data.developers) return;
    
    // Создаем контейнер для элементов управления
    const controlsDiv = createElement('div', {
        class: 'developer-visibility-controls'
    });
    
    // Добавляем заголовок
    const title = createElement('h3', {}, 'Управление видимостью разработчиков');
    controlsDiv.appendChild(title);
    
    // Создаем контейнер для чекбоксов
    const checkboxesDiv = createElement('div', {
        class: 'checkboxes-container'
    });
    
    // Получаем список всех разработчиков
    const developers = Object.entries(data.developers).map(([email, dev]) => ({
        email,
        name: dev.name
    }));
    
    // Сортируем разработчиков по имени
    developers.sort((a, b) => a.name.localeCompare(b.name));
    
    // Создаем чекбоксы для каждого разработчика
    developers.forEach(dev => {
        const label = createElement('label', {
            class: 'developer-label'
        });
        
        const checkbox = createElement('input', {
            type: 'checkbox',
            value: dev.email,
            checked: !window.hiddenDevelopers.has(dev.email),
            class: 'developer-checkbox'
        });
        
        // Обработчик изменения видимости
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                window.hiddenDevelopers.delete(dev.email);
            } else {
                window.hiddenDevelopers.add(dev.email);
            }
            
            // Обновляем отображение всех данных
            updateAllSections(data);
        });
        
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(`${dev.name} <${dev.email}>`));
        
        checkboxesDiv.appendChild(label);
    });
    
    controlsDiv.appendChild(checkboxesDiv);
    
    // Кнопки "Показать всех" и "Скрыть всех"
    const buttonsDiv = createElement('div', {
        class: 'button-container'
    });
    
    const showAllButton = createElement('button', {
        class: 'control-button',
        type: 'button'
    }, 'Показать всех');
    
    showAllButton.addEventListener('click', function() {
        window.hiddenDevelopers.clear();
        document.querySelectorAll('.developer-visibility-controls input[type="checkbox"]').forEach(cb => {
            cb.checked = true;
        });
        updateAllSections(data);
    });
    
    const hideAllButton = createElement('button', {
        class: 'control-button',
        type: 'button'
    }, 'Скрыть всех');
    
    hideAllButton.addEventListener('click', function() {
        developers.forEach(dev => {
            window.hiddenDevelopers.add(dev.email);
        });
        document.querySelectorAll('.developer-visibility-controls input[type="checkbox"]').forEach(cb => {
            cb.checked = false;
        });
        updateAllSections(data);
    });
    
    buttonsDiv.appendChild(showAllButton);
    buttonsDiv.appendChild(hideAllButton);
    
    controlsDiv.appendChild(buttonsDiv);
    
    // Вставляем контейнер в нужное место в DOM
    insertVisibilityControls(controlsDiv);
}

/**
 * Вставляет элементы управления видимостью в DOM
 * @param {HTMLElement} controlsDiv - элемент с элементами управления
 */
function insertVisibilityControls(controlsDiv) {
    // Вставляем сразу после информации о весах
    const weightInfo = document.querySelector('.weight-info');
    if (weightInfo) {
        weightInfo.parentNode.insertBefore(controlsDiv, weightInfo.nextSibling);
        return;
    }
    
    // Если нет информации о весах, вставляем в начало секции с графиками
    const chartSection = document.querySelector('.chart-section');
    if (chartSection) {
        chartSection.insertBefore(controlsDiv, chartSection.firstChild.nextSibling);
        return;
    }
    
    // Если нет ни того, ни другого, вставляем после метаданных
    const metadataSection = document.getElementById('metadata');
    if (metadataSection) {
        metadataSection.parentNode.insertBefore(controlsDiv, metadataSection.nextSibling);
    }
}

/**
 * Обновляет отображение рейтинга полезности в соответствии с видимостью разработчиков
 * @param {Object} data - данные Git-статистики
 */
function updateUsefulnessRatingVisibility(data) {
    const ratingDiv = document.getElementById('usefulness-rating');
    if (!ratingDiv) return;
    
    // Очищаем текущее содержимое
    ratingDiv.innerHTML = '';
    
    // Получаем отфильтрованный рейтинг
    const filteredRating = getFilteredUsefulnessRating(data);
    
    // Если нет видимых разработчиков, показываем сообщение
    if (filteredRating.length === 0) {
        ratingDiv.innerHTML = '<h2>Рейтинг полезности разработчиков</h2><p>Нет видимых разработчиков для отображения рейтинга</p>';
        return;
    }
    
    // Заново отображаем рейтинг
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

/**
 * Обновляет отображение статистики разработчиков в соответствии с видимостью
 * @param {Object} data - данные Git-статистики
 */
function updateDeveloperStatsVisibility(data) {
    const developerStatsDiv = document.getElementById('developer-stats');
    if (!developerStatsDiv) return;
    
    // Очищаем текущее содержимое
    developerStatsDiv.innerHTML = '';
    
    // Получаем отфильтрованных разработчиков
    const filteredDevelopers = getFilteredDevelopers(data);
    
    // Если нет видимых разработчиков, показываем сообщение
    if (filteredDevelopers.length === 0) {
        developerStatsDiv.innerHTML = '<h2>Статистика по разработчикам</h2><p>Нет видимых разработчиков для отображения статистики</p>';
        return;
    }
    
    // Заново отображаем статистику
    let html = '<h2>Статистика по разработчикам</h2>';
    
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
            
            ${stats.advanced_metrics ? createAdvancedMetricsSection(stats) : ""}
        `;
    }
    
    developerStatsDiv.innerHTML = html;
}