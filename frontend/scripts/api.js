// scripts/api.js
const API_BASE_URL = 'http://127.0.0.1:8000/api';

// This is a robust fetch wrapper for handling API calls, tokens, and errors.
async function apiFetch(endpoint, options = {}) {
    const token = localStorage.getItem('accessToken');
    const headers = options.headers || {};
    
    // The browser sets the correct Content-Type for FormData automatically, including the boundary.
    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        method: options.method || 'GET',
        headers: headers,
    };

    if (options.body) {
        // Only stringify if it's not FormData
        config.body = options.body instanceof FormData ? options.body : JSON.stringify(options.body);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        
        if (response.status === 204) return null; // Handle No Content responses

        const data = await response.json();

        if (!response.ok) {
            // Try to parse a meaningful error message from the backend response
            const errorMessage = Object.values(data).flat().join(' ') || 'An API error occurred.';
            throw new Error(errorMessage);
        }
        return data;
    } catch (error) {
        console.error('API Fetch Error:', error);
        // Re-throw the error so the calling function can handle it
        throw error;
    }
}

// API methods organized by resource
const auth = {
    login: (username, password) => apiFetch('/token/', { method: 'POST', body: { username, password } }),
    signup: (data) => apiFetch('/signup/', { method: 'POST', body: data }),
};
const expenses = {
    getAll: () => apiFetch('/expenses/'),
    create: (data) => apiFetch('/expenses/', { method: 'POST', body: data }), // Accepts plain object now
};
const approvals = {
    getAll: () => apiFetch('/approvals/'),
    act: (id, decision, comment) => apiFetch(`/approvals/${id}/act/`, { method: 'POST', body: { decision, comment } }),
};
const users = {
    getAll: () => apiFetch('/users/'),
    create: (data) => apiFetch('/users/', { method: 'POST', body: data }),
};
const workflows = {
    getAll: () => apiFetch('/workflows/'),
};