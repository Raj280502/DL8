import React, { useState } from 'react';
import { getModelTypeForAPI, authFetch } from '../../utils/apiHelpers.jsx';

const isAlzheimerModel = (model) =>
    typeof model === 'string' && model.toLowerCase().includes('alzheimer');

const FileUploadView = ({ model, onBack, onAnalysisComplete }) => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    // Clinical data for Alzheimer multimodal late fusion
    const [age, setAge] = useState('');
    const [mmse, setMmse] = useState('');

    const showClinical = isAlzheimerModel(model);

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

        // Append clinical data for Alzheimer late fusion (only if values provided)
        if (showClinical) {
            const clinical = {};
            if (age !== '') clinical.age = parseFloat(age);
            if (mmse !== '') clinical.mmse_score = parseFloat(mmse);
            if (Object.keys(clinical).length > 0) {
                formData.append('clinical_data', JSON.stringify(clinical));
            }
        }

        try {
            const response = await authFetch('/api/detections/', {
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

            // Include model type and detection ID in the result data for report generation
            const resultWithMetadata = {
                ...data,
                model_type: getModelTypeForAPI(model),
                detection_id: data.id,
            };
            onAnalysisComplete(resultWithMetadata);
        } catch (err) {
            setError(err.message || 'Analysis failed. Please try again.');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div>
            <button type="button" onClick={onBack} className="mb-6 btn-ghost">
                ← Back to selections
            </button>
            <h1 className="text-3xl font-bold">{model}</h1>
            <p className="mt-3 text-muted-foreground">
                Upload a medical image in PNG or JPG format to begin inference.
            </p>

            <div className="mt-8 rounded-3xl border border-border/70 bg-background/60 p-8 shadow-sm space-y-6">

                {/* ── Image Upload ── */}
                <div className="rounded-3xl border-2 border-dashed border-border/60 bg-card/40 p-10 text-center">
                    <input
                        type="file"
                        id="file-upload"
                        className="hidden"
                        accept=".png,.jpg,.jpeg"
                        onChange={handleFileChange}
                    />
                    <label htmlFor="file-upload" className="btn-secondary cursor-pointer px-6 py-2 text-sm">
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

                {/* ── Clinical Data Panel (Alzheimer only) ── */}
                {showClinical && (
                    <div className="rounded-2xl border border-purple-500/30 bg-purple-500/5 p-6">
                        <div className="flex items-center gap-2 mb-1">
                            <span className="text-lg">🧠</span>
                            <h3 className="text-base font-semibold text-purple-400">
                                Clinical Data — Multimodal Analysis
                            </h3>
                        </div>
                        <p className="text-xs text-muted-foreground mb-5">
                            Providing patient clinical data enables late-fusion weighting of the AI's image prediction
                            for improved accuracy. Both fields are optional.
                        </p>

                        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                            {/* Age */}
                            <div className="space-y-1">
                                <label htmlFor="patient-age" className="text-sm font-medium text-foreground">
                                    Patient Age
                                </label>
                                <input
                                    id="patient-age"
                                    type="number"
                                    min="0"
                                    max="120"
                                    placeholder="e.g. 72"
                                    value={age}
                                    onChange={(e) => setAge(e.target.value)}
                                    className="w-full rounded-xl border border-border/60 bg-background px-4 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-purple-500/40"
                                />
                            </div>

                            {/* MMSE Score */}
                            <div className="space-y-1">
                                <label htmlFor="mmse-score" className="text-sm font-medium text-foreground">
                                    MMSE Score
                                    <span className="ml-1 text-xs text-muted-foreground">(0 – 30)</span>
                                </label>
                                <input
                                    id="mmse-score"
                                    type="number"
                                    min="0"
                                    max="30"
                                    placeholder="e.g. 18"
                                    value={mmse}
                                    onChange={(e) => setMmse(e.target.value)}
                                    className="w-full rounded-xl border border-border/60 bg-background px-4 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-purple-500/40"
                                />
                                <p className="text-xs text-muted-foreground">
                                    27–30 Normal · 21–26 Mild · 10–20 Moderate · &lt;10 Severe
                                </p>
                            </div>
                        </div>
                    </div>
                )}

                {error && (
                    <div className="flex items-center justify-center gap-2 rounded-lg bg-destructive/10 p-3">
                        <span className="text-sm font-medium text-destructive">{error}</span>
                    </div>
                )}

                <div className="flex justify-end">
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