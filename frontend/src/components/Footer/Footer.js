import React from 'react';
import { Linkedin } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="relative z-10 border-t border-white/10 bg-black/20">
      <div className="max-w-7xl mx-auto px-4 py-8 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="text-gray-300 text-sm">
          © {new Date().getFullYear()} TravelAI. All rights reserved.
        </div>
        <div className="flex items-center gap-3 glass px-4 py-2 rounded-lg">
          <div className="text-gray-300 text-sm">Founder &amp; Developer:</div>
          <a
            href="https://www.linkedin.com/in/prajwal-poojary-67ba4a2a3/"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 text-primary-300 hover:text-primary-200 transition-colors"
            title="Connect on LinkedIn"
          >
            <Linkedin className="w-4 h-4" />
            <span className="font-medium">Prajwal Poojary</span>
          </a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;