import React from 'react';
import { Activity, Brain, Microscope } from 'lucide-react';

const DetectionsView = ({ onSelectModel }) => {
    const detectionOptions = [
        {
            id: 'brain_tumor',
            name: 'Brain Tumor Detection',
            description: 'Upload an MRI scan to detect and localize tumors with bounding boxes.',
            icon: Microscope,
            status: 'available',
        },
        {
            id: 'alzheimer',
            name: "Alzheimer's Detection",
            description: 'Classify brain MRI scans into dementia stages: Non, Very Mild, Mild, or Moderate.',
            icon: Brain,
            status: 'available',
        },
        {
            id: 'stroke',
            name: 'Stroke Detection',
            description: 'Identify ischemic and hemorrhagic strokes using CT or MRI datasets.',
            icon: Activity,
            status: 'unavailable',
        },
    ];

    return (
        <div>
            <h1 className="text-3xl font-bold">Detections</h1>
            <p className="mt-3 text-muted-foreground">
                Select an AI pipeline to begin processing your medical imaging scans.
            </p>
            <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
                {detectionOptions.map(({ id, name, description, icon: Icon, status }) => {
                    const isAvailable = status === 'available';
                    return (
                        <div
                            key={id}
                            className={`flex h-full flex-col justify-between rounded-3xl border p-6 shadow-sm transition-all ${
                                isAvailable
                                    ? 'border-border/60 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-slate-800 dark:via-slate-700 dark:to-slate-800 hover:-translate-y-1 hover:border-primary/50 hover:shadow-lg'
                                    : 'border-border/40 bg-gray-100 dark:bg-slate-800 opacity-60'
                            }`}
                        >
                            <div>
                                <div className="mb-4 flex items-center justify-between">
                                    <div className={`inline-flex items-center justify-center rounded-2xl p-3 ${isAvailable ? 'bg-gradient-to-br from-blue-500 to-purple-500' : 'bg-gray-300 dark:bg-slate-600'}`}>
                                        <Icon className={`h-6 w-6 ${isAvailable ? 'text-white' : 'text-gray-500 dark:text-gray-400'}`} />
                                    </div>
                                    {!isAvailable && (
                                        <span className="rounded-full bg-yellow-500/20 px-2 py-1 text-xs font-medium text-yellow-600 dark:text-yellow-400">
                                            Model Missing
                                        </span>
                                    )}
                                </div>
                                <h3 className="text-xl font-semibold leading-tight text-gray-800 dark:text-white">{name}</h3>
                                <p className="mt-3 text-sm text-gray-600 dark:text-gray-300">{description}</p>
                            </div>
                            <button
                                type="button"
                                onClick={() => isAvailable && onSelectModel(name)}
                                disabled={!isAvailable}
                                className={`mt-6 px-4 py-2.5 text-sm font-semibold rounded-xl transition-all ${
                                    isAvailable
                                        ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:shadow-lg hover:scale-[1.02]'
                                        : 'bg-gray-200 dark:bg-slate-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'
                                }`}
                            >
                                {isAvailable ? 'Select Pipeline' : 'Coming Soon'}
                            </button>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default DetectionsView;
