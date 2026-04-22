// Helper to get auth headers
export const getAuthHeaders = () => {
    const token = localStorage.getItem('access');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
};

export const getModelTypeForAPI = (modelName) => {
    const mapping = {
        'Brain Tumor Detection': 'BRAIN_TUMOR',
        'Alzheimer Detection': 'ALZHEIMER',
        "Alzheimer's Detection": 'ALZHEIMER',
        'Stroke Detection': 'STROKE'
    };
    return mapping[modelName] || 'UNKNOWN';
};

// Try to refresh the access token using the refresh token
export const refreshAccessToken = async () => {
    const refresh = localStorage.getItem('refresh');
    if (!refresh) return false;

    try {
        const res = await fetch('/api/token/refresh/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh }),
        });
        if (!res.ok) return false;
        const data = await res.json();
        localStorage.setItem('access', data.access);
        return true;
    } catch {
        return false;
    }
};

// Wrapper around fetch that adds auth and handles 401 with token refresh
export const authFetch = async (url, options = {}) => {
    const token = localStorage.getItem('access');
    const headers = { ...options.headers };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    let res = await fetch(url, { ...options, headers });

    // If 401, try refreshing the token once
    if (res.status === 401) {
        const refreshed = await refreshAccessToken();
        if (refreshed) {
            const newToken = localStorage.getItem('access');
            headers['Authorization'] = `Bearer ${newToken}`;
            res = await fetch(url, { ...options, headers });
        } else {
            // Refresh failed — clear tokens and redirect to login
            logout();
            return res;
        }
    }

    return res;
};

// Clear tokens and redirect to login
export const logout = () => {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    window.location.href = '/login';
};

// Check if user has a token stored
export const isLoggedIn = () => {
    return Boolean(localStorage.getItem('access'));
};