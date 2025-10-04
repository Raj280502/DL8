import React from 'react';

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

export default DetectionsView;