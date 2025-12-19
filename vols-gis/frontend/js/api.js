/** API клиент для backend */
const API_BASE = '/api';

class APIClient {
    constructor() {
        this.token = localStorage.getItem('auth_token');
    }

    setToken(token) {
        this.token = token;
        if (token) {
            localStorage.setItem('auth_token', token);
        } else {
            localStorage.removeItem('auth_token');
        }
    }

    getToken() {
        return this.token || localStorage.getItem('auth_token');
    }

    async request(url, options = {}) {
        try {
            const headers = {
                'Content-Type': 'application/json',
                ...options.headers,
            };

            // Добавляем токен авторизации, если есть
            const token = this.getToken();
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            const response = await fetch(`${API_BASE}${url}`, {
                headers,
                ...options,
            });
            
            // Получаем текст ответа для отладки
            const responseText = await response.text();
            let responseData;
            
            // Проверяем, является ли ответ HTML (ошибка от Waitress)
            if (responseText.trim().startsWith('<!DOCTYPE') || responseText.trim().startsWith('<html')) {
                console.error('Сервер вернул HTML вместо JSON:', responseText.substring(0, 200));
                responseData = {
                    error: 'Internal Server Error',
                    message: 'Сервер вернул HTML ошибку. Возможно, PostgreSQL не запущен.',
                    hint: 'Проверьте, что PostgreSQL запущен на порту 5433',
                    status: response.status
                };
            } else {
                try {
                    responseData = JSON.parse(responseText);
                } catch (e) {
                    console.error('Ошибка парсинга JSON ответа:', responseText);
                    // Если это текстовая ошибка от сервера
                    if (responseText.includes('Internal Server Error')) {
                        responseData = {
                            error: 'Internal Server Error',
                            message: 'Сервер вернул ошибку. Проверьте логи сервера.',
                            details: responseText.substring(0, 200)
                        };
                    } else {
                        throw new Error(`Неверный формат ответа от сервера: ${responseText.substring(0, 100)}`);
                    }
                }
            }
            
            if (!response.ok) {
                const errorMsg = responseData.error || responseData.message || `HTTP ${response.status}`;
                console.error('API ошибка:', {
                    url: `${API_BASE}${url}`,
                    status: response.status,
                    error: errorMsg,
                    response: responseData
                });
                throw new Error(errorMsg);
            }
            
            return responseData;
        } catch (error) {
            console.error('Ошибка в request:', {
                url: `${API_BASE}${url}`,
                error: error.message,
                options
            });
            throw error;
        }
    }

    // Nodes
    async getNodes() {
        return this.request('/nodes');
    }

    async createNode(data) {
        return this.request('/nodes', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async getNode(id) {
        return this.request(`/nodes/${id}`);
    }

    async updateNode(id, data) {
        return this.request(`/nodes/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    async deleteNode(id) {
        return this.request(`/nodes/${id}`, {
            method: 'DELETE',
        });
    }

    async getNodesNearby(lat, lon, distance = 5) {
        return this.request(`/nodes/nearby?lat=${lat}&lon=${lon}&distance=${distance}`);
    }

    // VOLS
    async getVols() {
        return this.request('/vols');
    }

    async createVols(data) {
        console.log('API: createVols вызван с данными:', data);
        try {
            const response = await this.request('/vols', {
                method: 'POST',
                body: JSON.stringify(data),
            });
            console.log('API: createVols получил ответ:', response);
            return response;
        } catch (error) {
            console.error('API: createVols ошибка:', error);
            throw error;
        }
    }

    async getVolsPath(id) {
        return this.request(`/vols/${id}/path`);
    }

    async updateVols(id, data) {
        return this.request(`/vols/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    // Fibers
    async getFibers() {
        return this.request('/fibers');
    }

    async getFibersByVols(volsId) {
        return this.request(`/fibers/by-vols/${volsId}`);
    }

    async getFiber(id) {
        return this.request(`/fibers/${id}`);
    }

    async createFiber(data) {
        return this.request('/fibers', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async updateFiber(id, data) {
        return this.request(`/fibers/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    // Links
    async getLinks() {
        return this.request('/links');
    }

    async getLink(id) {
        return this.request(`/links/${id}`);
    }

    async createLink(data) {
        return this.request('/links', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async updateLink(id, data) {
        return this.request(`/links/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    async searchLinks(fiberId = null, nodeId = null) {
        const params = new URLSearchParams();
        if (fiberId) params.append('fiber_id', fiberId);
        if (nodeId) params.append('node_id', nodeId);
        return this.request(`/links/search?${params.toString()}`);
    }

    // Auth
    async login(username, password) {
        const response = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });
        if (response.access_token) {
            this.setToken(response.access_token);
        }
        return response;
    }

    async logout() {
        this.setToken(null);
    }

    async getCurrentUser() {
        return this.request('/auth/me');
    }

    // Users
    async getUsers() {
        return this.request('/users');
    }

    async createUser(data) {
        return this.request('/users', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async getUser(id) {
        return this.request(`/users/${id}`);
    }

    async updateUser(id, data) {
        return this.request(`/users/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    async deleteUser(id) {
        return this.request(`/users/${id}`, {
            method: 'DELETE',
        });
    }

    // WebMaps
    async getWebMaps() {
        return this.request('/webmaps');
    }

    async createWebMap(data) {
        return this.request('/webmaps', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async getWebMap(id) {
        return this.request(`/webmaps/${id}`);
    }

    async updateWebMap(id, data) {
        return this.request(`/webmaps/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    async deleteWebMap(id) {
        return this.request(`/webmaps/${id}`, {
            method: 'DELETE',
        });
    }

    // Export
    async exportNodesGeoJSON() {
        const token = this.getToken();
        const response = await fetch(`${API_BASE}/export/nodes.geojson`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'nodes.geojson';
        a.click();
        window.URL.revokeObjectURL(url);
    }

    async exportVolsGeoJSON() {
        const token = this.getToken();
        const response = await fetch(`${API_BASE}/export/vols.geojson`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'vols.geojson';
        a.click();
        window.URL.revokeObjectURL(url);
    }

    async exportNodesCSV() {
        const token = this.getToken();
        const response = await fetch(`${API_BASE}/export/nodes.csv`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'nodes.csv';
        a.click();
        window.URL.revokeObjectURL(url);
    }

    async exportFibersCSV() {
        const token = this.getToken();
        const response = await fetch(`${API_BASE}/export/fibers.csv`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'fibers.csv';
        a.click();
        window.URL.revokeObjectURL(url);
    }

    async exportAllJSON() {
        const token = this.getToken();
        const response = await fetch(`${API_BASE}/export/all.json`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'vols_gis_export.json';
        a.click();
        window.URL.revokeObjectURL(url);
    }

    // Stats
    async getStatsDashboard() {
        return this.request('/stats/dashboard');
    }

    async getStatsSummary() {
        return this.request('/stats/summary');
    }

    // Search with filters
    async getNodes(filters = {}) {
        const params = new URLSearchParams();
        if (filters.node_type) params.append('node_type', filters.node_type);
        if (filters.status) params.append('status', filters.status);
        if (filters.search) params.append('search', filters.search);
        const query = params.toString();
        return this.request(`/nodes${query ? '?' + query : ''}`);
    }

    async getVols(filters = {}) {
        const params = new URLSearchParams();
        if (filters.status) params.append('status', filters.status);
        if (filters.search) params.append('search', filters.search);
        const query = params.toString();
        return this.request(`/vols${query ? '?' + query : ''}`);
    }

    async getFibers(filters = {}) {
        const params = new URLSearchParams();
        if (filters.vols_id) params.append('vols_id', filters.vols_id);
        if (filters.status) params.append('status', filters.status);
        if (filters.search) params.append('search', filters.search);
        const query = params.toString();
        return this.request(`/fibers${query ? '?' + query : ''}`);
    }

    async getLinks(filters = {}) {
        const params = new URLSearchParams();
        if (filters.fiber_id) params.append('fiber_id', filters.fiber_id);
        if (filters.start_node_id) params.append('start_node_id', filters.start_node_id);
        if (filters.end_node_id) params.append('end_node_id', filters.end_node_id);
        if (filters.status) params.append('status', filters.status);
        const query = params.toString();
        return this.request(`/links${query ? '?' + query : ''}`);
    }
}

const api = new APIClient();

