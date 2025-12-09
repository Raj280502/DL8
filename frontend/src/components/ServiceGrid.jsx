import React from 'react';

// Example SVG Icon Component (you can replace with your own or an icon library)
const BrainIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" style={{ color: '#19183B' }}><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.874 5.094a4.5 4.5 0 015.562-2.188 4.5 4.5 0 014.125 0 4.5 4.5 0 015.562 2.188m-15.25 0v.5a4.5 4.5 0 001.08 2.912A8.966 8.966 0 0012 12a8.966 8.966 0 007.09-3.588A4.5 4.5 0 0020.125 5.5v-.5m-15.25 0c-.896 0-1.77.202-2.55.578m17.8.001c.78-.376 1.654-.579 2.55-.579m-15.25 0a4.5 4.5 0 015.562 2.188m4.125 0a4.5 4.5 0 00-5.562-2.188m-4.125 0a4.5 4.5 0 014.125 0m0 0a4.5 4.5 0 005.562 2.188" /></svg>
);


const services = [
    {
        icon: <BrainIcon />,
        title: 'Brain Tumor Detection',
        description: 'Utilize our advanced AI to detect brain tumors from MRI scans with high precision, enabling early diagnosis.'
    },
    {
        icon: <BrainIcon />,
        title: 'Alzheimer Detection',
        description: 'Analyze cognitive and imaging data to identify early signs of Alzheimer\'s disease, helping in timely intervention.'
    },
    {
        icon: <BrainIcon />,
        title: 'Stroke Detection',
        description: 'Our system provides rapid analysis of brain scans to detect strokes, crucial for immediate medical response.'
    }
];

const ServicesGrid = () => {
    return (
        <section className="py-20" style={{ backgroundColor: '#E7F2EF' }}>
            <div className="container mx-auto px-6 text-center">
                <h2 className="text-3xl font-bold mb-12" style={{ color: '#19183B' }}>Our Services</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
                    {services.map((service, index) => (
                        <div 
                            key={index} 
                            className="p-8 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 hover:transform hover:scale-105"
                            style={{ backgroundColor: '#A1C2BD' }}
                        >
                            <div className="flex justify-center">{service.icon}</div>
                            <h3 className="text-xl font-bold mb-4" style={{ color: '#19183B' }}>{service.title}</h3>
                            <p style={{ color: '#708993' }}>{service.description}</p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default ServicesGrid;