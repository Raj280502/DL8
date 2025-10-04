import React from 'react';

const TestImageComponent = () => {
    const testAnnotatedImage = "http://localhost:8000/media/annotated_images/download_annotated.jpg";
    
    return (
        <div className="p-4">
            <h2 className="text-xl font-bold mb-4">Test Annotated Image Display</h2>
            <div className="border p-4 rounded">
                <p className="mb-2">Testing annotated image URL: {testAnnotatedImage}</p>
                <img 
                    src={testAnnotatedImage}
                    alt="Test annotated brain scan"
                    className="max-w-full h-auto"
                    onLoad={() => console.log('✅ Annotated image loaded successfully')}
                    onError={(e) => {
                        console.error('❌ Failed to load annotated image');
                        console.error('Error details:', e);
                    }}
                />
            </div>
        </div>
    );
};

export default TestImageComponent;