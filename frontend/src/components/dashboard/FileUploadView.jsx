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
            if (!response.ok) throw new Error(`Server responded with ${response.status}`);
            const data = await response.json();
            onAnalysisComplete(data);
        } catch (err) {
            setError('Analysis failed. Please try again.');
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
                className="mb-6 text-sm font-semibold text-muted-foreground transition-colors hover:text-foreground"
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
                        className="inline-flex cursor-pointer items-center justify-center rounded-full border border-primary/40 bg-primary/10 px-6 py-2 text-sm font-semibold text-primary transition-colors hover:border-primary hover:bg-primary/15"
                    >
                        Choose file
                    </label>
                    {selectedFile && (
                        <p className="mt-4 text-sm text-muted-foreground">
                            Selected: <span className="font-semibold text-foreground">{selectedFile.name}</span>
                        </p>
                    )}
                </div>

                {error && <p className="mt-4 text-center text-sm font-medium text-destructive">{error}</p>}

                <div className="mt-6 flex justify-end">
                    <button
                        type="button"
                        onClick={handleAnalyze}
                        className="inline-flex items-center justify-center rounded-full bg-primary px-6 py-2 text-sm font-semibold text-primary-foreground shadow-lg transition-transform hover:scale-105 disabled:cursor-not-allowed disabled:bg-muted"
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