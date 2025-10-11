import React from 'react';

const ResultsView = ({ resultData, onBack }) => {
    // Extract data from the new result format
    const { result, annotated_image, input_file, model_type } = resultData;
    
    // Check if this is stroke classification (has predicted_class) or object detection (has predictions)
    const isStrokeClassification = result?.predicted_class !== undefined;
    const isBrainTumorDetection = result?.predictions !== undefined;
    
    // For stroke classification
    const strokeResult = isStrokeClassification ? result : null;
    
    // For brain tumor detection
    const predictions = result?.predictions || [];
    
    const message = result?.message || `Analysis completed`;
    
    // Determine which image to show - annotated/visualization if available, otherwise original
    const displayImage = annotated_image 
        ? `http://localhost:8000/media/${annotated_image}` 
        : input_file;

    return (
        <div className="max-w-4xl mx-auto p-6">
            <button 
                onClick={onBack} 
                className="mb-6 text-blue-600 hover:text-blue-800 font-semibold flex items-center gap-2"
            >
                ← Back to Upload
            </button>
            
            <div className="bg-white rounded-lg shadow-lg p-6">
                <h1 className="text-3xl font-bold text-gray-800 mb-4">Analysis Results</h1>
                
                {/* Analysis Summary */}
                <div className="mb-6 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
                    <p className="text-lg font-semibold text-blue-800">{message}</p>
                    <p className="text-sm text-blue-600 mt-1">
                        Model: {model_type?.replace('_', ' ') || 'Brain Analysis'}
                    </p>
                </div>

                {/* Stroke Classification Results */}
                {isStrokeClassification && strokeResult && (
                    <div className="mb-6">
                        <h3 className="text-xl font-semibold text-gray-700 mb-3">Classification Result:</h3>
                        
                        {/* Main Prediction */}
                        <div className="bg-gray-50 p-4 rounded-lg border mb-4">
                            <div className="flex justify-between items-center mb-3">
                                <span className="text-lg font-bold text-gray-800">
                                    {strokeResult.predicted_class}
                                </span>
                                <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                                    strokeResult.confidence > 0.8 ? 'bg-green-100 text-green-800' :
                                    strokeResult.confidence > 0.6 ? 'bg-yellow-100 text-yellow-800' :
                                    'bg-red-100 text-red-800'
                                }`}>
                                    {Math.round(strokeResult.confidence * 100)}% confidence
                                </span>
                            </div>
                            
                            {/* All Class Confidences */}
                            {strokeResult.class_confidences && (
                                <div className="grid gap-2">
                                    <h4 className="text-sm font-semibold text-gray-600 mb-2">All Classifications:</h4>
                                    {Object.entries(strokeResult.class_confidences).map(([className, confidence]) => (
                                        <div key={className} className="flex justify-between items-center">
                                            <span className="text-sm text-gray-700">{className}</span>
                                            <div className="flex items-center gap-2">
                                                <div className="w-24 bg-gray-200 rounded-full h-2">
                                                    <div 
                                                        className="bg-blue-500 h-2 rounded-full" 
                                                        style={{ width: `${Math.round(confidence * 100)}%` }}
                                                    ></div>
                                                </div>
                                                <span className="text-xs text-gray-600 w-12 text-right">
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
                    <div className="mb-6">
                        <h3 className="text-xl font-semibold text-gray-700 mb-3">Detection Details:</h3>
                        <div className="grid gap-3">
                            {predictions.map((detection, index) => (
                                <div key={index} className="bg-gray-50 p-3 rounded-lg border">
                                    <div className="flex justify-between items-center">
                                        <span className="font-medium text-gray-800">
                                            {detection.name || 'Brain Tumor'}
                                        </span>
                                        <span className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-sm font-semibold">
                                            {Math.round((detection.confidence || 0) * 100)}% confidence
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-600 mt-1">
                                        Location: ({Math.round(detection.xmin)}, {Math.round(detection.ymin)}) to ({Math.round(detection.xmax)}, {Math.round(detection.ymax)})
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Image Display */}
                <div className="bg-gray-100 p-4 rounded-lg">
                    <h3 className="text-xl font-semibold text-gray-700 mb-3">
                        {annotated_image ? (
                            isStrokeClassification ? 'Grad-CAM Visualization' : 'Annotated Scan with Detections'
                        ) : 'Original Scan'}
                    </h3>
                    <div className="flex justify-center">
                        <img 
                            src={displayImage}
                            alt="Brain scan analysis result"
                            className="max-w-full h-auto rounded-lg shadow-md border"
                            style={{ maxHeight: '600px' }}
                            onError={(e) => {
                                console.error('Error loading image, falling back to original');
                                e.target.src = input_file;
                            }}
                        />
                    </div>
                    {annotated_image && (
                        <p className="text-sm text-gray-600 mt-2 text-center">
                            {isStrokeClassification 
                                ? 'Heatmap overlay shows areas the AI model focused on for classification'
                                : 'Red bounding boxes indicate detected brain tumors'
                            }
                        </p>
                    )}
                </div>

                {/* No Detections Message for Brain Tumor Detection */}
                {isBrainTumorDetection && predictions.length === 0 && (
                    <div className="mt-6 p-4 bg-green-50 rounded-lg border-l-4 border-green-500">
                        <p className="text-green-800 font-medium">✅ No brain tumors detected in this scan</p>
                        <p className="text-green-600 text-sm mt-1">This is a positive result indicating no abnormalities were found.</p>
                    </div>
                )}

                {/* Clinical Interpretation for Stroke */}
                {isStrokeClassification && strokeResult && (
                    <div className="mt-6 p-4 bg-yellow-50 rounded-lg border-l-4 border-yellow-500">
                        <p className="text-yellow-800 font-medium">⚠️ Clinical Note</p>
                        <p className="text-yellow-700 text-sm mt-1">
                            This AI analysis is for research purposes only and should not be used for clinical diagnosis. 
                            Always consult with a qualified medical professional for proper interpretation of medical imaging.
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ResultsView;