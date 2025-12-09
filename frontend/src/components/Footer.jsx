import React from 'react';

const Footer = () => {
    const currentYear = new Date().getFullYear();

    return (
        <footer style={{ backgroundColor: '#19183B', color: '#A1C2BD' }}>
            <div className="container mx-auto px-6 py-12">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                    {/* About Section */}
                    <div>
                        <h3 className="text-lg font-bold mb-4" style={{ color: '#E7F2EF' }}>AI Diagnostics</h3>
                        <p className="text-sm">Pioneering the future of medical technology with AI-driven insights.</p>
                    </div>

                    {/* Links */}
                    <div>
                        <h3 className="text-lg font-bold mb-4" style={{ color: '#E7F2EF' }}>Quick Links</h3>
                        <ul className="space-y-2 text-sm">
                            <li><a href="#" className="transition-colors duration-300" style={{ color: '#A1C2BD' }} onMouseEnter={(e) => e.target.style.color = '#E7F2EF'} onMouseLeave={(e) => e.target.style.color = '#A1C2BD'}>Home</a></li>
                            <li><a href="#" className="transition-colors duration-300" style={{ color: '#A1C2BD' }} onMouseEnter={(e) => e.target.style.color = '#E7F2EF'} onMouseLeave={(e) => e.target.style.color = '#A1C2BD'}>About</a></li>
                            <li><a href="#" className="transition-colors duration-300" style={{ color: '#A1C2BD' }} onMouseEnter={(e) => e.target.style.color = '#E7F2EF'} onMouseLeave={(e) => e.target.style.color = '#A1C2BD'}>Services</a></li>
                            <li><a href="#" className="transition-colors duration-300" style={{ color: '#A1C2BD' }} onMouseEnter={(e) => e.target.style.color = '#E7F2EF'} onMouseLeave={(e) => e.target.style.color = '#A1C2BD'}>Contact</a></li>
                        </ul>
                    </div>

                    {/* Legal */}
                    <div>
                        <h3 className="text-lg font-bold mb-4" style={{ color: '#E7F2EF' }}>Legal</h3>
                        <ul className="space-y-2 text-sm">
                            <li><a href="#" className="hover:text-white">Privacy Policy</a></li>
                            <li><a href="#" className="hover:text-white">Terms of Service</a></li>
                        </ul>
                    </div>

                    {/* Social Media */}
                    <div>
                        <h3 className="text-lg font-bold text-white mb-4">Follow Us</h3>
                        <div className="flex space-x-4">
                            {/* Replace with actual icons from a library if you want */}
                            <a href="#" className="hover:text-white">Twitter</a>
                            <a href="#" className="hover:text-white">LinkedIn</a>
                            <a href="#" className="hover:text-white">Facebook</a>
                        </div>

                    </div>
                </div>

                {/* Copyright */}
                <div className="mt-12 border-t border-gray-700 pt-8 text-center text-sm">
                    <p>&copy; {currentYear} MySite. All rights reserved.</p>
                </div>
            </div>
        </footer>
    );
};

export default Footer;