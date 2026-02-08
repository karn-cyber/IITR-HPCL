'use client';

import { useState, useEffect } from 'react';
import { generateMockLeads } from '@/lib/intelligence/mockData';
import {
    BarChart3,
    TrendingUp,
    PieChart,
    Target,
    Map,
    ArrowUpRight,
    ArrowDownRight
} from 'lucide-react';

export default function AnalyticsPage() {
    const [leads, setLeads] = useState([]);

    useEffect(() => {
        setLeads(generateMockLeads(250));
    }, []);

    const productStats = leads.reduce((acc, lead) => {
        acc[lead.primaryProduct] = (acc[lead.primaryProduct] || 0) + 1;
        return acc;
    }, {});

    const topProducts = Object.entries(productStats)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);

    return (
        <div className="bg-gray-50 min-h-screen p-4 lg:p-10 font-montserrat pb-24 lg:pb-10">
            <div className="max-w-7xl mx-auto">
                <div className="mb-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                    <div>
                        <h1 className="text-2xl lg:text-3xl font-black text-[#003366] uppercase tracking-tighter flex items-center gap-4">
                            <span className="w-2 h-8 bg-[#DD0000]"></span> B2B Analytics Hub
                        </h1>
                        <p className="text-gray-400 text-[10px] lg:text-xs font-black uppercase tracking-[0.2em] mt-2 opacity-70">Sales Pipeline & Market Penetration</p>
                    </div>
                    <div className="bg-white p-2 rounded-2xl shadow-sm border border-gray-100 flex gap-2">
                        <button className="px-4 py-2 bg-hpcl-blue text-white text-[10px] font-black rounded-xl shadow-md uppercase tracking-widest">Quarterly</button>
                        <button className="px-4 py-2 text-gray-400 text-[10px] font-black rounded-xl uppercase tracking-widest hover:bg-gray-50">Annual</button>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-10">
                    {/* Hero Stat: Conversion Funnel */}
                    <div className="lg:col-span-2 bg-white rounded-[2.5rem] p-8 lg:p-10 shadow-xl border border-gray-100">
                        <div className="flex justify-between items-center mb-10">
                            <h3 className="text-sm font-black text-[#003366] uppercase tracking-widest flex items-center gap-3">
                                <Target className="text-hpcl-red" size={18} /> Signal Conversion Funnel
                            </h3>
                            <button className="text-hpcl-blue text-[10px] font-black uppercase tracking-widest px-4 py-2 bg-blue-50 rounded-xl">Download Report</button>
                        </div>

                        <div className="space-y-8">
                            {[
                                { label: 'Raw Signals Detected', value: '4,821', percent: 100, color: 'bg-gray-200' },
                                { label: 'Qualified (Score > 0.75)', value: '1,240', percent: 65, color: 'bg-hpcl-blue' },
                                { label: 'Auto-Routed to Field', value: '452', percent: 40, color: 'bg-hpcl-red' },
                                { label: 'Closed/Conversion', value: '88', percent: 15, color: 'bg-green-600' }
                            ].map((step, i) => (
                                <div key={i}>
                                    <div className="flex justify-between items-center mb-3">
                                        <span className="text-xs font-black text-gray-600 uppercase tracking-widest">{step.label}</span>
                                        <span className="text-sm font-black text-[#003366]">{step.value}</span>
                                    </div>
                                    <div className="w-full bg-gray-50 h-4 rounded-full overflow-hidden border border-gray-100 p-0.5">
                                        <div
                                            className={`${step.color} h-full rounded-full shadow-inner transition-all duration-1000`}
                                            style={{ width: `${step.percent}%` }}
                                        ></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Right: Product Mix */}
                    <div className="bg-[#003366] rounded-[2.5rem] p-8 lg:p-10 text-white shadow-2xl flex flex-col">
                        <h3 className="text-sm font-black text-blue-200 uppercase tracking-widest mb-10 flex items-center gap-3">
                            <PieChart size={18} /> Product Demand Mix
                        </h3>

                        <div className="flex-grow space-y-6">
                            {topProducts.map(([name, count], i) => (
                                <div key={i} className="flex items-center justify-between">
                                    <div className="flex items-center gap-4">
                                        <div className={`w-3 h-3 rounded-full ${i === 0 ? 'bg-hpcl-red' : (i === 1 ? 'bg-blue-400' : 'bg-gray-400')}`}></div>
                                        <span className="text-xs font-bold tracking-tight">{name}</span>
                                    </div>
                                    <span className="text-xs font-black">{((count / leads.length) * 100).toFixed(1)}%</span>
                                </div>
                            ))}
                        </div>

                        <div className="mt-10 pt-10 border-t border-white/10">
                            <div className="flex items-center gap-4 mb-2">
                                <TrendingUp className="text-green-400" size={20} />
                                <span className="text-2xl font-black">+24.5%</span>
                            </div>
                            <p className="text-[10px] text-blue-200 font-bold uppercase tracking-widest opacity-60">Avg. Basket Value Growth</p>
                        </div>
                    </div>
                </div>

                {/* Bottom Row: Market Sentiment & Regional Heat */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="bg-white rounded-[2rem] p-8 shadow-lg border border-gray-100">
                        <div className="flex items-center justify-between mb-8">
                            <h4 className="text-xs font-black text-gray-400 uppercase tracking-widest">Market Sentiment Index</h4>
                            <ArrowUpRight className="text-green-600" />
                        </div>
                        <div className="flex items-end gap-2 h-40">
                            {[40, 60, 45, 80, 55, 90, 75, 50, 65, 85].map((h, i) => (
                                <div key={i} className="flex-1 bg-hpcl-blue/10 rounded-t-lg relative group overflow-hidden">
                                    <div className="absolute bottom-0 left-0 right-0 bg-hpcl-blue transition-all duration-500 rounded-t-lg group-hover:bg-hpcl-red" style={{ height: `${h}%` }}></div>
                                </div>
                            ))}
                        </div>
                        <div className="flex justify-between mt-4 text-[9px] font-black text-gray-400 uppercase tracking-widest">
                            <span>JAN</span>
                            <span>MAR</span>
                            <span>JUN</span>
                            <span>SEP</span>
                            <span>DEC</span>
                        </div>
                    </div>

                    <div className="bg-white rounded-[2rem] p-8 shadow-lg border border-gray-100">
                        <h4 className="text-xs font-black text-gray-400 uppercase tracking-widest mb-8">Regional Signal Intensity</h4>
                        <div className="space-y-4">
                            {[
                                { city: 'Mumbai', signals: 142, color: 'bg-hpcl-blue' },
                                { city: 'Ahmedabad', signals: 98, color: 'bg-hpcl-blue' },
                                { city: 'Chennai', signals: 86, color: 'bg-hpcl-blue' },
                                { city: 'Kolkata', signals: 74, color: 'bg-hpcl-blue' }
                            ].map((r, i) => (
                                <div key={i} className="flex items-center gap-4">
                                    <span className="w-20 text-[10px] font-bold text-gray-800">{r.city}</span>
                                    <div className="flex-grow bg-gray-50 h-2 rounded-full overflow-hidden">
                                        <div className={`${r.color} h-full`} style={{ width: `${(r.signals / 150) * 100}%` }}></div>
                                    </div>
                                    <span className="text-[10px] font-black text-[#003366]">{r.signals}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
