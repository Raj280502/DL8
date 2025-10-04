import React, { useState } from 'react';

// --- Sub-component for File Uploading ---
const FileUploadView = ({ model, onBack }) => {
    const [selectedFile, setSelectedFile] = useState(null);

    const handleFileChange = (event) => {
        if (event.target.files && event.target.files[0]) {
            setSelectedFile(event.target.files[0]);
        }
    };

    return (
        <div>
            <button onClick={onBack} className="mb-6 text-blue-600 hover:text-blue-800 font-semibold">
                &larr; Back to Selections
            </button>
            <h1 className="text-3xl font-bold text-gray-800">{model}</h1>
            <p className="mt-4 text-gray-600">Please upload the MRI scan file. Accepted formats: PDF, PNG, JPG.</p>
            
            <div className="mt-8 p-8 bg-white rounded-lg shadow-md">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-10 text-center">
                    <input 
                        type="file" 
                        id="file-upload" 
                        className="hidden" 
                        accept=".pdf,.png,.jpg,.jpeg"
                        onChange={handleFileChange}
                    />
                    <label 
                        htmlFor="file-upload" 
                        className="cursor-pointer bg-blue-100 text-blue-700 font-semibold py-2 px-4 rounded-md hover:bg-blue-200"
                    >
                        Choose File
                    </label>
                    {selectedFile && (
                        <p className="mt-4 text-gray-600">
                            Selected: <strong>{selectedFile.name}</strong>
                        </p>
                    )}
                    <p className="mt-2 text-sm text-gray-500">or drag and drop it here</p>
                </div>

                <div className="mt-6 text-right">
                    <button 
                        className="bg-blue-600 text-white font-bold px-6 py-3 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
                        disabled={!selectedFile}
                    >
                        Upload & Analyze
                    </button>
                </div>
            </div>
        </div>
    );
};


// --- Sub-component for the detection options view ---
const DetectionsView = ({ onSelectModel }) => {
    const detectionOptions = [
        { name: 'Brain Tumor Detection', description: 'Upload an MRI scan to detect tumors.' },
        { name: 'Alzheimer Detection', description: 'Analyze scans for signs of Alzheimer\'s.' },
        { name: 'Stroke Detection', description: 'Identify strokes from brain imaging data.' }
    ];

    return (
        <div>
            <h1 className="text-3xl font-bold text-gray-800">Detections</h1>
            <p className="mt-4 text-gray-600">Please select a model to begin the detection process.</p>
            <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {detectionOptions.map(option => (
                    <div key={option.name} className="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300">
                        <h3 className="text-xl font-semibold text-gray-800">{option.name}</h3>
                        <p className="mt-2 text-gray-500">{option.description}</p>
                        <button 
                            onClick={() => onSelectModel(option.name)}
                            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                        >
                            Select
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

// --- Sub-component for the reports view ---
const ReportsView = () => {
    // ... (This component remains the same)
};


// --- Main Dashboard Page Component ---
const DashboardPage = () => {
    const [currentView, setCurrentView] = useState({
        page: 'detections', // 'detections' or 'report'
        selectedModel: null, // e.g., 'Brain Tumor Detection'
    });

    const handleSelectModel = (modelName) => {
        setCurrentView({ ...currentView, selectedModel: modelName });
    };

    const handleBackToSelection = () => {
        setCurrentView({ ...currentView, selectedModel: null });
    };

    const renderMainContent = () => {
        if (currentView.page === 'detections') {
            if (currentView.selectedModel) {
                return <FileUploadView model={currentView.selectedModel} onBack={handleBackToSelection} />;
            }
            return <DetectionsView onSelectModel={handleSelectModel} />;
        }
        if (currentView.page === 'report') {
            return <ReportsView />;
        }
    };

    return (
        <div className="pt-20 min-h-screen bg-gray-100 flex">
            {/* --- Sidebar --- */}
            <aside className="w-64 bg-white shadow-md flex-shrink-0">
                <div className="p-6">
                    <h2 className="text-xl font-bold text-gray-800 mb-6">Menu</h2>
                    <nav>
                        <ul>
                            <li>
                                <button 
                                    onClick={() => setCurrentView({ page: 'detections', selectedModel: null })}
                                    className={`w-full text-left py-2 px-4 rounded font-semibold ${currentView.page === 'detections' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-200'}`}
                                >
                                    Detections
                                </button>
                            </li>
                            <li className="mt-2">
                                <button 
                                    onClick={() => setCurrentView({ page: 'report', selectedModel: null })}
                                    className={`w-full text-left py-2 px-4 rounded font-semibold ${currentView.page === 'report' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-200'}`}
                                >
                                    Report
                                </button>
                            </li>
                        </ul>
                    </nav>
                </div>
            </aside>

            {/* --- Main Content --- */}
            <main className="flex-1 p-10">
                {renderMainContent()}
            </main>
        </div>
    );
};

export default DashboardPage;
