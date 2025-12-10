export const getModelTypeForAPI = (modelName) => {
    const mapping = {
        'Brain Tumor Detection': 'BRAIN_TUMOR',
        'Alzheimer Detection': 'ALZHEIMER',
        "Alzheimer's Detection": 'ALZHEIMER',
        'Stroke Detection': 'STROKE'
    };
    return mapping[modelName] || 'UNKNOWN';
};