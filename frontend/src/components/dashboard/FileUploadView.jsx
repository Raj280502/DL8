import React, { useState } from 'react';
import { getModelTypeForAPI } from '../../utils/apiHelpers.jsx';

const FileUploadView = ({ model, onBack, onAnalysisComplete }) => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleFileChange = (event) => {
        if (event.target.files && event.target.files[0]) {
            setSelectedFile(event.target.files[0]);
            setError('');
        }
    };

    const handleAnalyze = async () => {
        if (!selectedFile) return;
        setIsLoading(true);
        setError('');

        const formData = new FormData();
        formData.append('input_file', selectedFile);
        formData.append('model_type', getModelTypeForAPI(model));

        try {
            const response = await fetch('http://127.0.0.1:8000/api/detections/', {
                method: 'POST',
                body: formData,
            });

            const text = await response.text();
            let data;
            try {
                data = text ? JSON.parse(text) : {};
            } catch (parseErr) {
                data = { error: text || 'Invalid JSON from server' };
            }

            if (!response.ok) {
                const detail = data?.error || data?.detail || `Server responded with ${response.status}`;
                throw new Error(detail);
            }

            onAnalysisComplete(data);
        } catch (err) {
            setError(err.message || 'Analysis failed. Please try again.');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div>
            <button
                type="button"
                onClick={onBack}
                className="mb-6 btn-ghost"
            >
                ← Back to selections
            </button>
            <h1 className="text-3xl font-bold">{model}</h1>
            <p className="mt-3 text-muted-foreground">
                Upload a medical image in PNG or JPG format to begin inference.
            </p>

            <div className="mt-8 rounded-3xl border border-border/70 bg-background/60 p-8 shadow-sm">
                <div className="rounded-3xl border-2 border-dashed border-border/60 bg-card/40 p-10 text-center">
                    <input
                        type="file"
                        id="file-upload"
                        className="hidden"
                        accept=".png,.jpg,.jpeg"
                        onChange={handleFileChange}
                    />
                    <label
                        htmlFor="file-upload"
                        className="btn-secondary cursor-pointer px-6 py-2 text-sm"
                    >
                        Choose file
                    </label>
                    {selectedFile && (
                        <div className="mt-4 space-y-3">
                            <p className="text-sm text-muted-foreground">
                                Selected: <span className="font-semibold text-foreground">{selectedFile.name}</span>
                            </p>
                            <img
                                src={URL.createObjectURL(selectedFile)}
                                alt="Preview"
                                className="mx-auto max-h-48 rounded-xl border border-border/50 object-contain shadow-sm"
                            />
                        </div>
                    )}
                </div>

                {error && (
                    <div className="mt-4 flex items-center justify-center gap-2 rounded-lg bg-destructive/10 p-3">
                        <span className="text-sm font-medium text-destructive">{error}</span>
                    </div>
                )}

                <div className="mt-6 flex justify-end">
                    <button
                        type="button"
                        onClick={handleAnalyze}
                        className="btn-primary px-6 py-2 text-sm disabled:cursor-not-allowed"
                        disabled={!selectedFile || isLoading}
                    >
                        {isLoading ? 'Analyzing…' : 'Upload & Analyze'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default FileUploadView;