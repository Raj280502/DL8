import React, { useState } from 'react';
import DetectionsView from '../components/dashboard/DetectionsView';
import FileUploadView from '../components/dashboard/FileUploadView';
import ResultsView from '../components/dashboard/ResultsView';
import ChatView from '../components/dashboard/ChatView';

const ReportsView = () => (
    <div>
        <h1 className="text-3xl font-bold">Reports</h1>
        <p className="mt-4 text-muted-foreground">All generated reports will be available here.</p>
    </div>
);

const menuItems = [
    { key: 'detections', label: 'Detections', description: 'Run AI-powered analyses across imaging modalities.' },
    { key: 'chat', label: 'Neuro Chat', description: 'Ask neuroanatomy and brain-disease questions.' },
    { key: 'report', label: 'Reports', description: 'Review exported summaries and historical findings.' },
];

const DashboardPage = () => {
    const [currentView, setCurrentView] = useState({
        page: 'detections',
        selectedModel: null,
        resultData: null,
    });

    const setPage = (page) => setCurrentView({ page, selectedModel: null, resultData: null });

    const handleAnalysisComplete = (data) => {
        setCurrentView((prev) => ({ ...prev, resultData: data }));
    };

    const handleBackToUpload = () => {
        setCurrentView((prev) => ({ ...prev, resultData: null }));
    };

    const renderMainContent = () => {
        const { page, selectedModel, resultData } = currentView;

        if (page === 'detections') {
            if (resultData) {
                return <ResultsView resultData={resultData} onBack={handleBackToUpload} />;
            }
            if (selectedModel) {
                return (
                    <FileUploadView
                        model={selectedModel}
                        onBack={() => setCurrentView((prev) => ({ ...prev, selectedModel: null }))}
                        onAnalysisComplete={handleAnalysisComplete}
                    />
                );
            }
            return <DetectionsView onSelectModel={(model) => setCurrentView((prev) => ({ ...prev, selectedModel: model }))} />;
        }

        if (page === 'chat') {
            return <ChatView />;
        }

        if (page === 'report') {
            return <ReportsView />;
        }

        return null;
    };

    return (
        <div className="bg-background">
            <div className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-7xl flex-col gap-6 px-6 py-12 lg:flex-row">
                <aside className="rounded-3xl border border-border/70 bg-card/60 p-6 shadow-sm lg:w-72">
                    <h2 className="text-lg font-semibold">Workspace</h2>
                    <p className="mt-2 text-sm text-muted-foreground">
                        Navigate analysis pipelines and review key reports.
                    </p>
                    <nav className="mt-6 space-y-2">
                        {menuItems.map((item) => {
                            const isActive = currentView.page === item.key;
                            return (
                                <button
                                    key={item.key}
                                    type="button"
                                    onClick={() => setPage(item.key)}
                                    className={`w-full rounded-2xl border px-4 py-3 text-left transition-all ${
                                        isActive
                                            ? 'border-primary/60 bg-primary/10 text-primary shadow-md'
                                            : 'border-transparent bg-transparent text-muted-foreground hover:border-border hover:bg-muted/40 hover:text-foreground'
                                    }`}
                                >
                                    <p className="text-sm font-semibold">{item.label}</p>
                                    <p className="mt-1 text-xs text-muted-foreground">{item.description}</p>
                                </button>
                            );
                        })}
                    </nav>
                </aside>

                <main className="flex-1 rounded-3xl border border-border/70 bg-card/40 p-8 shadow-sm backdrop-blur">
                    {renderMainContent()}
                </main>
            </div>
        </div>
    );
};

export default DashboardPage;