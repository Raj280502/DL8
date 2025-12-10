import React from 'react';

const ResultsView = ({ resultData, onBack }) => {
    const { result, annotated_image, input_file, model_type } = resultData;

    // Check model types based on result structure
    const isClassification = result?.predicted_class !== undefined;
    const isBrainTumorDetection = result?.predictions !== undefined;
    const isStrokeClassification = isClassification && model_type === 'STROKE';
    const isAlzheimerClassification = isClassification && model_type === 'ALZHEIMER';

    // For classification models (stroke or alzheimer)
    const classificationResult = isClassification ? result : null;

    // For brain tumor detection
    const predictions = result?.predictions || [];

    const message = result?.message || 'Analysis completed';

    // Determine which image to show - annotated/visualization if available, otherwise original
    const displayImage = annotated_image
        ? `http://localhost:8000/media/${annotated_image}`
        : input_file;

    return (
        <div className="mx-auto max-w-4xl space-y-6">
            <button
                type="button"
                onClick={onBack}
                className="btn-ghost"
            >
                ← Back to upload
            </button>

            <div className="rounded-3xl border border-border/70 bg-card/60 p-8 shadow-sm">
                <h1 className="text-3xl font-bold">Analysis Results</h1>

                <div className="mt-6 rounded-2xl border-l-4 border-primary/60 bg-background/70 p-5">
                    <p className="text-lg font-semibold text-foreground">{message}</p>
                    <p className="mt-1 text-sm text-muted-foreground">
                        Model: {model_type?.replace('_', ' ') || 'Brain Analysis'}
                    </p>
                </div>

                {/* Stroke Classification Results */}
                {isStrokeClassification && classificationResult && (
                    <div className="mt-8">
                        <h3 className="text-xl font-semibold">Stroke Classification Result</h3>
                        <div className="mt-4 rounded-2xl border border-border/50 bg-background/70 p-5">
                            <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
                                <span className="text-lg font-bold text-foreground">
                                    {classificationResult.predicted_class}
                                </span>
                                <span className={`rounded-full px-3 py-1 text-sm font-semibold ${
                                    classificationResult.confidence > 0.8
                                        ? 'bg-green-500/20 text-green-400'
                                        : classificationResult.confidence > 0.6
                                        ? 'bg-yellow-500/20 text-yellow-400'
                                        : 'bg-red-500/20 text-red-400'
                                }`}>
                                    {Math.round(classificationResult.confidence * 100)}% confidence
                                </span>
                            </div>
                            {classificationResult.class_confidences && (
                                <div className="space-y-3">
                                    <h4 className="text-sm font-semibold text-muted-foreground">All Classifications:</h4>
                                    {Object.entries(classificationResult.class_confidences).map(([className, confidence]) => (
                                        <div key={className} className="flex items-center justify-between gap-3">
                                            <span className="text-sm text-foreground">{className}</span>
                                            <div className="flex items-center gap-2">
                                                <div className="w-24 rounded-full bg-muted h-2">
                                                    <div
                                                        className="bg-primary h-2 rounded-full transition-all"
                                                        style={{ width: `${Math.round(confidence * 100)}%` }}
                                                    />
                                                </div>
                                                <span className="text-xs text-muted-foreground w-12 text-right">
                                                    {Math.round(confidence * 100)}%
                                                </span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Alzheimer Classification Results */}
                {isAlzheimerClassification && classificationResult && (
                    <div className="mt-8">
                        <h3 className="text-xl font-semibold">Alzheimer Classification Result</h3>
                        <div className="mt-4 rounded-2xl border border-border/50 bg-background/70 p-5">
                            <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
                                <span className="text-lg font-bold text-foreground">
                                    {classificationResult.predicted_class}
                                </span>
                                <span className={`rounded-full px-3 py-1 text-sm font-semibold ${
                                    classificationResult.confidence > 0.8
                                        ? 'bg-green-500/20 text-green-400'
                                        : classificationResult.confidence > 0.6
                                        ? 'bg-yellow-500/20 text-yellow-400'
                                        : 'bg-red-500/20 text-red-400'
                                }`}>
                                    {Math.round(classificationResult.confidence * 100)}% confidence
                                </span>
                            </div>
                            {classificationResult.class_confidences && (
                                <div className="space-y-3">
                                    <h4 className="text-sm font-semibold text-muted-foreground">All Classifications:</h4>
                                    {Object.entries(classificationResult.class_confidences).map(([className, confidence]) => (
                                        <div key={className} className="flex items-center justify-between gap-3">
                                            <span className="text-sm text-foreground">{className}</span>
                                            <div className="flex items-center gap-2">
                                                <div className="w-24 rounded-full bg-muted h-2">
                                                    <div
                                                        className="bg-purple-500 h-2 rounded-full transition-all"
                                                        style={{ width: `${Math.round(confidence * 100)}%` }}
                                                    />
                                                </div>
                                                <span className="text-xs text-muted-foreground w-12 text-right">
                                                    {Math.round(confidence * 100)}%
                                                </span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Brain Tumor Detection Results */}
                {isBrainTumorDetection && predictions.length > 0 && (
                    <div className="mt-8">
                        <h3 className="text-xl font-semibold">Detection details</h3>
                        <div className="mt-4 grid gap-4">
                            {predictions.map((detection, index) => (
                                <div
                                    key={`${detection.name}-${index}`}
                                    className="rounded-2xl border border-border/50 bg-background/70 p-4"
                                >
                                    <div className="flex flex-wrap items-center justify-between gap-3">
                                        <span className="text-sm font-semibold text-foreground">
                                            {detection.name || 'Brain Tumor'}
                                        </span>
                                        <span className="rounded-full bg-primary/15 px-3 py-1 text-xs font-semibold text-primary">
                                            {Math.round((detection.confidence || 0) * 100)}% confidence
                                        </span>
                                    </div>
                                    <p className="mt-2 text-xs text-muted-foreground">
                                        Location: ({Math.round(detection.xmin)}, {Math.round(detection.ymin)}) → ({Math.round(detection.xmax)}, {Math.round(detection.ymax)})
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                <div className="mt-8 rounded-2xl border border-border/60 bg-background/70 p-5">
                    <h3 className="text-xl font-semibold">
                        {annotated_image
                            ? isStrokeClassification || isAlzheimerClassification
                                ? 'Grad-CAM Visualization'
                                : 'Annotated scan with detections'
                            : 'Original scan'}
                    </h3>
                    <div className="mt-4 flex justify-center">
                        <img
                            src={displayImage}
                            alt="Brain scan analysis result"
                            className="max-h-[600px] w-full rounded-2xl border border-border/60 object-contain shadow-md"
                            onError={(e) => {
                                console.error('Error loading annotated image, falling back to original');
                                e.target.src = input_file;
                            }}
                        />
                    </div>
                    {annotated_image && (
                        <p className="mt-3 text-center text-xs text-muted-foreground">
                            {isStrokeClassification || isAlzheimerClassification
                                ? 'Heatmap overlay shows areas the AI model focused on for classification'
                                : 'Red bounding boxes indicate detected abnormalities.'}
                        </p>
                    )}
                </div>

                {/* No Detections Message for Brain Tumor Detection */}
                {isBrainTumorDetection && predictions.length === 0 && (
                    <div className="mt-6 rounded-2xl border-l-4 border-primary/50 bg-background/70 p-5">
                        <p className="font-semibold text-foreground">✅ No abnormalities detected</p>
                        <p className="mt-1 text-sm text-muted-foreground">
                            This scan shows no concerning findings. Continue monitoring as needed.
                        </p>
                    </div>
                )}

                {/* Clinical Interpretation for Stroke */}
                {isStrokeClassification && classificationResult && (
                    <div className="mt-6 rounded-2xl border-l-4 border-yellow-500/60 bg-yellow-500/10 p-5">
                        <p className="font-semibold text-yellow-400">⚠️ Clinical Note</p>
                        <p className="mt-1 text-sm text-yellow-300/80">
                            This AI analysis is for research purposes only and should not be used for clinical diagnosis.
                            Always consult with a qualified medical professional for proper interpretation of medical imaging.
                        </p>
                    </div>
                )}

                {/* Clinical Interpretation for Alzheimer */}
                {isAlzheimerClassification && classificationResult && (
                    <div className="mt-6 rounded-2xl border-l-4 border-purple-500/60 bg-purple-500/10 p-5">
                        <p className="font-semibold text-purple-400">⚠️ Clinical Note</p>
                        <p className="mt-1 text-sm text-purple-300/80">
                            This AI analysis is for research purposes only. Alzheimer's disease diagnosis requires 
                            comprehensive clinical evaluation including cognitive assessments, medical history, and 
                            professional medical consultation.
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ResultsView;