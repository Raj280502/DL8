import React, { useState } from 'react';
import DetectionsView from '../components/dashboard/DetectionsView';
import FileUploadView from '../components/dashboard/FileUploadView';
import ResultsView from '../components/dashboard/ResultsView';

// We can define ReportsView here or move it to its own file if it becomes complex
const ReportsView = () => (
    <div>
        <h1 className="text-3xl font-bold text-gray-800">Reports</h1>
        <p className="mt-4 text-gray-600">All generated reports will be available here.</p>
    </div>
);

const DashboardPage = () => {
    const [currentView, setCurrentView] = useState({
        page: 'detections',
        selectedModel: null,
        resultData: null,
    });

    const handleAnalysisComplete = (data) => {
        setCurrentView({ ...currentView, resultData: data });
    };
    
    const handleBackToUpload = () => {
        setCurrentView({ ...currentView, resultData: null });
    };

    const renderMainContent = () => {
        const { page, selectedModel, resultData } = currentView;

        if (page === 'detections') {
            if (resultData) {
                return <ResultsView resultData={resultData} onBack={handleBackToUpload} />;
            }
            if (selectedModel) {
                return <FileUploadView model={selectedModel} onBack={() => setCurrentView({ ...currentView, selectedModel: null })} onAnalysisComplete={handleAnalysisComplete} />;
            }
            return <DetectionsView onSelectModel={(model) => setCurrentView({ ...currentView, selectedModel: model })} />;
        }
        if (page === 'report') {
            return <ReportsView />;
        }
    };

    return (
        <div className="pt-20 min-h-screen bg-gray-100 flex">
            {/* Sidebar */}
            <aside className="w-64 bg-white shadow-md flex-shrink-0">
                <div className="p-6">
                    <h2 className="text-xl font-bold text-gray-800 mb-6">Menu</h2>
                    <nav>
                        <ul>
                            <li><button onClick={() => setCurrentView({ page: 'detections', selectedModel: null, resultData: null })} className={`w-full text-left py-2 px-4 rounded font-semibold ${currentView.page === 'detections' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-200'}`}>Detections</button></li>
                            <li className="mt-2"><button onClick={() => setCurrentView({ page: 'report', selectedModel: null, resultData: null })} className={`w-full text-left py-2 px-4 rounded font-semibold ${currentView.page === 'report' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-200'}`}>Report</button></li>
                        </ul>
                    </nav>
                </div>
            </aside>
            {/* Main Content */}
            <main className="flex-1 p-10">{renderMainContent()}</main>
        </div>
    );
};

export default DashboardPage;