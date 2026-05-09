import React from 'react';
import { PhoneCall, Globe, Heart } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-primary dark:bg-[#040d18] text-gray-300 py-12 md:py-16 border-t border-white/10">
      <div className="container mx-auto px-6">
        <div className="grid md:grid-cols-4 gap-8 mb-12">
          <div className="col-span-1 md:col-span-2">
            <h3 className="text-2xl font-bold text-white mb-4 flex items-center gap-2 font-heading">
              <div className="w-8 h-8 bg-teal-500 rounded-lg flex items-center justify-center">
                <Heart className="w-5 h-5 text-white" />
              </div>
              MediChain
            </h3>
            <p className="text-primary-light max-w-sm mb-6">
              AI-powered rural health triage platform for India. Making healthcare accessible, understandable, and timely for everyone.
            </p>
            
            <div className="flex gap-4">
              <button className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors">
                <Globe className="w-4 h-4" />
                English (Change)
              </button>
            </div>
          </div>

          <div>
            <h4 className="text-white font-bold mb-4 font-heading tracking-wide">EMERGENCY</h4>
            <ul className="space-y-3">
              <li>
                <a href="tel:108" className="flex items-center gap-2 hover:text-teal-400 transition-colors">
                  <PhoneCall className="w-4 h-4 text-rose-500" />
                  Ambulance (108)
                </a>
              </li>
              <li>
                <a href="tel:104" className="flex items-center gap-2 hover:text-teal-400 transition-colors">
                  <PhoneCall className="w-4 h-4 text-amber-500" />
                  Health Helpline (104)
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-white font-bold mb-4 font-heading tracking-wide">QUICK LINKS</h4>
            <ul className="space-y-3 text-sm">
              <li><a href="#" className="hover:text-teal-400 transition-colors">About Us</a></li>
              <li><a href="#" className="hover:text-teal-400 transition-colors">For Doctors</a></li>
              <li><a href="#" className="hover:text-teal-400 transition-colors">ABDM Integration</a></li>
              <li><a href="#" className="hover:text-teal-400 transition-colors">Privacy Policy</a></li>
            </ul>
          </div>
        </div>

        <div className="pt-8 border-t border-white/10 flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-gray-500">
          <p>© {new Date().getFullYear()} MediChain. All rights reserved.</p>
          <p>Built with purpose for India 🇮🇳</p>
        </div>
      </div>
    </footer>
  );
}
