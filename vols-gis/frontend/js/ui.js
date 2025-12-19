/** Управление UI элементами */
class UIManager {
    constructor() {
        this.currentPanel = 'info';
        this.currentNode = null;
        this.currentVols = null;
        this.currentFiber = null;
        this.currentLink = null;
        this.fibersCache = [];
        this.linksCache = [];
        this.init();
    }

    init() {
        console.log('UIManager инициализирован');
        
        // Обработчики навигации
        document.getElementById('nav-map')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.showPanel('info');
            this.setActiveNav('nav-map');
            // Показываем sidebar если он скрыт
            const sidebar = document.getElementById('sidebar');
            if (sidebar && sidebar.classList.contains('hidden')) {
                sidebar.classList.remove('hidden');
            }
        });
        
        document.getElementById('nav-nodes')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.showPanel('nodes');
            this.setActiveNav('nav-nodes');
        });
        
        document.getElementById('nav-vols')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.showPanel('vols');
            this.setActiveNav('nav-vols');
        });
        
        document.getElementById('nav-fibers')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.showPanel('fibers');
            this.setActiveNav('nav-fibers');
        });
        
        document.getElementById('nav-links')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.showPanel('links');
            this.setActiveNav('nav-links');
        });
        
        // Кнопка переключения боковой панели
        document.getElementById('btn-toggle-sidebar')?.addEventListener('click', () => {
            this.toggleSidebar();
        });
        
        document.getElementById('btn-close-sidebar')?.addEventListener('click', () => {
            this.toggleSidebar();
        });
        
        // Кнопка обновления
        document.getElementById('btn-refresh')?.addEventListener('click', () => {
            if (window.loadRoutes) {
                window.loadRoutes();
            }
        });
        
        // Кнопки инструментов редактирования
        document.getElementById('btn-draw-node')?.addEventListener('click', () => {
            this.toggleDrawNode();
        });
        
        document.getElementById('btn-draw-route')?.addEventListener('click', () => {
            this.toggleDrawRoute();
        });
        
        document.getElementById('btn-edit-mode')?.addEventListener('click', () => {
            this.toggleEditMode();
        });
        
        // Кнопки добавления волокон и связей
        document.getElementById('btn-add-fiber')?.addEventListener('click', () => {
            this.openFiberModal();
        });
        
        document.getElementById('btn-add-link')?.addEventListener('click', () => {
            this.openLinkModal();
        });
        
        // Обработчики сохранения
        document.getElementById('btn-save-fiber')?.addEventListener('click', () => {
            this.saveFiber();
        });
        
        document.getElementById('btn-save-link')?.addEventListener('click', () => {
            this.saveLink();
        });
    }

    toggleDrawNode() {
        if (window.mapManager) {
            const btn = document.getElementById('btn-draw-node');
            if (btn.classList.contains('active')) {
                window.mapManager.disableDraw();
                btn.classList.remove('active');
            } else {
                // Отключаем другие режимы
                document.getElementById('btn-draw-route')?.classList.remove('active');
                document.getElementById('btn-edit-mode')?.classList.remove('active');
                window.mapManager.disableDraw();
                if (window.mapManager.modifyInteraction) {
                    window.mapManager.map.removeInteraction(window.mapManager.modifyInteraction);
                }
                
                window.mapManager.enableDrawNode();
                btn.classList.add('active');
            }
        }
    }

    toggleDrawRoute() {
        if (window.mapManager) {
            const btn = document.getElementById('btn-draw-route');
            if (btn.classList.contains('active')) {
                window.mapManager.disableDraw();
                btn.classList.remove('active');
            } else {
                // Отключаем другие режимы
                document.getElementById('btn-draw-node')?.classList.remove('active');
                document.getElementById('btn-edit-mode')?.classList.remove('active');
                window.mapManager.disableDraw();
                if (window.mapManager.modifyInteraction) {
                    window.mapManager.map.removeInteraction(window.mapManager.modifyInteraction);
                }
                
                window.mapManager.enableDrawRoute();
                btn.classList.add('active');
            }
        }
    }

    toggleEditMode() {
        if (window.mapManager) {
            const btn = document.getElementById('btn-edit-mode');
            if (btn.classList.contains('active')) {
                // Отключаем режим редактирования
                if (window.mapManager.modifyInteraction) {
                    window.mapManager.map.removeInteraction(window.mapManager.modifyInteraction);
                    window.mapManager.modifyInteraction = null;
                    console.log('Режим редактирования отключен');
                }
                btn.classList.remove('active');
            } else {
                // Отключаем другие режимы
                document.getElementById('btn-draw-node')?.classList.remove('active');
                document.getElementById('btn-draw-route')?.classList.remove('active');
                window.mapManager.disableDraw();
                
                // Удаляем старый Modify interaction, если он есть
                if (window.mapManager.modifyInteraction) {
                    window.mapManager.map.removeInteraction(window.mapManager.modifyInteraction);
                    window.mapManager.modifyInteraction = null;
                }
                
                // Включаем режим редактирования - создаем новый interaction
                // Modify interaction работает с выбранными features из обоих источников
                // Важно: не указываем source, чтобы работало с любыми выбранными features
                const selectedFeatures = window.mapManager.selectInteraction.getFeatures();
                console.log('Создание Modify interaction для', selectedFeatures.getLength(), 'выбранных features');
                
                window.mapManager.modifyInteraction = new ol.interaction.Modify({
                    features: selectedFeatures,
                    // Разрешаем редактирование вершин LineString
                    deleteCondition: (event) => {
                        // Разрешаем удаление вершин при Shift+Click
                        return ol.events.condition.shiftKeyOnly(event) && ol.events.condition.singleClick(event);
                    }
                });
                
                console.log('Modify interaction создан для редактирования узлов и маршрутов');
                
                // Проверяем, что interaction правильно настроен
                selectedFeatures.forEach(feature => {
                    const geomType = feature.getGeometry().getType();
                    console.log('Feature в Modify:', feature.getId(), 'Тип:', geomType);
                });
                
                // Обработчик изменений
                window.mapManager.modifyInteraction.on('modifyend', async (e) => {
                        console.log('Modify interaction: modifyend event', e);
                        
                        // e.features - это Collection, нужно получить массив
                        const features = e.features.getArray ? e.features.getArray() : Array.from(e.features);
                        console.log('Измененные features:', features.length);
                        
                        for (const feature of features) {
                            const featureId = feature.getId();
                            const geometryType = feature.getGeometry().getType();
                            console.log('Обработка измененного feature:', featureId, geometryType);
                            
                            // Определяем тип объекта по геометрии
                            if (geometryType === 'Point') {
                                console.log('Это узел:', featureId);
                                // Редактирование узла
                                const node = window.mapManager.nodesData.get(featureId);
                                if (node) {
                                    const geometry = feature.getGeometry();
                                    const coordinates = ol.proj.toLonLat(geometry.getCoordinates());
                                    node.lon = coordinates[0];
                                    node.lat = coordinates[1];
                                    
                                    // Отправляем обновление на сервер
                                    try {
                                        await api.updateNode(featureId, {
                                            lat: node.lat,
                                            lon: node.lon
                                        });
                                        console.log('Узел обновлен на сервере:', featureId);
                                        if (window.uiManager) {
                                            window.uiManager.showMessage('Изменения сохранены');
                                        }
                                    } catch (error) {
                                        console.error('Ошибка обновления узла:', error);
                                        alert('Ошибка сохранения изменений: ' + error.message);
                                    }
                                }
                            } else if (geometryType === 'LineString') {
                                console.log('Это маршрут:', featureId);
                                // Редактирование маршрута
                                const vols = window.mapManager.volsData.get(featureId);
                                if (vols) {
                                    const geometry = feature.getGeometry();
                                    console.log('Тип геометрии:', geometry.getType());
                                    
                                    // Получаем координаты LineString
                                    const coordinates = geometry.getCoordinates().map(coord => {
                                        return ol.proj.toLonLat(coord);
                                    });
                                    
                                    console.log('Новые координаты маршрута:', coordinates.length, 'точек');
                                    
                                    // Обновляем path маршрута
                                    vols.path = coordinates;
                                    
                                    // Отправляем обновление на сервер
                                    try {
                                        console.log('Отправка обновления маршрута на сервер:', featureId);
                                        await api.updateVols(featureId, {
                                            path: coordinates
                                        });
                                        console.log('Маршрут обновлен на сервере:', featureId);
                                        if (window.uiManager) {
                                            window.uiManager.showMessage('Изменения сохранены');
                                        }
                                    } catch (error) {
                                        console.error('Ошибка обновления маршрута:', error);
                                        alert('Ошибка сохранения изменений: ' + error.message);
                                    }
                                } else {
                                    console.warn('Маршрут не найден в данных:', featureId);
                                }
                            } else {
                                console.warn('Неизвестный тип feature:', featureId);
                            }
                        }
                    });
                
                // Добавляем interaction на карту
                window.mapManager.map.addInteraction(window.mapManager.modifyInteraction);
                btn.classList.add('active');
                
                console.log('Режим редактирования включен');
            }
        }
    }

    setActiveNav(navId) {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.getElementById(navId)?.classList.add('active');
    }

    showPanel(panelName) {
        // Скрываем все панели списков
        document.getElementById('panel-nodes')?.style.setProperty('display', 'none');
        document.getElementById('panel-vols')?.style.setProperty('display', 'none');
        document.getElementById('panel-fibers')?.style.setProperty('display', 'none');
        document.getElementById('panel-links')?.style.setProperty('display', 'none');
        
        // Показываем нужную панель
        this.currentPanel = panelName;
        if (panelName === 'nodes') {
            document.getElementById('panel-nodes')?.style.setProperty('display', 'block');
            document.getElementById('panel-info')?.style.setProperty('display', 'none');
        } else if (panelName === 'vols') {
            document.getElementById('panel-vols')?.style.setProperty('display', 'block');
            document.getElementById('panel-info')?.style.setProperty('display', 'none');
        } else if (panelName === 'fibers') {
            document.getElementById('panel-fibers')?.style.setProperty('display', 'block');
            document.getElementById('panel-info')?.style.setProperty('display', 'none');
            // Загружаем волокна при открытии панели
            this.loadFibers();
        } else if (panelName === 'links') {
            document.getElementById('panel-links')?.style.setProperty('display', 'block');
            document.getElementById('panel-info')?.style.setProperty('display', 'none');
            // Загружаем связи при открытии панели
            this.loadLinks();
        } else {
            // Показываем информационную панель по умолчанию
            document.getElementById('panel-info')?.style.setProperty('display', 'block');
        }
    }

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        if (sidebar) {
            sidebar.classList.toggle('hidden');
        }
    }

    updateStats(stats) {
        if (stats.nodes !== undefined) {
            document.getElementById('stat-nodes').textContent = stats.nodes;
        }
        if (stats.vols !== undefined) {
            document.getElementById('stat-vols').textContent = stats.vols;
        }
        if (stats.fibers !== undefined) {
            document.getElementById('stat-fibers').textContent = stats.fibers;
        }
        if (stats.links !== undefined) {
            document.getElementById('stat-links').textContent = stats.links;
        }
    }

    showNodesList(nodes) {
        const listContainer = document.getElementById('nodes-list');
        if (!listContainer) return;
        
        listContainer.innerHTML = '';
        
        nodes.forEach(node => {
            const item = document.createElement('div');
            item.className = 'list-group-item';
            item.dataset.nodeId = node.id;
            
            const typeLabels = {
                'muft': 'Муфта',
                'cross': 'Кросс',
                'bsp': 'БСП',
                'terminal': 'Терминал'
            };
            
            const statusLabels = {
                'active': 'Активный',
                'inactive': 'Неактивный',
                'maintenance': 'На обслуживании'
            };
            
            item.innerHTML = `
                <div class="item-title">${this.escapeHtml(node.name)}</div>
                <div class="item-meta">
                    <i class="bi bi-tag"></i> ${typeLabels[node.node_type] || node.node_type || 'Не указан'}<br>
                    <i class="bi bi-circle-fill" style="color: ${node.status === 'active' ? '#2ecc71' : node.status === 'maintenance' ? '#f39c12' : '#e74c3c'}; font-size: 0.5rem;"></i> ${statusLabels[node.status] || node.status || 'Не указан'}
                </div>
            `;
            
            item.addEventListener('click', (e) => {
                // Предотвращаем скролл страницы при клике
                e.preventDefault();
                e.stopPropagation();
                this.selectNode(node);
            });
            
            listContainer.appendChild(item);
        });
    }

    showVolsList(volsList) {
        const listContainer = document.getElementById('vols-list');
        if (!listContainer) return;
        
        listContainer.innerHTML = '';
        
        volsList.forEach(vols => {
            const item = document.createElement('div');
            item.className = 'list-group-item';
            item.dataset.volsId = vols.id;
            
            const statusLabels = {
                'active': 'Активный',
                'planning': 'Планируется',
                'under_construction': 'Строится'
            };
            
            item.innerHTML = `
                <div class="item-title">${this.escapeHtml(vols.name)}</div>
                <div class="item-meta">
                    <i class="bi bi-rulers"></i> ${vols.length_km ? `${vols.length_km} км` : 'Длина не указана'}<br>
                    <i class="bi bi-circle-fill" style="color: ${vols.status === 'active' ? '#2ecc71' : vols.status === 'under_construction' ? '#f39c12' : '#95a5a6'}; font-size: 0.5rem;"></i> ${statusLabels[vols.status] || vols.status || 'Не указан'}
                </div>
            `;
            
            item.addEventListener('click', (e) => {
                // Предотвращаем скролл страницы при клике
                e.preventDefault();
                e.stopPropagation();
                this.selectVols(vols);
            });
            
            listContainer.appendChild(item);
        });
    }

    selectNode(node) {
        this.currentNode = node;
        this.showNodeInfo(node);
        
        // Подсвечиваем выбранный элемент
        document.querySelectorAll('#nodes-list .list-group-item').forEach(item => {
            item.classList.remove('active');
            if (parseInt(item.dataset.nodeId) === node.id) {
                item.classList.add('active');
            }
        });
        
        // Подсвечиваем узел на карте БЕЗ автоматического центрирования
        // Это предотвращает нежелательный скролл страницы
        if (window.mapManager && node.lat && node.lon) {
            window.mapManager.highlightNode(node.id, false);
        }
    }

    selectVols(vols) {
        this.currentVols = vols;
        this.showVolsInfo(vols);
        
        // Подсвечиваем выбранный элемент
        document.querySelectorAll('#vols-list .list-group-item').forEach(item => {
            item.classList.remove('active');
            if (parseInt(item.dataset.volsId) === vols.id) {
                item.classList.add('active');
            }
        });
        
        // Подсвечиваем маршрут на карте БЕЗ автоматического центрирования
        // Это предотвращает нежелательный скролл страницы
        if (window.mapManager && vols.id) {
            window.mapManager.highlightRoute(vols.id, false);
        }
    }

    showNodeInfo(node) {
        const infoPanel = document.getElementById('panel-info');
        const infoTitle = document.getElementById('info-title');
        const infoContent = document.getElementById('info-content');
        
        if (!infoPanel || !infoTitle || !infoContent) return;
        
        const typeLabels = {
            'muft': 'Муфта',
            'cross': 'Кросс',
            'bsp': 'БСП',
            'terminal': 'Терминал'
        };
        
        const statusLabels = {
            'active': 'Активный',
            'inactive': 'Неактивный',
            'maintenance': 'На обслуживании'
        };
        
        infoTitle.innerHTML = `<i class="bi bi-geo-alt"></i> ${this.escapeHtml(node.name)}`;
        infoContent.innerHTML = `
            <div class="info-item">
                <div class="info-label">Тип узла</div>
                <div class="info-value">${typeLabels[node.node_type] || node.node_type || 'Не указан'}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Статус</div>
                <div class="info-value">${statusLabels[node.status] || node.status || 'Не указан'}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Координаты</div>
                <div class="info-value">${node.lat?.toFixed(6)}, ${node.lon?.toFixed(6)}</div>
            </div>
            ${node.description ? `
            <div class="info-item">
                <div class="info-label">Описание</div>
                <div class="info-value">${this.escapeHtml(node.description)}</div>
            </div>
            ` : ''}
        `;
        
        this.showPanel('info');
    }

    showVolsInfo(vols) {
        const infoPanel = document.getElementById('panel-info');
        const infoTitle = document.getElementById('info-title');
        const infoContent = document.getElementById('info-content');
        
        if (!infoPanel || !infoTitle || !infoContent) return;
        
        const statusLabels = {
            'active': 'Активный',
            'planning': 'Планируется',
            'under_construction': 'Строится'
        };
        
        infoTitle.innerHTML = `<i class="bi bi-diagram-2"></i> ${this.escapeHtml(vols.name)}`;
        infoContent.innerHTML = `
            <div class="info-item">
                <div class="info-label">Длина</div>
                <div class="info-value">${vols.length_km ? `${vols.length_km} км` : 'Не указана'}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Статус</div>
                <div class="info-value">${statusLabels[vols.status] || vols.status || 'Не указан'}</div>
            </div>
            ${vols.description ? `
            <div class="info-item">
                <div class="info-label">Описание</div>
                <div class="info-value">${this.escapeHtml(vols.description)}</div>
            </div>
            ` : ''}
        `;
        
        this.showPanel('info');
    }

    calculateCenter(path) {
        if (!path || path.length === 0) return [0, 0];
        
        let sumLat = 0, sumLon = 0;
        path.forEach(coord => {
            sumLon += coord[0];
            sumLat += coord[1];
        });
        
        return [sumLon / path.length, sumLat / path.length];
    }

    showMessage(message, type = 'info') {
        console.log(`[${type}] ${message}`);
    }

    showError(message) {
        this.showMessage(message, 'error');
        alert(`Ошибка: ${message}`);
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Загрузка и отображение волокон
    async loadFibers() {
        try {
            console.log('Загрузка волокон...');
            const response = await api.getFibers();
            console.log('Ответ API для волокон:', response);
            const fibers = response.fibers || [];
            console.log(`Найдено волокон: ${fibers.length}`);
            this.showFibersList(fibers);
        } catch (error) {
            console.error('Ошибка загрузки волокон:', error);
            this.showError('Ошибка загрузки волокон: ' + error.message);
        }
    }

    showFibersList(fibers) {
        const listContainer = document.getElementById('fibers-list');
        if (!listContainer) return;
        
        listContainer.innerHTML = '';
        
        if (fibers.length === 0) {
            listContainer.innerHTML = '<div class="list-group-item text-muted">Волокна не найдены</div>';
            return;
        }
        
        fibers.forEach(fiber => {
            const item = document.createElement('div');
            item.className = 'list-group-item';
            item.dataset.fiberId = fiber.id;
            
            const statusLabels = {
                'active': 'Активное',
                'spare': 'Резервное',
                'damaged': 'Поврежденное'
            };
            
            item.innerHTML = `
                <div class="item-title">${this.escapeHtml(fiber.name)}</div>
                <div class="item-meta">
                    <i class="bi bi-cable"></i> ${fiber.cable_type || 'Тип не указан'}<br>
                    <i class="bi bi-hash"></i> ${fiber.fiber_count || 0} волокон<br>
                    <i class="bi bi-circle-fill" style="color: ${fiber.status === 'active' ? '#2ecc71' : fiber.status === 'spare' ? '#f39c12' : '#e74c3c'}; font-size: 0.5rem;"></i> ${statusLabels[fiber.status] || fiber.status || 'Не указан'}
                </div>
            `;
            
            item.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.selectFiber(fiber);
            });
            
            listContainer.appendChild(item);
        });
    }

    selectFiber(fiber) {
        this.currentFiber = fiber;
        this.showFiberInfo(fiber);
        
        // Подсвечиваем выбранный элемент
        document.querySelectorAll('#fibers-list .list-group-item').forEach(item => {
            item.classList.remove('active');
            if (parseInt(item.dataset.fiberId) === fiber.id) {
                item.classList.add('active');
            }
        });
    }

    showFiberInfo(fiber) {
        const infoPanel = document.getElementById('panel-info');
        const infoTitle = document.getElementById('info-title');
        const infoContent = document.getElementById('info-content');
        
        if (!infoPanel || !infoTitle || !infoContent) return;
        
        const statusLabels = {
            'active': 'Активное',
            'spare': 'Резервное',
            'damaged': 'Поврежденное'
        };
        
        infoTitle.innerHTML = `<i class="bi bi-lightning"></i> ${this.escapeHtml(fiber.name)}`;
        infoContent.innerHTML = `
            <div class="info-item">
                <div class="info-label">Тип кабеля</div>
                <div class="info-value">${fiber.cable_type || 'Не указан'}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Количество волокон</div>
                <div class="info-value">${fiber.fiber_count || 0}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Статус</div>
                <div class="info-value">${statusLabels[fiber.status] || fiber.status || 'Не указан'}</div>
            </div>
            ${fiber.vols_id ? `
            <div class="info-item">
                <div class="info-label">Маршрут ВОЛС</div>
                <div class="info-value">ID: ${fiber.vols_id}</div>
            </div>
            ` : ''}
        `;
        
        this.showPanel('info');
    }

    // Загрузка и отображение связей
    async loadLinks() {
        try {
            console.log('Загрузка связей...');
            const response = await api.getLinks();
            console.log('Ответ API для связей:', response);
            const links = response.links || [];
            console.log(`Найдено связей: ${links.length}`);
            this.showLinksList(links);
        } catch (error) {
            console.error('Ошибка загрузки связей:', error);
            this.showError('Ошибка загрузки связей: ' + error.message);
        }
    }

    showLinksList(links) {
        const listContainer = document.getElementById('links-list');
        if (!listContainer) return;
        
        listContainer.innerHTML = '';
        
        if (links.length === 0) {
            listContainer.innerHTML = '<div class="list-group-item text-muted">Связи не найдены</div>';
            return;
        }
        
        links.forEach(link => {
            const item = document.createElement('div');
            item.className = 'list-group-item';
            item.dataset.linkId = link.id;
            
            const statusLabels = {
                'active': 'Активная',
                'spare': 'Резервная',
                'unused': 'Неиспользуемая'
            };
            
            item.innerHTML = `
                <div class="item-title">Связь #${link.id}</div>
                <div class="item-meta">
                    <i class="bi bi-arrow-left-right"></i> Узел ${link.start_node_id} → Узел ${link.end_node_id}<br>
                    ${link.capacity_gbps ? `<i class="bi bi-speedometer2"></i> ${link.capacity_gbps} Гбит/с<br>` : ''}
                    <i class="bi bi-circle-fill" style="color: ${link.status === 'active' ? '#2ecc71' : link.status === 'spare' ? '#f39c12' : '#95a5a6'}; font-size: 0.5rem;"></i> ${statusLabels[link.status] || link.status || 'Не указан'}
                </div>
            `;
            
            item.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.selectLink(link);
            });
            
            listContainer.appendChild(item);
        });
    }

    selectLink(link) {
        this.currentLink = link;
        this.showLinkInfo(link);
        
        // Подсвечиваем выбранный элемент
        document.querySelectorAll('#links-list .list-group-item').forEach(item => {
            item.classList.remove('active');
            if (parseInt(item.dataset.linkId) === link.id) {
                item.classList.add('active');
            }
        });
    }

    showLinkInfo(link) {
        const infoPanel = document.getElementById('panel-info');
        const infoTitle = document.getElementById('info-title');
        const infoContent = document.getElementById('info-content');
        
        if (!infoPanel || !infoTitle || !infoContent) return;
        
        const statusLabels = {
            'active': 'Активная',
            'spare': 'Резервная',
            'unused': 'Неиспользуемая'
        };
        
        infoTitle.innerHTML = `<i class="bi bi-link-45deg"></i> Связь #${link.id}`;
        infoContent.innerHTML = `
            <div class="info-item">
                <div class="info-label">Волокно</div>
                <div class="info-value">ID: ${link.fiber_id || 'Не указано'}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Начальный узел</div>
                <div class="info-value">ID: ${link.start_node_id || 'Не указан'}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Конечный узел</div>
                <div class="info-value">ID: ${link.end_node_id || 'Не указан'}</div>
            </div>
            ${link.start_port ? `
            <div class="info-item">
                <div class="info-label">Порт начала</div>
                <div class="info-value">${link.start_port}</div>
            </div>
            ` : ''}
            ${link.end_port ? `
            <div class="info-item">
                <div class="info-label">Порт конца</div>
                <div class="info-value">${link.end_port}</div>
            </div>
            ` : ''}
            <div class="info-item">
                <div class="info-label">Статус</div>
                <div class="info-value">${statusLabels[link.status] || link.status || 'Не указан'}</div>
            </div>
            ${link.capacity_gbps ? `
            <div class="info-item">
                <div class="info-label">Емкость</div>
                <div class="info-value">${link.capacity_gbps} Гбит/с</div>
            </div>
            ` : ''}
        `;
        
        this.showPanel('info');
    }

    // Модальные окна для волокон и связей
    openFiberModal(fiber = null) {
        const modal = new bootstrap.Modal(document.getElementById('fiberModal'));
        const title = document.getElementById('fiberModalTitle');
        const form = document.getElementById('fiberForm');
        
        if (fiber) {
            title.textContent = 'Редактировать волокно';
            document.getElementById('fiberId').value = fiber.id;
            document.getElementById('fiberName').value = fiber.name || '';
            document.getElementById('fiberCableType').value = fiber.cable_type || '';
            document.getElementById('fiberCount').value = fiber.fiber_count || 1;
            document.getElementById('fiberVolsId').value = fiber.vols_id || '';
            document.getElementById('fiberStatus').value = fiber.status || 'active';
        } else {
            title.textContent = 'Новое волокно';
            form.reset();
            document.getElementById('fiberId').value = '';
        }
        
        modal.show();
    }

    async saveFiber() {
        try {
            const fiberId = document.getElementById('fiberId').value;
            const fiberData = {
                name: document.getElementById('fiberName').value.trim(),
                cable_type: document.getElementById('fiberCableType').value.trim() || null,
                fiber_count: parseInt(document.getElementById('fiberCount').value) || 1,
                vols_id: document.getElementById('fiberVolsId').value ? parseInt(document.getElementById('fiberVolsId').value) : null,
                status: document.getElementById('fiberStatus').value
            };
            
            if (!fiberData.name) {
                alert('Введите название волокна');
                return;
            }
            
            let response;
            if (fiberId) {
                response = await api.updateFiber(parseInt(fiberId), fiberData);
            } else {
                response = await api.createFiber(fiberData);
            }
            
            const bootstrapModal = bootstrap.Modal.getInstance(document.getElementById('fiberModal'));
            bootstrapModal.hide();
            
            this.showMessage('Волокно сохранено успешно');
            
            // Обновляем общие данные (включая статистику)
            if (window.loadRoutes) {
                await window.loadRoutes();
            }
            
            // Перезагружаем список волокон
            await this.loadFibers();
        } catch (error) {
            console.error('Ошибка сохранения волокна:', error);
            alert('Ошибка сохранения: ' + error.message);
        }
    }

    openLinkModal(link = null) {
        const modal = new bootstrap.Modal(document.getElementById('linkModal'));
        const title = document.getElementById('linkModalTitle');
        const form = document.getElementById('linkForm');
        
        if (link) {
            title.textContent = 'Редактировать связь';
            document.getElementById('linkId').value = link.id;
            document.getElementById('linkFiberId').value = link.fiber_id || '';
            document.getElementById('linkStartNodeId').value = link.start_node_id || '';
            document.getElementById('linkEndNodeId').value = link.end_node_id || '';
            document.getElementById('linkStartPort').value = link.start_port || '';
            document.getElementById('linkEndPort').value = link.end_port || '';
            document.getElementById('linkCapacity').value = link.capacity_gbps || '';
            document.getElementById('linkStatus').value = link.status || 'active';
        } else {
            title.textContent = 'Новая связь';
            form.reset();
            document.getElementById('linkId').value = '';
        }
        
        modal.show();
    }

    async saveLink() {
        try {
            const linkId = document.getElementById('linkId').value;
            const linkData = {
                fiber_id: parseInt(document.getElementById('linkFiberId').value),
                start_node_id: parseInt(document.getElementById('linkStartNodeId').value),
                end_node_id: parseInt(document.getElementById('linkEndNodeId').value),
                start_port: document.getElementById('linkStartPort').value ? parseInt(document.getElementById('linkStartPort').value) : null,
                end_port: document.getElementById('linkEndPort').value ? parseInt(document.getElementById('linkEndPort').value) : null,
                capacity_gbps: document.getElementById('linkCapacity').value ? parseFloat(document.getElementById('linkCapacity').value) : null,
                status: document.getElementById('linkStatus').value
            };
            
            if (!linkData.fiber_id || !linkData.start_node_id || !linkData.end_node_id) {
                alert('Заполните обязательные поля: волокно, начальный и конечный узлы');
                return;
            }
            
            let response;
            if (linkId) {
                response = await api.updateLink(parseInt(linkId), linkData);
            } else {
                response = await api.createLink(linkData);
            }
            
            const bootstrapModal = bootstrap.Modal.getInstance(document.getElementById('linkModal'));
            bootstrapModal.hide();
            
            this.showMessage('Связь сохранена успешно');
            
            // Обновляем общие данные (включая статистику)
            if (window.loadRoutes) {
                await window.loadRoutes();
            }
            
            // Перезагружаем список связей
            await this.loadLinks();
        } catch (error) {
            console.error('Ошибка сохранения связи:', error);
            alert('Ошибка сохранения: ' + error.message);
        }
    }
}
