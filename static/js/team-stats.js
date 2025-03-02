/**
 * Модуль для отображения статистики по команде
 */

/**
 * Отображает статистику команды
 * @param {Object} teamStats - данные о команде
 */
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
                <div class="subtitle">${calculatePercentage(teamStats.total_substantial_commits, teamStats.total_commits)}% от общего числа</div>
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
    `;
    
    // Проверяем, есть ли информация о ключевых разработчиках
    if (teamStats.most_active_developer || 
        teamStats.most_impactful_developer || 
        teamStats.most_prolific_developer) {
        
        html += `
            <h3>Ключевые разработчики</h3>
            <table>
                <tr>
                    <th>Категория</th>
                    <th>Разработчик</th>
                    <th>Показатель</th>
                </tr>
        `;
        
        // Добавляем информацию о наиболее активном разработчике
        if (teamStats.most_active_developer && 
            !window.hiddenDevelopers.has(teamStats.most_active_developer.id)) {
            html += `
                <tr>
                    <td>Наиболее активный</td>
                    <td>${teamStats.most_active_developer.name}</td>
                    <td>${teamStats.most_active_developer.commits} коммитов</td>
                </tr>
            `;
        }
        
        // Добавляем информацию о наиболее влиятельном разработчике
        if (teamStats.most_impactful_developer && 
            !window.hiddenDevelopers.has(teamStats.most_impactful_developer.id)) {
            html += `
                <tr>
                    <td>Наиболее влиятельный</td>
                    <td>${teamStats.most_impactful_developer.name}</td>
                    <td>Влияние: ${Math.round(teamStats.most_impactful_developer.impact)}</td>
                </tr>
            `;
        }
        
        // Добавляем информацию о наиболее продуктивном разработчике
        if (teamStats.most_prolific_developer && 
            !window.hiddenDevelopers.has(teamStats.most_prolific_developer.id)) {
            html += `
                <tr>
                    <td>Наиболее продуктивный</td>
                    <td>${teamStats.most_prolific_developer.name}</td>
                    <td>${teamStats.most_prolific_developer.lines_added} строк кода</td>
                </tr>
            `;
        }
        
        html += `</table>`;
    }
    
    teamStatsDiv.innerHTML = html;
}

/**
 * Отображает метаданные
 * @param {Object} metadata - метаданные
 */
function displayMetadata(metadata) {
    const metadataDiv = document.getElementById('metadata');
    if (!metadataDiv) return;
    
    let html = `
        <p>Сгенерировано: ${metadata.generated_at}</p>
        <p>Количество разработчиков: ${metadata.developer_count}</p>
    `;
    
    // Добавляем дополнительные метаданные, если они есть
    if (metadata.report_period) {
        html += `<p>Период анализа: ${metadata.report_period}</p>`;
    }
    
    if (metadata.repository) {
        html += `<p>Репозиторий: ${metadata.repository}</p>`;
    }
    
    if (metadata.branch) {
        html += `<p>Ветка: ${metadata.branch}</p>`;
    }
    
    metadataDiv.innerHTML = html;
}

/**
 * Обновляет статистику команды с учетом скрытых разработчиков
 * @param {Object} data - данные Git-статистики
 */
function updateTeamStats(data) {
    // Если нет данных о команде, выходим
    if (!data.team_stats) return;
    
    // Копируем статистику команды
    const teamStats = {...data.team_stats};
    
    // Пересчитываем статистику, исключая скрытых разработчиков
    if (window.hiddenDevelopers.size > 0) {
        // Пересчитываем общие показатели
        teamStats.total_commits = 0;
        teamStats.total_substantial_commits = 0;
        teamStats.total_lines_added = 0;
        teamStats.total_lines_removed = 0;
        
        // Собираем данные только по видимым разработчикам
        Object.entries(data.developers).forEach(([devId, stats]) => {
            if (!window.hiddenDevelopers.has(devId)) {
                teamStats.total_commits += stats.total_commits;
                teamStats.total_substantial_commits += stats.substantial_commits;
                teamStats.total_lines_added += stats.lines_added;
                teamStats.total_lines_removed += stats.lines_removed;
            }
        });
        
        // Находим новых ключевых разработчиков среди видимых
        if (teamStats.most_active_developer && 
            window.hiddenDevelopers.has(teamStats.most_active_developer.id)) {
            // Находим нового наиболее активного разработчика
            let maxCommits = 0;
            let mostActive = null;
            
            Object.entries(data.developers).forEach(([devId, stats]) => {
                if (!window.hiddenDevelopers.has(devId) && stats.total_commits > maxCommits) {
                    maxCommits = stats.total_commits;
                    mostActive = {
                        id: devId,
                        name: stats.name,
                        commits: stats.total_commits
                    };
                }
            });
            
            teamStats.most_active_developer = mostActive;
        }
        
        // Аналогично для наиболее влиятельного разработчика
        if (teamStats.most_impactful_developer && 
            window.hiddenDevelopers.has(teamStats.most_impactful_developer.id)) {
            let maxImpact = 0;
            let mostImpactful = null;
            
            Object.entries(data.developers).forEach(([devId, stats]) => {
                if (!window.hiddenDevelopers.has(devId) && stats.commit_impact > maxImpact) {
                    maxImpact = stats.commit_impact;
                    mostImpactful = {
                        id: devId,
                        name: stats.name,
                        impact: stats.commit_impact
                    };
                }
            });
            
            teamStats.most_impactful_developer = mostImpactful;
        }
        
        // Аналогично для наиболее продуктивного разработчика
        if (teamStats.most_prolific_developer && 
            window.hiddenDevelopers.has(teamStats.most_prolific_developer.id)) {
            let maxLines = 0;
            let mostProlific = null;
            
            Object.entries(data.developers).forEach(([devId, stats]) => {
                if (!window.hiddenDevelopers.has(devId) && stats.lines_added > maxLines) {
                    maxLines = stats.lines_added;
                    mostProlific = {
                        id: devId,
                        name: stats.name,
                        lines_added: stats.lines_added
                    };
                }
            });
            
            teamStats.most_prolific_developer = mostProlific;
        }
    }
    
    // Отображаем обновленную статистику
    displayTeamStats(teamStats);
}