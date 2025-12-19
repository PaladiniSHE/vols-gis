/** Управление картой OpenLayers */
class MapManager {
    constructor(containerId) {
        this.containerId = containerId;
        this.map = null;
        this.initialized = false;
        
        // Слои
        this.baseLayer = null;
        this.nodesLayer = null;
        this.routesLayer = null;
        
        // Источники данных
        this.nodesSource = null;
        this.routesSource = null;
        
        // Features (объекты на карте)
        this.nodeFeatures = new Map(); // Map<nodeId, Feature>
        this.routeFeatures = new Map(); // Map<volsId, Feature>
        
        // Interactions
        this.selectInteraction = null;
        this.modifyInteraction = null;
        this.drawInteraction = null;
        this.snapInteraction = null;
        this.snapRoutesInteraction = null;
        
        // Overlay для попапов
        this.popupOverlay = null;
        this.popupElement = null;
        
        // Данные
        this.nodesData = new Map(); // Map<nodeId, nodeData>
        this.volsData = new Map(); // Map<volsId, volsData>
    }

    init() {
        if (this.initialized) {
            console.log('MapManager уже инициализирован');
            return;
        }

        // Создаем попап элемент
        this.createPopupElement();

        // Создаем источники данных
        this.nodesSource = new ol.source.Vector({
            features: []
        });

        this.routesSource = new ol.source.Vector({
            features: []
        });

        // Создаем слои
        this.baseLayer = new ol.layer.Tile({
            source: new ol.source.OSM()
        });

        this.nodesLayer = new ol.layer.Vector({
            source: this.nodesSource,
            style: (feature) => this.getNodeStyle(feature)
        });

        this.routesLayer = new ol.layer.Vector({
            source: this.routesSource,
            style: (feature) => this.getRouteStyle(feature)
        });

        // Создаем overlay для попапа
        this.popupOverlay = new ol.Overlay({
            element: this.popupElement,
            positioning: 'bottom-center',
            stopEvent: false,
            offset: [0, -10]
        });

        // Создаем карту
        this.map = new ol.Map({
            target: this.containerId,
            layers: [
                this.baseLayer,
                this.routesLayer,
                this.nodesLayer
            ],
            view: new ol.View({
                center: ol.proj.fromLonLat([37.6173, 55.7558]), // Москва [lon, lat] -> EPSG:3857
                zoom: 10,
                projection: 'EPSG:3857'
            }),
            overlays: [this.popupOverlay]
        });

        // Добавляем interactions
        this.addInteractions();

        // Обработчик изменения размера
        window.addEventListener('resize', () => {
            if (this.map) {
                this.map.updateSize();
            }
        });

        this.initialized = true;
        console.log('MapManager (OpenLayers) инициализирован');
        
        // Сохраняем ссылку для доступа из других модулей
        window.mapManager = this;
    }

    createPopupElement() {
        this.popupElement = document.createElement('div');
        this.popupElement.className = 'ol-popup';
        this.popupElement.id = 'ol-popup';
        this.popupElement.innerHTML = '<div id="popup-content"></div><button id="popup-closer" class="ol-popup-closer"></button>';
        document.body.appendChild(this.popupElement);

        // Обработчик закрытия попапа
        const closer = document.getElementById('popup-closer');
        closer.onclick = () => {
            this.popupOverlay.setPosition(undefined);
            closer.blur();
            return false;
        };
    }

    addInteractions() {
        // Select Interaction - выбор объектов
        this.selectInteraction = new ol.interaction.Select({
            layers: [this.nodesLayer, this.routesLayer],
            style: (feature) => this.getSelectedStyle(feature)
        });

        this.selectInteraction.on('select', (e) => {
            if (e.selected.length > 0) {
                const feature = e.selected[0];
                const featureId = feature.getId();
                const geometryType = feature.getGeometry().getType();
                
                console.log('Выбран объект:', featureId, 'Тип геометрии:', geometryType);
                
                // Определяем тип объекта по геометрии, а не по Map
                // LineString = маршрут, Point = узел
                if (geometryType === 'LineString') {
                    // Это маршрут
                    console.log('Выбран маршрут');
                    const vols = this.volsData.get(featureId);
                    if (vols && window.uiManager) {
                        window.uiManager.selectVols(vols);
                    }
                    this.showPopup(feature, this.createRoutePopup(vols));
                } else if (geometryType === 'Point') {
                    // Это узел
                    console.log('Выбран узел');
                    const node = this.nodesData.get(featureId);
                    if (node && window.uiManager) {
                        window.uiManager.selectNode(node);
                    }
                    this.showPopup(feature, this.createNodePopup(node));
                } else {
                    console.warn('Выбран неизвестный тип объекта:', featureId, geometryType);
                }
            } else {
                // Скрываем попап при снятии выбора
                this.popupOverlay.setPosition(undefined);
            }
        });

        this.map.addInteraction(this.selectInteraction);

        // Modify Interaction будет добавлен по требованию через UI
        // Не добавляем его сразу, чтобы не мешать обычной навигации

        // Snap Interaction - прилипание к узлам при рисовании и редактировании
        this.snapInteraction = new ol.interaction.Snap({
            source: this.nodesSource,
            pixelTolerance: 10
        });

        this.map.addInteraction(this.snapInteraction);
        
        // Snap для маршрутов - прилипание к узлам при редактировании маршрутов
        this.snapRoutesInteraction = new ol.interaction.Snap({
            source: this.routesSource,
            pixelTolerance: 10
        });
        
        this.map.addInteraction(this.snapRoutesInteraction);
    }

    // Стили для узлов
    getNodeStyle(feature) {
        const nodeId = feature.getId();
        const node = this.nodesData.get(nodeId);
        
        if (!node) {
            return new ol.style.Style({
                image: new ol.style.Circle({
                    radius: 8,
                    fill: new ol.style.Fill({ color: '#3498db' }),
                    stroke: new ol.style.Stroke({ color: '#fff', width: 2 })
                })
            });
        }

        // Цвет по статусу
        let color = '#3498db'; // Синий по умолчанию
        if (node.status === 'active') {
            color = '#2ecc71'; // Зеленый
        } else if (node.status === 'maintenance') {
            color = '#f39c12'; // Оранжевый
        } else if (node.status === 'inactive') {
            color = '#e74c3c'; // Красный
        }

        return new ol.style.Style({
            image: new ol.style.Circle({
                radius: 10,
                fill: new ol.style.Fill({ color: color }),
                stroke: new ol.style.Stroke({ 
                    color: '#fff', 
                    width: 3 
                })
            }),
            text: new ol.style.Text({
                text: node.name || '',
                offsetY: -20,
                fill: new ol.style.Fill({ color: '#000' }),
                stroke: new ol.style.Stroke({ color: '#fff', width: 3 }),
                font: '12px sans-serif'
            })
        });
    }

    // Стили для маршрутов
    getRouteStyle(feature) {
        const volsId = feature.getId();
        const vols = this.volsData.get(volsId);
        
        if (!vols) {
            return new ol.style.Style({
                stroke: new ol.style.Stroke({
                    color: '#3498db',
                    width: 4,
                    lineCap: 'round',
                    lineJoin: 'round'
                })
            });
        }

        // Цвет по статусу
        let color = '#3498db';
        let width = 4;
        
        if (vols.status === 'active') {
            color = '#2ecc71';
            width = 5;
        } else if (vols.status === 'under_construction') {
            color = '#f39c12';
            width = 4;
        } else if (vols.status === 'planning') {
            color = '#95a5a6';
            width = 3;
        }

        // Толщина может зависеть от емкости/длины
        if (vols.length_km) {
            width = Math.max(3, Math.min(6, 3 + vols.length_km / 20));
        }

        return new ol.style.Style({
            stroke: new ol.style.Stroke({
                color: color,
                width: width,
                lineCap: 'round',
                lineJoin: 'round'
            })
        });
    }

    // Стиль для выбранных объектов
    getSelectedStyle(feature) {
        const geometryType = feature.getGeometry().getType();
        
        if (geometryType === 'Point') {
            // Узел - просто выделяем красным
            return new ol.style.Style({
                image: new ol.style.Circle({
                    radius: 14,
                    fill: new ol.style.Fill({ color: '#e74c3c' }),
                    stroke: new ol.style.Stroke({ 
                        color: '#fff', 
                        width: 4 
                    })
                })
            });
        } else if (geometryType === 'LineString') {
            // Маршрут - используем массив стилей: основной + выделение
            const featureId = feature.getId();
            const vols = this.volsData.get(featureId);
            
            // Получаем основной стиль маршрута
            const baseStyle = this.getRouteStyle(feature);
            
            // Стиль выделения (красная обводка поверх)
            const highlightStyle = new ol.style.Style({
                stroke: new ol.style.Stroke({
                    color: '#e74c3c',
                    width: (vols && vols.status === 'active' ? 7 : 6), // Немного толще основного
                    lineCap: 'round',
                    lineJoin: 'round'
                }),
                zIndex: 1 // Поверх основного стиля
            });
            
            // Возвращаем массив стилей: сначала основной, затем выделение
            return [baseStyle, highlightStyle];
        } else {
            // Неизвестный тип - возвращаем базовый стиль
            return new ol.style.Style({
                stroke: new ol.style.Stroke({
                    color: '#e74c3c',
                    width: 6,
                    lineCap: 'round',
                    lineJoin: 'round'
                })
            });
        }
    }

    // Добавление узла на карту
    addMarker(lat, lon, title, node = null) {
        if (!node || !node.id) {
            console.warn('Узел должен иметь ID');
            return null;
        }

        // OpenLayers использует [lon, lat] и EPSG:3857
        const coordinates = ol.proj.fromLonLat([lon, lat]);

        // Создаем Point feature
        const feature = new ol.Feature({
            geometry: new ol.geom.Point(coordinates)
        });

        feature.setId(node.id);
        
        // Сохраняем данные узла
        this.nodesData.set(node.id, node);
        this.nodeFeatures.set(node.id, feature);
        
        // Добавляем в источник
        this.nodesSource.addFeature(feature);

        return feature;
    }

    // Добавление маршрута на карту
    addRoute(path, name, vols = null) {
        if (!path || path.length < 2) {
            console.warn('Некорректный путь для маршрута');
            return null;
        }

        if (!vols || !vols.id) {
            console.warn('Маршрут должен иметь ID');
            return null;
        }

        // API возвращает path как массив [lon, lat] координат
        // OpenLayers использует [lon, lat] и требует EPSG:3857
        const coordinates = path.map(coord => {
            if (Array.isArray(coord) && coord.length >= 2) {
                // coord уже в формате [lon, lat] от API
                return ol.proj.fromLonLat([coord[0], coord[1]]);
            }
            return null;
        }).filter(c => c !== null);

        if (coordinates.length < 2) {
            console.warn('Не удалось преобразовать координаты маршрута', path);
            return null;
        }

        // Создаем LineString feature
        const feature = new ol.Feature({
            geometry: new ol.geom.LineString(coordinates)
        });

        feature.setId(vols.id);
        
        // Сохраняем данные маршрута
        this.volsData.set(vols.id, vols);
        this.routeFeatures.set(vols.id, feature);
        
        // Добавляем в источник
        this.routesSource.addFeature(feature);

        return feature;
    }

    // Создание попапа для узла
    createNodePopup(node) {
        if (!node) return '';

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

        return `
            <h4>${this.escapeHtml(node.name || 'Без названия')}</h4>
            <div class="popup-info">
                <strong>Тип:</strong> ${typeLabels[node.node_type] || node.node_type || 'Не указан'}<br>
                <strong>Статус:</strong> ${statusLabels[node.status] || node.status || 'Не указан'}<br>
                ${node.lat && node.lon ? `<strong>Координаты:</strong> ${node.lat.toFixed(6)}, ${node.lon.toFixed(6)}` : ''}
            </div>
        `;
    }

    // Создание попапа для маршрута
    createRoutePopup(vols) {
        if (!vols) return '';

        const statusLabels = {
            'active': 'Активный',
            'planning': 'Планируется',
            'under_construction': 'Строится'
        };

        return `
            <h4>${this.escapeHtml(vols.name || 'Без названия')}</h4>
            <div class="popup-info">
                ${vols.length_km ? `<strong>Длина:</strong> ${vols.length_km} км<br>` : ''}
                <strong>Статус:</strong> ${statusLabels[vols.status] || vols.status || 'Не указан'}
            </div>
        `;
    }

    // Показать попап
    showPopup(feature, content) {
        const geometry = feature.getGeometry();
        const coordinate = geometry.getType() === 'Point' 
            ? geometry.getCoordinates()
            : geometry.getClosestPoint(this.map.getView().getCenter());

        const contentElement = document.getElementById('popup-content');
        if (contentElement) {
            contentElement.innerHTML = content;
        }

        this.popupOverlay.setPosition(coordinate);
    }

    // Очистка маркеров
    clearMarkers() {
        this.nodesSource.clear();
        this.nodeFeatures.clear();
        this.nodesData.clear();
    }

    // Очистка маршрутов
    clearRoutes() {
        this.routesSource.clear();
        this.routeFeatures.clear();
        this.volsData.clear();
    }

    // Подогнать карту под все объекты
    fitBounds() {
        const extent = ol.extent.createEmpty();
        
        // Добавляем extent узлов
        this.nodesSource.forEachFeature(feature => {
            ol.extent.extend(extent, feature.getGeometry().getExtent());
        });
        
        // Добавляем extent маршрутов
        this.routesSource.forEachFeature(feature => {
            ol.extent.extend(extent, feature.getGeometry().getExtent());
        });

        if (!ol.extent.isEmpty(extent)) {
            this.map.getView().fit(extent, {
                padding: [50, 50, 50, 50],
                duration: 500
            });
        }
    }

    // Обновить размер карты
    updateSize() {
        if (this.map) {
            this.map.updateSize();
        }
    }

    // Подсветка узла
    highlightNode(nodeId, centerMap = false) {
        const feature = this.nodeFeatures.get(nodeId);
        if (feature) {
            this.selectInteraction.getFeatures().clear();
            this.selectInteraction.getFeatures().push(feature);
            
            // Центрируем карту на узле только если явно запрошено
            if (centerMap) {
                const geometry = feature.getGeometry();
                const currentCenter = this.map.getView().getCenter();
                const nodeCoord = geometry.getCoordinates();
                
                // Проверяем, виден ли узел в текущем viewport
                const extent = this.map.getView().calculateExtent(this.map.getSize());
                const nodeVisible = ol.extent.containsCoordinate(extent, nodeCoord);
                
                // Центрируем только если узел не виден или если он далеко от центра
                if (!nodeVisible) {
                    this.map.getView().animate({
                        center: nodeCoord,
                        zoom: Math.max(this.map.getView().getZoom(), 13),
                        duration: 500
                    });
                }
            }
            
            // Показываем попап без центрирования карты
            const node = this.nodesData.get(nodeId);
            if (node) {
                this.showPopup(feature, this.createNodePopup(node));
            }
        }
    }

    // Подсветка маршрута
    highlightRoute(volsId, centerMap = false) {
        const feature = this.routeFeatures.get(volsId);
        if (feature) {
            this.selectInteraction.getFeatures().clear();
            this.selectInteraction.getFeatures().push(feature);
            
            // Центрируем карту на маршруте только если явно запрошено
            if (centerMap) {
                const geometry = feature.getGeometry();
                const extent = geometry.getExtent();
                const currentExtent = this.map.getView().calculateExtent(this.map.getSize());
                
                // Проверяем, виден ли маршрут в текущем viewport
                const routeVisible = ol.extent.containsExtent(currentExtent, extent) || 
                                    ol.extent.intersects(currentExtent, extent);
                
                // Центрируем только если маршрут не виден
                if (!routeVisible) {
                    this.map.getView().fit(extent, {
                        padding: [50, 50, 50, 50],
                        duration: 500
                    });
                }
            }
            
            // Показываем попап без центрирования карты
            const vols = this.volsData.get(volsId);
            if (vols) {
                this.showPopup(feature, this.createRoutePopup(vols));
            }
        }
    }

    // Включить режим рисования узлов
    enableDrawNode() {
        this.disableDraw();
        
        this.drawInteraction = new ol.interaction.Draw({
            source: this.nodesSource,
            type: 'Point'
        });

        this.drawInteraction.on('drawend', (e) => {
            const feature = e.feature;
            const coordinate = feature.getGeometry().getCoordinates();
            const lonLat = ol.proj.toLonLat(coordinate);
            
            // Проверяем, не слишком ли близко к существующему узлу
            const minDistance = 0.001; // примерно 100 метров
            let tooClose = false;
            
            this.nodesSource.forEachFeature(existingFeature => {
                if (existingFeature !== feature && existingFeature.getId()) {
                    const existingCoord = existingFeature.getGeometry().getCoordinates();
                    const existingLonLat = ol.proj.toLonLat(existingCoord);
                    const distance = Math.sqrt(
                        Math.pow(lonLat[0] - existingLonLat[0], 2) + 
                        Math.pow(lonLat[1] - existingLonLat[1], 2)
                    );
                    if (distance < minDistance) {
                        tooClose = true;
                    }
                }
            });
            
            if (tooClose) {
                this.nodesSource.removeFeature(feature);
                alert('Узел слишком близко к существующему. Выберите другое место.');
                return;
            }
            
            // Открываем модальное окно для создания узла
            this.openNodeModal(lonLat[1], lonLat[0], feature);
        });

        this.map.addInteraction(this.drawInteraction);
    }

    // Включить режим рисования маршрутов
    enableDrawRoute() {
        this.disableDraw();
        
        this.drawInteraction = new ol.interaction.Draw({
            source: this.routesSource,
            type: 'LineString',
            snapTolerance: 10
        });

        this.drawInteraction.on('drawend', (e) => {
            const feature = e.feature;
            const geometry = feature.getGeometry();
            // Преобразуем координаты из EPSG:3857 в [lon, lat]
            const coordinates = geometry.getCoordinates().map(coord => {
                return ol.proj.toLonLat(coord);
            });
            
            // Проверяем минимальное количество точек
            if (coordinates.length < 2) {
                this.routesSource.removeFeature(feature);
                alert('Маршрут должен содержать минимум 2 точки');
                return;
            }
            
            // Открываем модальное окно для создания маршрута
            this.openRouteModal(coordinates, feature);
        });

        this.map.addInteraction(this.drawInteraction);
    }
    
    // Открыть модальное окно для создания узла
    openNodeModal(lat, lon, feature) {
        // Заполняем форму координатами
        document.getElementById('nodeLat').value = lat.toFixed(6);
        document.getElementById('nodeLon').value = lon.toFixed(6);
        document.getElementById('nodeId').value = '';
        document.getElementById('nodeModalTitle').textContent = 'Новый узел';
        
        // Сохраняем feature для последующего добавления ID
        feature.set('pending', true);
        
        // Показываем модальное окно
        const modal = new bootstrap.Modal(document.getElementById('nodeModal'));
        modal.show();
        
        // Обработчик сохранения
        const saveBtn = document.getElementById('btn-save-node');
        const originalHandler = saveBtn.onclick;
        saveBtn.onclick = async () => {
            await this.saveNode(feature, modal);
        };
    }
    
    // Открыть модальное окно для создания маршрута
    openRouteModal(coordinates, feature) {
        // Запрашиваем название маршрута
        const routeName = prompt('Введите название маршрута:');
        if (!routeName || routeName.trim() === '') {
            // Пользователь отменил или ввел пустое название - удаляем feature
            this.routesSource.removeFeature(feature);
            return;
        }
        
        // Сохраняем feature для последующего добавления ID
        feature.set('pending', true);
        
        // Создаем маршрут на сервере
        this.saveRoute(feature, routeName.trim(), coordinates);
    }
    
    // Сохранить маршрут
    async saveRoute(feature, name, coordinates) {
        try {
            if (!name || name.trim() === '') {
                this.routesSource.removeFeature(feature);
                return;
            }
            
            // Проверяем формат координат - должны быть [lon, lat]
            if (!Array.isArray(coordinates) || coordinates.length < 2) {
                console.error('Некорректный формат координат:', coordinates);
                alert('Ошибка: некорректный формат координат маршрута');
                this.routesSource.removeFeature(feature);
                return;
            }
            
            // Убеждаемся, что координаты в правильном формате [[lon, lat], [lon, lat], ...]
            const validCoordinates = coordinates.map(coord => {
                if (Array.isArray(coord) && coord.length >= 2) {
                    return [parseFloat(coord[0]), parseFloat(coord[1])];
                }
                return null;
            }).filter(coord => coord !== null);
            
            if (validCoordinates.length < 2) {
                console.error('Недостаточно валидных координат:', validCoordinates);
                alert('Ошибка: маршрут должен содержать минимум 2 точки');
                this.routesSource.removeFeature(feature);
                return;
            }
            
            const routeData = {
                name: name.trim(),
                path: validCoordinates, // [[lon, lat], [lon, lat], ...] формат
                status: 'active'
            };
            
            console.log('Отправка данных маршрута:', routeData);
            
            const response = await api.createVols(routeData);
            
            console.log('Ответ от сервера:', response);
            
            // Проверяем формат ответа
            let vols = null;
            if (Array.isArray(response)) {
                vols = response[0]?.vols || response[0];
            } else {
                vols = response.vols || response;
            }
            
            // Проверяем наличие ошибки в ответе
            if (response.error) {
                throw new Error(response.error);
            }
            
            if (vols && vols.id) {
                // Устанавливаем ID для feature
                feature.setId(vols.id);
                feature.unset('pending');
                
                // Сохраняем данные маршрута
                this.volsData.set(vols.id, vols);
                this.routeFeatures.set(vols.id, feature);
                
                console.log('Маршрут успешно создан с ID:', vols.id);
                
                // Обновляем UI
                if (window.uiManager) {
                    window.uiManager.showMessage('Маршрут создан успешно');
                    // Обновляем статистику
                    if (window.loadRoutes) {
                        window.loadRoutes();
                    }
                }
            } else {
                console.error('Не удалось получить ID из ответа:', response);
                throw new Error('Не удалось получить ID созданного маршрута. Ответ: ' + JSON.stringify(response));
            }
        } catch (error) {
            console.error('Ошибка сохранения маршрута:', error);
            const errorMessage = error.message || error.toString() || 'Неизвестная ошибка';
            alert('Ошибка сохранения маршрута: ' + errorMessage);
            // Удаляем feature при ошибке
            this.routesSource.removeFeature(feature);
        }
    }
    
    // Сохранить узел
    async saveNode(feature, modal) {
        try {
            const nodeName = document.getElementById('nodeName').value.trim();
            if (!nodeName) {
                alert('Введите название узла');
                return;
            }
            
            const nodeData = {
                name: nodeName,
                node_type: document.getElementById('nodeType').value,
                status: document.getElementById('nodeStatus').value,
                lat: parseFloat(document.getElementById('nodeLat').value),
                lon: parseFloat(document.getElementById('nodeLon').value)
            };
            
            // Валидация координат
            if (isNaN(nodeData.lat) || isNaN(nodeData.lon)) {
                alert('Некорректные координаты');
                return;
            }
            
            if (nodeData.lat < -90 || nodeData.lat > 90 || nodeData.lon < -180 || nodeData.lon > 180) {
                alert('Координаты вне допустимого диапазона');
                return;
            }
            
            const response = await api.createNode(nodeData);
            
            // Проверяем формат ответа (может быть объект или массив)
            let node = null;
            if (Array.isArray(response)) {
                node = response[0]?.node || response[0];
            } else {
                node = response.node || response;
            }
            
            if (node && node.id) {
                // Устанавливаем ID для feature
                feature.setId(node.id);
                feature.unset('pending');
                
                // Обновляем координаты feature на случай, если они изменились
                const coordinates = ol.proj.fromLonLat([node.lon || nodeData.lon, node.lat || nodeData.lat]);
                feature.getGeometry().setCoordinates(coordinates);
                
                // Сохраняем данные узла
                this.nodesData.set(node.id, node);
                this.nodeFeatures.set(node.id, feature);
                
                // Обновляем UI
                if (window.uiManager) {
                    window.uiManager.showMessage('Узел создан успешно');
                    // Обновляем статистику и списки
                    if (window.loadRoutes) {
                        window.loadRoutes();
                    }
                }
            } else {
                throw new Error('Не удалось получить ID созданного узла');
            }
            
            const bootstrapModal = bootstrap.Modal.getInstance(document.getElementById('nodeModal'));
            if (bootstrapModal) {
                bootstrapModal.hide();
            } else {
                modal.hide();
            }
        } catch (error) {
            console.error('Ошибка сохранения узла:', error);
            alert('Ошибка сохранения узла: ' + (error.message || 'Неизвестная ошибка'));
            // Удаляем feature при ошибке
            this.nodesSource.removeFeature(feature);
        }
    }

    // Отключить режим рисования
    disableDraw() {
        if (this.drawInteraction) {
            this.map.removeInteraction(this.drawInteraction);
            
            // Удаляем незавершенные features
            const pendingFeatures = [];
            this.nodesSource.forEachFeature(feature => {
                if (feature.get('pending')) {
                    pendingFeatures.push(feature);
                }
            });
            this.routesSource.forEachFeature(feature => {
                if (feature.get('pending')) {
                    pendingFeatures.push(feature);
                }
            });
            
            pendingFeatures.forEach(feature => {
                if (feature.getSource() === this.nodesSource) {
                    this.nodesSource.removeFeature(feature);
                } else if (feature.getSource() === this.routesSource) {
                    this.routesSource.removeFeature(feature);
                }
            });
            
            this.drawInteraction = null;
        }
    }

    // Вспомогательная функция для экранирования HTML
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
