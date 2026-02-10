'use client';

import { useState, useEffect } from 'react';
import { MessageCircle, Bell, X, MapPin, Target, User, ArrowRight } from 'lucide-react';

export default function LeadAlert() {
    const [activeAlert, setActiveAlert] = useState(null);

    useEffect(() => {
        // Simulate a high-confidence lead detection after 5 seconds
        const timer = setTimeout(() => {
            setActiveAlert({
                id: 'WA-8822',
                company: 'JSW Steel Plant Expansion',
                product: 'Furnace Oil (FO)',
                confidence: 0.95,
                location: 'Bellary, Karnataka',
                officer: 'Officer Verma'
            });
        }, 8000);

        return () => clearTimeout(timer);
    }, []);

    if (!activeAlert) return null;

    return (
        <div className="fixed bottom-6 right-6 z-50 animate-bounce-subtle">
            <div className="bg-white rounded-2xl shadow-2xl border border-green-100 overflow-hidden w-80 lg:w-96">
                <div className="bg-[#25D366] p-3 flex items-center justify-between">
                    <div className="flex items-center gap-2 text-white">
                        <MessageCircle size={20} />
                        <span className="font-bold text-xs uppercase tracking-widest">WhatsApp Lead Alert</span>
                    </div>
                    <button onClick={() => setActiveAlert(null)} className="text-white/80 hover:text-white transition-colors">
                        <X size={20} />
                    </button>
                </div>

                <div className="p-5">
                    <div className="flex items-start gap-4 mb-4">
                        <div className="bg-green-100 h-10 w-10 rounded-full flex items-center justify-center text-green-600 shrink-0">
                            <Bell size={20} />
                        </div>
                        <div>
                            <p className="text-[10px] text-gray-500 font-bold uppercase mb-1">High Intent Detected</p>
                            <h4 className="text-sm font-bold text-gray-800 leading-tight">
                                {activeAlert.company} shows high interest in {activeAlert.product}
                            </h4>
                        </div>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-3 mb-5 border border-gray-100 text-[10px] lg:text-xs text-gray-600 space-y-2">
                        <p className="flex items-center gap-2">
                            <MapPin size={12} className="text-gray-400" />
                            <span>Location: <span className="font-semibold text-gray-800">{activeAlert.location}</span></span>
                        </p>
                        <p className="flex items-center gap-2">
                            <Target size={12} className="text-gray-400" />
                            <span>Confidence: <span className="font-bold text-green-600">{(activeAlert.confidence * 100)}%</span></span>
                        </p>
                        <p className="flex items-center gap-2">
                            <User size={12} className="text-gray-400" />
                            <span>Routed To: <span className="font-semibold text-gray-800">{activeAlert.officer}</span></span>
                        </p>
                    </div>

                    <div className="flex gap-2">
                        <button
                            onClick={() => {
                                window.location.href = `/leads/LEAD-1001`;
                                setActiveAlert(null);
                            }}
                            className="flex-grow bg-[#25D366] hover:bg-[#1ebc59] text-white py-2 rounded-lg text-xs font-bold transition-all shadow-md active:scale-95 flex items-center justify-center gap-2"
                        >
                            VIEW DOSSIER <ArrowRight size={14} />
                        </button>
                    </div>
                </div>
                <div className="bg-gray-50 px-5 py-2 text-[9px] text-gray-400 italic text-right border-t border-gray-100">
                    Triggered via HPCL Node Intelligence • Just now
                </div>
            </div>
        </div>
    );
}
