'use client';

import { useState, useEffect } from 'react';
import { generateMockLeads } from '@/lib/intelligence/mockData';
import Link from 'next/link';
import { Search, MapPin, Building2, TrendingUp, Filter } from 'lucide-react';

export default function LeadsQueue() {
    const [leads, setLeads] = useState([]);
    const [filter, setFilter] = useState('ALL');
    const [search, setSearch] = useState('');

    useEffect(() => {
        const allLeads = generateMockLeads(200);
        setLeads(allLeads);
    }, []);

    const filteredLeads = leads.filter(lead => {
        const matchesSearch = lead.company.toLowerCase().includes(search.toLowerCase()) ||
            lead.primaryProduct.toLowerCase().includes(search.toLowerCase());
        const matchesFilter = filter === 'ALL' || lead.status === filter;
        return matchesSearch && matchesFilter;
    });

    return (
        <div className="bg-gray-50 min-h-screen font-montserrat pb-24 lg:pb-10">
            {/* Mobile Sticky Header */}
            <div className="lg:hidden bg-[#0055A4] p-5 pt-7 text-white sticky top-0 z-30 shadow-lg">
                <div className="flex justify-between items-center mb-4">
                    <h1 className="text-lg font-black uppercase tracking-widest flex items-center gap-2">
                        <span className="w-1.5 h-5 bg-[#DD0000]"></span> Intel Queue
                    </h1>
                </div>
                <div className="space-y-4">
                    <div className="relative">
                        <input
                            type="text"
                            placeholder="Quick search entities..."
                            className="w-full bg-white border-none rounded-xl py-3 px-5 text-sm focus:outline-none text-gray-800 placeholder:text-gray-400 transition-all font-bold shadow-inner"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />
                        <Search className="absolute right-4 top-3.5 opacity-30 text-black px-0.5" size={18} />
                    </div>
                    <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide py-1">
                        {['ALL', 'AUTO_ASSIGNED', 'QUALIFIED', 'REVIEW_REQUIRED'].map(f => (
                            <button
                                key={f}
                                onClick={() => setFilter(f)}
                                className={`whitespace-nowrap px-5 py-2 rounded-full text-[9px] font-black uppercase tracking-widest transition-all shadow-sm ${filter === f ? 'bg-[#DD0000] text-white ring-2 ring-white/50' : 'bg-white/10 border border-white/20 text-white'}`}
                            >
                                {f.replace('_', ' ')}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Desktop Header */}
            <div className="hidden lg:block bg-white border-b border-gray-200 px-20 py-10">
                <div className="max-w-7xl mx-auto flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-black text-[#003366] uppercase tracking-tighter flex items-center gap-4">
                            <span className="w-2 h-10 bg-[#DD0000]"></span> B2B Signal Inventory
                        </h1>
                        <p className="text-gray-400 text-[10px] mt-1 font-black tracking-[0.3em] uppercase opacity-60">Verified Direct Sales Pipe</p>
                    </div>

                    <div className="flex gap-4">
                        <input
                            type="text"
                            placeholder="Filter by company, product..."
                            className="px-6 py-3 bg-gray-50 border border-gray-100 rounded-2xl text-sm focus:ring-2 focus:ring-hpcl-blue focus:bg-white transition-all w-80 font-bold outline-none shadow-sm"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />
                        <select
                            className="px-6 py-3 bg-gray-50 border border-gray-100 rounded-2xl text-sm focus:ring-2 focus:ring-hpcl-blue focus:outline-none font-black uppercase tracking-widest text-[#003366] shadow-sm"
                            value={filter}
                            onChange={(e) => setFilter(e.target.value)}
                        >
                            <option value="ALL">All Signals</option>
                            <option value="AUTO_ASSIGNED">Priority</option>
                            <option value="QUALIFIED">Qualified</option>
                            <option value="REVIEW_REQUIRED">Review</option>
                        </select>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 lg:px-20 py-6 lg:py-12">
                {/* MOBILE CARD VIEW */}
                <div className="lg:hidden space-y-4">
                    {filteredLeads.map(lead => (
                        <Link
                            key={lead.id}
                            href={`/leads/${lead.id}`}
                            className="block bg-white rounded-2xl p-6 shadow-sm border-l-8 hover:shadow-md transition-all active:scale-[0.97]"
                            style={{ borderLeftColor: getScoreHex(lead.confidence) }}
                        >
                            <div className="flex justify-between items-start mb-4">
                                <div className="max-w-[70%]">
                                    <h3 className="font-black text-gray-800 text-lg leading-tight tracking-tight">{lead.company}</h3>
                                    <p className="text-[10px] text-gray-400 font-extrabold uppercase tracking-widest mt-1 opacity-80 flex items-center gap-1.5">
                                        <MapPin size={10} /> {lead.location} • <Building2 size={10} /> {lead.industry}
                                    </p>
                                </div>
                                <span className={`px-2 py-1 rounded-lg text-[10px] font-black ${getScoreColor(lead.confidence)} shadow-sm`}>
                                    {(lead.confidence * 100).toFixed(0)}%
                                </span>
                            </div>
                            <div className="flex items-center justify-between border-t border-gray-50 pt-4">
                                <div className="flex gap-2">
                                    <span className="bg-hpcl-blue/5 text-hpcl-blue px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest">
                                        {lead.primaryProduct}
                                    </span>
                                </div>
                                <StatusBadge status={lead.status} />
                            </div>
                        </Link>
                    ))}
                </div>

                {/* DESKTOP TABLE VIEW */}
                <div className="hidden lg:block overflow-x-auto rounded-[2rem] border border-gray-100 shadow-2xl bg-white">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-gray-50/50 text-[#003366] text-[10px] font-black uppercase tracking-[0.3em]">
                                <th className="px-10 py-6 border-b border-gray-50">Score</th>
                                <th className="px-10 py-6 border-b border-gray-50">Enterprise Entity</th>
                                <th className="px-10 py-6 border-b border-gray-50">Product</th>
                                <th className="px-10 py-6 border-b border-gray-50">Source</th>
                                <th className="px-10 py-6 border-b border-gray-50">Status</th>
                                <th className="px-10 py-6 border-b border-gray-50 text-right">Action</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-50">
                            {filteredLeads.map(lead => (
                                <tr key={lead.id} className="hover:bg-blue-50/20 transition-all text-sm group">
                                    <td className="px-10 py-6">
                                        <span className={`font-black text-sm ${getScoreTextColor(lead.confidence)}`}>
                                            {(lead.confidence * 100).toFixed(0)}%
                                        </span>
                                    </td>
                                    <td className="px-10 py-6">
                                        <div className="font-black text-gray-800 tracking-tight text-base mb-0.5">{lead.company}</div>
                                        <div className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">{lead.location}</div>
                                    </td>
                                    <td className="px-10 py-6">
                                        <span className="text-[10px] font-black text-hpcl-blue bg-hpcl-blue/5 px-4 py-1.5 rounded-full uppercase tracking-widest">
                                            {lead.primaryProduct}
                                        </span>
                                    </td>
                                    <td className="px-10 py-6 text-gray-400 text-[11px] font-bold italic">
                                        {lead.source}
                                    </td>
                                    <td className="px-10 py-6">
                                        <StatusBadge status={lead.status} />
                                    </td>
                                    <td className="px-10 py-6 text-right">
                                        <Link
                                            href={`/leads/${lead.id}`}
                                            className="bg-[#003366] text-white px-6 py-2.5 rounded-full font-black text-[10px] uppercase tracking-[.25em] hover:bg-hpcl-blue hover:shadow-xl transition-all active:scale-95 inline-block"
                                        >
                                            Analyze
                                        </Link>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

function StatusBadge({ status }) {
    switch (status) {
        case 'AUTO_ASSIGNED':
            return <span className="text-green-600 font-black text-[9px] bg-green-50 px-4 py-2 border border-green-100 rounded-full uppercase tracking-widest shadow-sm">Priority</span>;
        case 'QUALIFIED':
            return <span className="text-blue-600 font-black text-[9px] bg-blue-50 px-4 py-2 border border-blue-100 rounded-full uppercase tracking-widest shadow-sm">Qualified</span>;
        default:
            return <span className="text-amber-600 font-black text-[9px] bg-amber-50 px-4 py-2 border border-amber-100 rounded-full uppercase tracking-widest shadow-sm">Review</span>;
    }
}

function getScoreColor(score) {
    if (score >= 0.90) return 'bg-green-600 text-white';
    if (score >= 0.75) return 'bg-blue-600 text-white';
    return 'bg-amber-500 text-white';
}

function getScoreTextColor(score) {
    if (score >= 0.90) return 'text-green-600';
    if (score >= 0.75) return 'text-blue-600';
    return 'text-amber-600';
}

function getScoreHex(score) {
    if (score >= 0.90) return '#16a34a';
    if (score >= 0.75) return '#2563eb';
    return '#f59e0b';
}
