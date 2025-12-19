/** Главное приложение */
let mapManager;
let uiManager;

document.addEventListener('DOMContentLoaded', () => {
    console.log('Инициализация приложения...');
    
    // Инициализация UI
    uiManager = new UIManager();
    window.uiManager = uiManager; // Для доступа из других модулей
    
    // Инициализация карты
    mapManager = new MapManager('map');
    mapManager.init();
    
    // Автоматическая загрузка данных при старте
    loadAllData();
    
    console.log('Приложение инициализировано');
});

async function loadAllData() {
    try {
        uiManager.showMessage('Загрузка данных...');
        
        // Загружаем все данные параллельно с улучшенной обработкой ошибок
        const [nodesResponse, volsResponse, fibersResponse, linksResponse] = await Promise.allSettled([
            api.getNodes(),
            api.getVols(),
            api.getFibers(),
            api.getLinks()
        ]).then(results => {
            return results.map((result, index) => {
                if (result.status === 'fulfilled') {
                    return result.value;
                } else {
                    const names = ['узлов', 'маршрутов', 'волокон', 'связей'];
                    console.error(`Ошибка загрузки ${names[index]}:`, result.reason);
                    const emptyResponses = [
                        { nodes: [], count: 0 },
                        { vols: [], count: 0 },
                        { fibers: [], count: 0 },
                        { links: [], count: 0 }
                    ];
                    return emptyResponses[index];
                }
            });
        });
        
        const nodes = nodesResponse.nodes || [];
        const volsList = volsResponse.vols || [];
        const fibers = fibersResponse.fibers || [];
        const links = linksResponse.links || [];
        
        console.log(`Загружено данных: ${nodes.length} узлов, ${volsList.length} маршрутов, ${fibers.length} волокон, ${links.length} связей`);
        
        // Обновляем статистику
        uiManager.updateStats({
            nodes: nodes.length,
            vols: volsList.length,
            fibers: fibers.length,
            links: links.length
        });
        
        // Очищаем карту
        mapManager.clearRoutes();
        mapManager.clearMarkers();
        
        // Загружаем маршруты на карту
        // OpenLayers использует [lon, lat], API возвращает [lon, lat] - порядок правильный
        for (const vols of volsList) {
            if (vols.path && Array.isArray(vols.path) && vols.path.length >= 2) {
                // API возвращает [lon, lat], OpenLayers тоже использует [lon, lat]
                mapManager.addRoute(vols.path, vols.name, vols);
            }
        }
        
        // Загружаем узлы на карту
        // OpenLayers использует [lon, lat], поэтому передаем lon, lat
        nodes.forEach(node => {
            if (node.lat && node.lon) {
                mapManager.addMarker(node.lat, node.lon, node.name, node);
            }
        });
        
        // Обновляем все списки в UI
        uiManager.showNodesList(nodes);
        uiManager.showVolsList(volsList);
        
        // Обновляем списки волокон и связей, если соответствующие панели открыты
        const currentPanel = uiManager.currentPanel;
        if (currentPanel === 'fibers' || document.getElementById('panel-fibers')?.style.display === 'block') {
            uiManager.showFibersList(fibers);
        }
        if (currentPanel === 'links' || document.getElementById('panel-links')?.style.display === 'block') {
            uiManager.showLinksList(links);
        }
        
        // Сохраняем данные волокон и связей для быстрого доступа
        uiManager.fibersCache = fibers;
        uiManager.linksCache = links;
        
        // Подгоняем карту под все объекты только если есть новые объекты
        if (nodes.length > 0 || volsList.length > 0) {
            // Не делаем fitBounds автоматически, чтобы не сбивать позицию пользователя
            // mapManager.fitBounds();
        }
        
        uiManager.showMessage(`Загружено: ${volsList.length} маршрутов, ${nodes.length} узлов`);
    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
        uiManager.showError(`Ошибка: ${error.message}`);
    }
}

// Экспортируем функцию для использования в других местах
window.loadRoutes = loadAllData;
