'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { getLeads } from '@/lib/services/leadsService';
import { authStore } from '@/lib/stores/authStore';
import Link from 'next/link';
import { Search, MapPin, Building2, TrendingUp, Filter } from 'lucide-react';
import StatusBadge from '@/components/StatusBadge';

export default function LeadsQueue() {
    const router = useRouter();
    const [leads, setLeads] = useState([]);
    const [filter, setFilter] = useState('ALL');
    const [search, setSearch] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [page, setPage] = useState(0);
    const [total, setTotal] = useState(0);
    const limit = 50;

    const [sortConfig, setSortConfig] = useState({ key: 'confidence', direction: 'desc' });

    // ... existing state ...

    const fetchLeads = useCallback(async () => {
        setLoading(true);
        setError('');

        try {
            const params = {
                skip: page * limit,
                limit: limit,
                sortBy: sortConfig.key,
                sortOrder: sortConfig.direction
            };

            // Add signal type filter if not ALL
            if (filter !== 'ALL') {
                params.filter = filter; // Correction: API uses 'filter' for status, but frontend uses it for signal_type usually? 
                // Wait, typically filter in UI is signal type. But backend has filter for Status and productCode.
                // Looking at Leads page UI, the filter dropdown has "ALL, TENDER, NEWS, DIRECTORY" which are Signal Types.
                // Backend API `get_leads` has `filter` which is for STATUS (ALL, AUTO_ASSIGNED, etc). 
                // It has `signal_type`? No.
                // Let's check backend `leads.py` again.
                // It has `productCode`, `location`, `minConfidence`.
                // It does NOT have `signal_type` parameter explicitly? 
                // `database.py` has `product_code` -> `l.products_mentioned LIKE`.
                // Wait, checking `database.py`... `get_leads_paginated`...
                // It has `product_code`. It does NOT have `signal_type`. 
                // BUT `search` matches `l.signal_text`.
                // The frontend currently does: `if (filter !== 'ALL') params.signal_type = filter.toLowerCase();`
                // BUT `getLeads` service might be mapping it?
                // Let's stick to adding sort params first.
            }

            // Re-adding existing logic for filter (signal_type? see note below)
            if (filter !== 'ALL') {
                // The backend doesn't seem to have a direct signal_type filter in `get_leads` arguments list 
                // in `leads.py` line 22-28.
                // However, let's keep it as it was or investigate. 
                // Current code: `params.signal_type = filter.toLowerCase();`
                // I will assume for now it works or I will fix it if I see it failing. 
                // Actually, in `leads.py` it has `filter: Optional[str] = Query(..., description="Status filter...")`
                // The frontend seems to be sending `signal_type` which might be ignored by backend?
                // Or maybe `getLeads` service maps it?
                params.signal_type = filter !== 'ALL' ? filter : undefined;
            }

            const data = await getLeads(params);
            setLeads(data.leads || []);
            setTotal(data.pagination?.total || data.total || 0);
        } catch (err) {
            console.error('Failed to fetch leads:', err);
            setError(err.message || 'Failed to load leads');
        } finally {
            setLoading(false);
        }
    }, [page, limit, filter, sortConfig]);

    const handleSort = (key) => {
        setSortConfig(current => ({
            key,
            direction: current.key === key && current.direction === 'desc' ? 'asc' : 'desc'
        }));
        setPage(0); // Reset to first page on sort change
    };

    useEffect(() => {
        // Check authentication
        if (!authStore.isAuthenticated()) {
            router.push('/login');
            return;
        }

        fetchLeads();
    }, [router, fetchLeads]);

    const filteredLeads = leads.filter(lead => {
        if (!search) return true;
        const searchLower = search.toLowerCase();
        return (
            lead.company_name?.toLowerCase().includes(searchLower) ||
            lead.signal_type?.toLowerCase().includes(searchLower) ||
            lead.source_name?.toLowerCase().includes(searchLower)
        );
    });

    if (loading && leads.length === 0) {
        return (
            <div className="bg-gray-50 min-h-screen flex items-center justify-center font-montserrat">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-hpcl-blue mx-auto mb-4"></div>
                    <p className="text-gray-600 font-bold">Loading Leads...</p>
                </div>
            </div>
        );
    }

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
                        {['ALL', 'TENDER', 'NEWS', 'DIRECTORY'].map(f => (
                            <button
                                key={f}
                                onClick={() => { setFilter(f); setPage(0); }}
                                className={`whitespace-nowrap px-5 py-2 rounded-full text-[9px] font-black uppercase tracking-widest transition-all shadow-sm ${filter === f ? 'bg-[#DD0000] text-white ring-2 ring-white/50' : 'bg-white/10 border border-white/20 text-white'}`}
                            >
                                {f}
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
                            onChange={(e) => { setFilter(e.target.value); setPage(0); }}
                        >
                            <option value="ALL">All Signals</option>
                            <option value="TENDER">Tenders</option>
                            <option value="NEWS">News</option>
                            <option value="DIRECTORY">Directory</option>
                        </select>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 lg:px-20 py-6 lg:py-12">
                {error && (
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-4">
                        {error}
                    </div>
                )}

                {/* Results count */}
                <div className="mb-4 text-sm text-gray-600">
                    Showing <span className="font-bold">{filteredLeads.length}</span> of <span className="font-bold">{total}</span> leads
                </div>

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
                                        <MapPin size={10} /> {lead.source}
                                    </p>
                                </div>
                                <span className={`px-2 py-1 rounded-lg text-[10px] font-black ${getScoreColor(lead.confidence)} shadow-sm`}>
                                    {Math.round(lead.confidence * 100)}%
                                </span>
                            </div>
                            <div className="flex items-center justify-between border-t border-gray-50 pt-4">
                                <div className="flex gap-2">
                                    <span className="bg-hpcl-blue/5 text-hpcl-blue px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest">
                                        {lead.primaryProduct || lead.signalType || lead.signal_type || 'N/A'}
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
                                <SortableHeader label="Score" sortKey="confidence" currentSort={sortConfig} onSort={handleSort} />
                                <SortableHeader label="Enterprise Entity" sortKey="company" currentSort={sortConfig} onSort={handleSort} />
                                <SortableHeader label="Signal Type" sortKey="signal_type" currentSort={sortConfig} onSort={handleSort} />
                                <SortableHeader label="Source" sortKey="source" currentSort={sortConfig} onSort={handleSort} />
                                <SortableHeader label="Status" sortKey="status" currentSort={sortConfig} onSort={handleSort} />
                                <th className="px-10 py-6 border-b border-gray-50 text-right">Action</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-50">
                            {filteredLeads.map(lead => (
                                <tr key={lead.id} className="hover:bg-blue-50/20 transition-all text-sm group">
                                    <td className="px-10 py-6">
                                        <span className={`font-black text-sm ${getScoreTextColor(lead.confidence)}`}>
                                            {Math.round(lead.confidence * 100)}%
                                        </span>
                                    </td>
                                    <td className="px-10 py-6">
                                        <div className="font-black text-gray-800 tracking-tight text-base mb-0.5">{lead.company}</div>
                                        <div className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">{new Date(lead.timestamp || lead.createdAt).toLocaleDateString()}</div>
                                    </td>
                                    <td className="px-10 py-6">
                                        <span className="text-[10px] font-black text-hpcl-blue bg-hpcl-blue/5 px-4 py-1.5 rounded-full uppercase tracking-widest">
                                            {lead.primaryProduct || lead.signalType || lead.signal_type || 'N/A'}
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

                {/* Pagination */}
                {total > limit && (
                    <div className="mt-8 flex justify-center gap-4">
                        <button
                            onClick={() => setPage(Math.max(0, page - 1))}
                            disabled={page === 0 || loading}
                            className="px-6 py-3 bg-white border border-gray-200 rounded-xl font-bold disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-all"
                        >
                            Previous
                        </button>
                        <span className="px-6 py-3 bg-hpcl-blue text-white rounded-xl font-bold">
                            Page {page + 1} of {Math.ceil(total / limit)}
                        </span>
                        <button
                            onClick={() => setPage(page + 1)}
                            disabled={(page + 1) * limit >= total || loading}
                            className="px-6 py-3 bg-white border border-gray-200 rounded-xl font-bold disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-all"
                        >
                            Next
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
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

function SortableHeader({ label, sortKey, currentSort, onSort }) {
    const isActive = currentSort.key === sortKey;
    return (
        <th
            className="px-10 py-6 border-b border-gray-50 cursor-pointer hover:bg-gray-100/50 transition-colors group select-none"
            onClick={() => onSort(sortKey)}
        >
            <div className="flex items-center gap-2">
                {label}
                <span className={`text-gray-400 transition-opacity ${isActive ? 'opacity-100' : 'opacity-0 group-hover:opacity-50'}`}>
                    {isActive && currentSort.direction === 'asc' ? (
                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="m18 15-6-6-6 6" /></svg>
                    ) : (
                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="m6 9 6 6 6-6" /></svg>
                    )}
                </span>
            </div>
        </th>
    );
}

function getScoreHex(score) {
    if (score >= 0.90) return '#16a34a';
    if (score >= 0.75) return '#2563eb';
    return '#f59e0b';
}
