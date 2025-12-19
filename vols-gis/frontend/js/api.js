/** API клиент для backend */
const API_BASE = '/api';

class APIClient {
    async request(url, options = {}) {
        try {
            const response = await fetch(`${API_BASE}${url}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
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
}

const api = new APIClient();

