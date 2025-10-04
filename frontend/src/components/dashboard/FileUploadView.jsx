import React, { useState } from 'react';
import { getModelTypeForAPI } from '../../utils/apiHelpers';

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
            <button onClick={onBack} className="mb-6 text-blue-600 hover:text-blue-800 font-semibold">&larr; Back to Selections</button>
            <h1 className="text-3xl font-bold text-gray-800">{model}</h1>
            <p className="mt-4 text-gray-600">Please upload the MRI scan file. Accepted formats: PNG, JPG.</p>
            <div className="mt-8 p-8 bg-white rounded-lg shadow-md">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-10 text-center">
                    <input type="file" id="file-upload" className="hidden" accept=".png,.jpg,.jpeg" onChange={handleFileChange}/>
                    <label htmlFor="file-upload" className="cursor-pointer bg-blue-100 text-blue-700 font-semibold py-2 px-4 rounded-md hover:bg-blue-200">Choose File</label>
                    {selectedFile && <p className="mt-4 text-gray-600">Selected: <strong>{selectedFile.name}</strong></p>}
                </div>
                {error && <p className="mt-4 text-red-500 text-center">{error}</p>}
                <div className="mt-6 text-right">
                    <button onClick={handleAnalyze} className="bg-blue-600 text-white font-bold px-6 py-3 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed" disabled={!selectedFile || isLoading}>
                        {isLoading ? 'Analyzing...' : 'Upload & Analyze'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default FileUploadView;