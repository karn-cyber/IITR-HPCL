'use client';

import { useParams, useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { getLeadById, addLeadAction } from '@/lib/services/leadsService';
import { authStore } from '@/lib/stores/authStore';
import Link from 'next/link';
import {
    ArrowLeft,
    ShieldCheck,
    MapPin,
    Building2,
    Phone,
    Share2,
    AlertCircle,
    CheckCircle2,
    User,
    ChevronRight,
    XCircle
} from 'lucide-react';

export default function LeadDossier() {
    const { id } = useParams();
    const router = useRouter();
    const [lead, setLead] = useState(null);
    const [feedback, setFeedback] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [actionLoading, setActionLoading] = useState(false);

    useEffect(() => {
        // Check authentication
        if (!authStore.isAuthenticated()) {
            router.push('/login');
            return;
        }

        fetchLeadDetails();
    }, [id, router]);

    const fetchLeadDetails = async () => {
        setLoading(true);
        setError('');

        try {
            const leadData = await getLeadById(id);
            setLead(leadData);

            // Set feedback state based on current status
            if (leadData.assignment?.status === 'ACCEPTED' || leadData.assignment?.status === 'CONVERTED') {
                setFeedback('ACCEPTED');
            } else if (leadData.assignment?.status === 'REJECTED') {
                setFeedback('REJECTED');
            } else {
                setFeedback(null);
            }
        } catch (err) {
            console.error('Failed to fetch lead details:', err);
            setError(err.message || 'Failed to load lead details');
        } finally {
            setLoading(false);
        }
    };

    const handleAction = async (actionType) => {
        setActionLoading(true);
        try {
            await addLeadAction(id, {
                action: actionType,
                notes: `${actionType} from lead dossier`
            });
            // Map action verb to status state (ACCEPT -> ACCEPTED)
            const statusMap = {
                'ACCEPT': 'ACCEPTED',
                'REJECT': 'REJECTED',
                'CONVERT': 'CONVERTED'
            };
            setFeedback(statusMap[actionType] || actionType);

            // Refresh lead data
            await fetchLeadDetails();
        } catch (err) {
            console.error('Failed to add action:', err);
            alert('Failed to submit action: ' + err.message);
        } finally {
            setActionLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="bg-gray-50 min-h-screen flex items-center justify-center font-montserrat">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-hpcl-blue mx-auto mb-4"></div>
                    <p className="text-gray-600 font-bold">Loading Lead Dossier...</p>
                </div>
            </div>
        );
    }

    if (error || !lead) {
        return (
            <div className="bg-gray-50 min-h-screen flex items-center justify-center font-montserrat p-4">
                <div className="bg-white rounded-2xl p-8 shadow-xl max-w-md w-full">
                    <div className="text-red-600 text-center mb-4">
                        <p className="text-lg font-bold mb-2">Error Loading Lead</p>
                        <p className="text-sm">{error || 'Lead not found'}</p>
                    </div>
                    <Link
                        href="/leads"
                        className="block w-full bg-hpcl-blue text-white py-3 rounded-xl font-bold text-center hover:bg-opacity-90 transition-all"
                    >
                        Back to Leads
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-gray-50 min-h-screen p-4 lg:p-10 font-montserrat pb-24 lg:pb-10">
            <div className="max-w-5xl mx-auto">
                {/* Breadcrumb & Navigation */}
                <div className="flex justify-between items-center mb-6">
                    <Link href="/leads" className="text-hpcl-blue text-[10px] lg:text-sm font-black uppercase tracking-widest hover:underline flex items-center gap-2">
                        <ArrowLeft size={16} /> Queue
                    </Link>
                    <div className="flex gap-2">
                        <span className="text-[10px] text-gray-400 font-bold">ID: {lead.id}</span>
                    </div>
                </div>

                {/* Main Dossier Card */}
                <div className="bg-white rounded-3xl shadow-xl border border-gray-100 overflow-hidden">
                    {/* Header Section */}
                    <div className="bg-[#003366] text-white p-6 lg:p-10">
                        <div className="flex flex-col md:flex-row justify-between items-start lg:items-center gap-6">
                            <div className="w-full md:w-auto">
                                <div className="flex flex-wrap items-center gap-2 lg:gap-3 mb-3">
                                    <span className={`px-2 py-0.5 rounded text-[10px] lg:text-sm font-black bg-white ${getScoreTextColor(lead.scoring?.finalScore || lead.confidence)} uppercase shadow-sm`}>
                                        {Math.round((lead.scoring?.finalScore || lead.confidence || 0) * 100)}% Match
                                    </span>
                                    {(lead.scoring?.finalScore || lead.confidence) >= 0.9 && (
                                        <span className="bg-[#DD0000] text-white text-[9px] lg:text-[10px] px-2 py-1 rounded font-black uppercase tracking-widest animate-pulse">High Priority</span>
                                    )}
                                </div>
                                <h1 className="text-2xl lg:text-4xl font-black mb-2 leading-tight tracking-tight uppercase">{lead.company?.name || lead.company}</h1>
                                <p className="text-blue-100 flex items-center gap-4 text-xs lg:text-sm font-bold opacity-80">
                                    <span className="flex items-center gap-1.5"><MapPin size={14} /> {lead.company?.location || lead.location || lead.signal?.source || lead.source}</span>
                                    <span className="flex items-center gap-1.5"><Building2 size={14} /> {lead.company?.industry || lead.industry || lead.primaryProduct}</span>
                                </p>
                            </div>
                            <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
                                <button className="flex-1 bg-white/10 hover:bg-white/20 border border-white/20 px-6 py-3 rounded-xl font-black text-[10px] uppercase tracking-widest transition-all">Report</button>
                                <button className="flex-1 bg-[#DD0000] hover:bg-[#b20000] px-8 py-3 rounded-xl font-black text-[10px] uppercase tracking-[0.2em] shadow-lg transition-all active:scale-95">Share</button>
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 divide-y lg:divide-y-0 lg:divide-x divide-gray-100">
                        {/* Left Column: Intelligence Proof */}
                        <div className="lg:col-span-2 p-6 lg:p-10">
                            <section className="mb-10">
                                <h3 className="text-[#0055A4] font-black uppercase text-[10px] lg:text-xs tracking-[0.25em] mb-6 flex items-center gap-3">
                                    <span className="w-1.5 h-4 bg-[#DD0000]"></span>
                                    Signal Evidence
                                </h3>
                                <div className="bg-gray-50 rounded-2xl p-6 border border-gray-100 mb-8 shadow-inner relative">
                                    <span className="absolute -top-3 left-6 bg-white border border-gray-100 px-3 py-1 rounded text-[10px] font-black text-hpcl-blue uppercase tracking-widest">Logic Extract</span>
                                    <p className="text-gray-700 text-xs lg:text-sm leading-relaxed italic mb-4 font-medium pt-2">
                                        "{lead.signal?.rawText || lead.signal_text || `Signal detected from ${lead.signal?.source || lead.source} indicating potential interest in HPCL products.`}"
                                    </p>
                                    <div className="flex items-center gap-4 text-[9px] font-black uppercase tracking-widest text-gray-400">
                                        <span>Origin: <span className="text-hpcl-blue">{lead.signal?.source || lead.source}</span></span>
                                        <span>Sync: {new Date(lead.signal?.detectedAt || lead.timestamp || lead.createdAt).toLocaleDateString()}</span>
                                    </div>
                                </div>

                                <div className="space-y-3">
                                    <p className="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] mb-4">Verification Checkpoints:</p>
                                    <div className="flex items-start gap-4 bg-white p-4 rounded-xl border border-gray-100 text-[11px] lg:text-xs group hover:border-hpcl-blue transition-all shadow-sm">
                                        <div className="text-green-600 bg-green-50 w-6 h-6 rounded-full flex items-center justify-center shrink-0">
                                            <ShieldCheck size={14} />
                                        </div>
                                        <span className="text-gray-700 font-bold pt-1">Product: {lead.primaryProduct || (lead.products && lead.products[0]?.code) || lead.signalType || lead.signal_type || 'N/A'}</span>
                                    </div>
                                    <div className="flex items-start gap-4 bg-white p-4 rounded-xl border border-gray-100 text-[11px] lg:text-xs group hover:border-hpcl-blue transition-all shadow-sm">
                                        <div className="text-green-600 bg-green-50 w-6 h-6 rounded-full flex items-center justify-center shrink-0">
                                            <ShieldCheck size={14} />
                                        </div>
                                        <span className="text-gray-700 font-bold pt-1">Confidence Score: {lead.scoring?.finalScore !== undefined ? Math.round(lead.scoring.finalScore * 100) : 0}%</span>
                                    </div>
                                    <div className="flex items-start gap-4 bg-white p-4 rounded-xl border border-gray-100 text-[11px] lg:text-xs group hover:border-hpcl-blue transition-all shadow-sm">
                                        <div className="text-green-600 bg-green-50 w-6 h-6 rounded-full flex items-center justify-center shrink-0">
                                            <ShieldCheck size={14} />
                                        </div>
                                        <span className="text-gray-700 font-bold pt-1">Source Verified: {lead.signal?.source || lead.source}</span>
                                    </div>
                                </div>
                            </section>

                            <section>
                                <h3 className="text-[#0055A4] font-black uppercase text-[10px] lg:text-xs tracking-[0.25em] mb-6">Signal Category</h3>
                                <div className="flex items-center gap-5 p-5 border border-hpcl-blue/10 rounded-2xl bg-[#003366]/5 shadow-sm">
                                    <div className="w-14 h-14 bg-[#003366] rounded-2xl flex items-center justify-center text-white font-black text-xl shadow-lg shrink-0">
                                        {(lead.primaryProduct || (lead.products && lead.products[0]?.code) || lead.signalType || lead.signal_type || 'NA').slice(0, 2).toUpperCase()}
                                    </div>
                                    <div className="flex-1">
                                        <h4 className="font-black text-gray-800 text-sm lg:text-base uppercase tracking-tight">{lead.primaryProduct || (lead.products && lead.products[0]?.code) || lead.signalType || lead.signal_type || 'N/A'}</h4>
                                        <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest mt-0.5">Product Intelligence Signal</p>
                                    </div>
                                </div>
                            </section>
                        </div>

                        {/* Right Column: Actions & Feedback */}
                        <div className="bg-gray-50/30 p-6 lg:p-10 flex flex-col gap-10">
                            {/* Sales Officer Action */}
                            <div>
                                <h3 className="text-[#003366] font-black uppercase text-[10px] tracking-[0.2em] mb-6 opacity-60">Actions</h3>
                                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-3">
                                    <button
                                        onClick={() => router.push('/leads')}
                                        className="bg-[#0055A4] text-white py-4 rounded-xl font-black text-[10px] uppercase tracking-[0.2em] hover:bg-[#003366] transition-all shadow-lg active:scale-95"
                                    >
                                        Back to Queue
                                    </button>
                                    <button className="bg-white border border-gray-200 text-gray-800 py-4 rounded-xl font-black text-[10px] uppercase tracking-[0.2em] hover:bg-gray-50 transition-all shadow-sm">
                                        View Details
                                    </button>
                                </div>
                            </div>

                            {/* Feedback Loop */}
                            <div className="mt-auto border-t border-gray-100 pt-10">
                                <h3 className="text-[#003366] font-black uppercase text-[10px] tracking-[0.2em] mb-6 opacity-60 text-center">Engine Feedback</h3>
                                {!feedback ? (
                                    <div className="flex flex-col gap-3">
                                        <button
                                            onClick={() => handleAction('ACCEPT')}
                                            disabled={actionLoading}
                                            className="w-full bg-green-600 text-white py-4 rounded-xl font-black text-[10px] uppercase tracking-[0.2em] hover:bg-green-700 transition-all shadow-lg active:scale-95 flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
                                        >
                                            {actionLoading ? 'Processing...' : 'Accept Intel'}
                                        </button>
                                        <button
                                            onClick={() => handleAction('REJECT')}
                                            disabled={actionLoading}
                                            className="w-full bg-white border border-red-100 text-red-600 py-4 rounded-xl font-black text-[10px] uppercase tracking-[0.2em] hover:bg-red-50 transition-all shadow-sm flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
                                        >
                                            {actionLoading ? 'Processing...' : 'Inaccurate'}
                                        </button>
                                    </div>
                                ) : (
                                    <div className={`p-6 rounded-2xl text-center text-[10px] font-black uppercase tracking-widest ${feedback === 'ACCEPTED' ? 'bg-green-100 text-green-700 border border-green-200' : 'bg-red-100 text-red-700 border border-red-200'}`}>
                                        {feedback === 'ACCEPTED' ? (
                                            <span className="flex items-center gap-2 justify-center"><CheckCircle2 size={16} /> Data Logged</span>
                                        ) : (
                                            <span className="flex items-center gap-2 justify-center"><XCircle size={16} /> Signal Rejected</span>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* WhatsApp Simulation Overlay */}
                {lead.confidence >= 0.9 && (
                    <div className="mt-8 bg-green-50 border border-green-100 rounded-3xl p-6 lg:p-8 flex flex-col sm:flex-row gap-5 items-center">
                        <div className="bg-green-600 w-14 h-14 rounded-2xl flex items-center justify-center text-white text-2xl shadow-xl shrink-0">
                            <Phone size={24} />
                        </div>
                        <div className="text-center sm:text-left">
                            <p className="text-[10px] font-black text-green-700 uppercase tracking-[0.2em] mb-1">High Priority Lead</p>
                            <p className="text-xs lg:text-sm text-green-800 font-bold leading-snug">This lead qualifies for immediate notification to field officers.</p>
                        </div>
                        <button className="sm:ml-auto text-green-600 text-[10px] font-black uppercase tracking-widest border-b border-green-200">View Log</button>
                    </div>
                )}
            </div>
        </div>
    );
}

function getScoreTextColor(score) {
    if (score >= 0.90) return 'text-green-600';
    if (score >= 0.75) return 'text-blue-600';
    return 'text-amber-600';
}
