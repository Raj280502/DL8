import React from 'react';
import { Activity, Brain, Microscope } from 'lucide-react';

const DetectionsView = ({ onSelectModel }) => {
    const detectionOptions = [
        {
            name: 'Brain Tumor Detection',
            description: 'Upload an MRI scan to detect tumors and highlight critical regions.',
            icon: Microscope,
        },
        {
            name: 'Alzheimer Detection',
            description: "Analyze scans for early indicators of cognitive decline and memory loss.",
            icon: Brain,
        },
        {
            name: 'Stroke Detection',
            description: 'Identify ischemic and hemorrhagic strokes using CT or MRI datasets.',
            icon: Activity,
        },
    ];

    return (
        <div>
            <h1 className="text-3xl font-bold">Detections</h1>
            <p className="mt-3 text-muted-foreground">
                Select an AI pipeline to begin processing your medical imaging scans.
            </p>
            <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
                {detectionOptions.map(({ name, description, icon: Icon }) => (
                    <div
                        key={name}
                        className="flex h-full flex-col justify-between rounded-3xl border border-border/60 bg-card/70 p-6 shadow-sm transition-transform hover:-translate-y-1 hover:border-primary/50 hover:shadow-lg"
                    >
                        <div>
                            <div className="mb-5 inline-flex items-center justify-center rounded-2xl bg-primary/10 p-3">
                                <Icon className="h-6 w-6 text-primary" />
                            </div>
                            <h3 className="text-xl font-semibold leading-tight">{name}</h3>
                            <p className="mt-3 text-sm text-muted-foreground">{description}</p>
                        </div>
                        <button
                            type="button"
                            onClick={() => onSelectModel(name)}
                            className="mt-6 inline-flex items-center justify-center rounded-full bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground transition-transform hover:scale-105 hover:glow-primary"
                        >
                            Select Pipeline
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default DetectionsView;