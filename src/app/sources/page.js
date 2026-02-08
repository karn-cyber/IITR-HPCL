'use client';

import { useState, useEffect } from 'react';
import { generateMockLeads } from '@/lib/intelligence/mockData';
import {
    Globe,
    Newspaper,
    FileText,
    Zap,
    BarChart3,
    Activity,
    ArrowRight
} from 'lucide-react';
import Link from 'next/link';

export default function SourcesPage() {
    const [leads, setLeads] = useState([]);

    useEffect(() => {
        setLeads(generateMockLeads(200));
    }, []);

    const sources = [
        {
            name: 'GeM Portal (Tenders)',
            icon: <FileText className="text-blue-600" />,
            count: leads.filter(l => l.source === 'GeM Portal').length,
            description: 'Direct procurement signals from the Government e-Marketplace.',
            trend: '+12%',
            reliability: 98
        },
        {
            name: 'Financial News Feed',
            icon: <Newspaper className="text-emerald-600" />,
            count: leads.filter(l => l.source === 'Financial Express').length,
            description: 'Expansion announcements and corporate investment disclosures.',
            trend: '+5%',
            reliability: 82
        },
        {
            name: 'Corporate Websites',
            icon: <Globe className="text-amber-600" />,
            count: leads.filter(l => l.source === 'Company Website').length,
            description: 'Intent detected via company career pages and project sections.',
            trend: '-2%',
            reliability: 75
        }
    ];

    return (
        <div className="bg-gray-50 min-h-screen p-4 lg:p-10 font-montserrat pb-24 lg:pb-10">
            <div className="max-w-7xl mx-auto">
                <div className="mb-10">
                    <h1 className="text-2xl lg:text-3xl font-black text-[#003366] uppercase tracking-tighter flex items-center gap-4">
                        <span className="w-2 h-8 bg-[#DD0000]"></span> Intelligence Sources
                    </h1>
                    <p className="text-gray-500 text-[10px] lg:text-xs font-black uppercase tracking-[0.2em] mt-2 opacity-70">Data Origin & Connector Status</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                    {sources.map(source => (
                        <div key={source.name} className="bg-white rounded-3xl p-8 border border-gray-100 shadow-xl hover:translate-y-[-4px] transition-all group">
                            <div className="flex justify-between items-start mb-6">
                                <div className="p-4 bg-gray-50 rounded-2xl group-hover:bg-blue-50 transition-colors">
                                    {source.icon}
                                </div>
                                <span className="text-xs font-black text-green-600 bg-green-50 px-3 py-1 rounded-full">{source.trend}</span>
                            </div>
                            <h3 className="text-lg font-black text-gray-800 mb-2">{source.name}</h3>
                            <p className="text-gray-500 text-xs leading-relaxed mb-6 font-medium">{source.description}</p>

                            <div className="flex items-end justify-between border-t border-gray-50 pt-6">
                                <div>
                                    <p className="text-[10px] text-gray-400 font-black uppercase tracking-widest mb-1">Active Signals</p>
                                    <p className="text-2xl font-black text-[#003366]">{source.count}</p>
                                </div>
                                <div className="text-right">
                                    <p className="text-[10px] text-gray-400 font-black uppercase tracking-widest mb-1">Reliability</p>
                                    <p className="text-sm font-black text-hpcl-blue">{source.reliability}%</p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                <div className="bg-[#003366] rounded-[2.5rem] p-8 lg:p-12 text-white relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -mr-32 -mt-32"></div>
                    <div className="relative z-10 flex flex-col lg:flex-row justify-between items-center gap-10">
                        <div className="max-w-2xl text-center lg:text-left">
                            <h2 className="text-3xl lg:text-4xl font-black mb-4 tracking-tighter uppercase">LLM Scrapers are Online</h2>
                            <p className="text-blue-100 text-sm lg:text-lg font-medium opacity-80 leading-relaxed">
                                Our proprietary Node-Intelligence layer is cross-referencing 400+ industrial news outlets
                                and GeM tender releases every 15 minutes to find high-intent B2B leads.
                            </p>
                        </div>
                        <div className="flex gap-4">
                            <div className="bg-white/10 px-8 py-6 rounded-3xl text-center backdrop-blur-md border border-white/20">
                                <p className="text-[10px] font-black uppercase tracking-[0.2em] mb-1 opacity-60">Sync Frequency</p>
                                <p className="text-3xl font-black">15m</p>
                            </div>
                            <div className="bg-white/10 px-8 py-6 rounded-3xl text-center backdrop-blur-md border border-white/20">
                                <p className="text-[10px] font-black uppercase tracking-[0.2em] mb-1 opacity-60">Success Rate</p>
                                <p className="text-3xl font-black">94%</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
