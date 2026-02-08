'use client';

import { useParams, useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { generateMockLeads } from '@/lib/intelligence/mockData';
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

    useEffect(() => {
        const allLeads = generateMockLeads(250);
        const foundLead = allLeads.find(l => l.id === id) || allLeads[0];
        setLead(foundLead);
    }, [id]);

    if (!lead) return <div className="p-10 text-center font-montserrat">Loading Lead Dossier...</div>;

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
                                    <span className={`px-2 py-0.5 rounded text-[10px] lg:text-sm font-black bg-white ${getScoreTextColor(lead.confidence)} uppercase shadow-sm`}>
                                        {(lead.confidence * 100).toFixed(0)}% Match
                                    </span>
                                    <span className="bg-[#DD0000] text-white text-[9px] lg:text-[10px] px-2 py-1 rounded font-black uppercase tracking-widest animate-pulse">High Priority</span>
                                </div>
                                <h1 className="text-2xl lg:text-4xl font-black mb-2 leading-tight tracking-tight uppercase">{lead.company}</h1>
                                <p className="text-blue-100 flex items-center gap-4 text-xs lg:text-sm font-bold opacity-80">
                                    <span className="flex items-center gap-1.5"><MapPin size={14} /> {lead.location}</span>
                                    <span className="flex items-center gap-1.5"><Building2 size={14} /> {lead.industry}</span>
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
                                        "{lead.company} is currently expanding its {lead.industry.toLowerCase()} facility in {lead.location}.
                                        Procurement triggers detected for {lead.primaryProduct} based equipment installation via {lead.source}."
                                    </p>
                                    <div className="flex items-center gap-4 text-[9px] font-black uppercase tracking-widest text-gray-400">
                                        <span>Origin: <span className="text-hpcl-blue">{lead.source}</span></span>
                                        <span>Sync: 08/02/26</span>
                                    </div>
                                </div>

                                <div className="space-y-3">
                                    <p className="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] mb-4">Verification Checkpoints:</p>
                                    {lead.reasonCodes.map((code, idx) => (
                                        <div key={idx} className="flex items-start gap-4 bg-white p-4 rounded-xl border border-gray-100 text-[11px] lg:text-xs group hover:border-hpcl-blue transition-all shadow-sm">
                                            <div className="text-green-600 bg-green-50 w-6 h-6 rounded-full flex items-center justify-center shrink-0">
                                                <ShieldCheck size={14} />
                                            </div>
                                            <span className="text-gray-700 font-bold pt-1">{code}</span>
                                        </div>
                                    ))}
                                </div>
                            </section>

                            <section>
                                <h3 className="text-[#0055A4] font-black uppercase text-[10px] lg:text-xs tracking-[0.25em] mb-6">Product Rec</h3>
                                <div className="flex items-center gap-5 p-5 border border-hpcl-blue/10 rounded-2xl bg-[#003366]/5 shadow-sm">
                                    <div className="w-14 h-14 bg-[#003366] rounded-2xl flex items-center justify-center text-white font-black text-xl shadow-lg shrink-0">
                                        {lead.primaryProduct.slice(0, 2)}
                                    </div>
                                    <div className="flex-1">
                                        <h4 className="font-black text-gray-800 text-sm lg:text-base uppercase tracking-tight">{lead.primaryProduct}</h4>
                                        <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest mt-0.5">Bulk Direct Supply</p>
                                    </div>
                                    <div className="hidden sm:block">
                                        <button className="text-[#DD0000] text-[10px] font-black uppercase tracking-widest border-b-2 border-[#DD0000]/20 hover:border-[#DD0000] transition-all">Specs</button>
                                    </div>
                                </div>
                            </section>
                        </div>

                        {/* Right Column: Actions & Feedback */}
                        <div className="bg-gray-50/30 p-6 lg:p-10 flex flex-col gap-10">
                            {/* Sales Officer Action */}
                            <div>
                                <h3 className="text-[#003366] font-black uppercase text-[10px] tracking-[0.2em] mb-6 opacity-60">Territory Officer</h3>
                                <div className="flex items-center gap-5 mb-8">
                                    <div className="w-14 h-14 rounded-2xl bg-gray-200 shadow-inner flex items-center justify-center text-xl grayscale">
                                        <User size={28} className="text-gray-400" />
                                    </div>
                                    <div>
                                        <p className="text-sm lg:text-base font-black text-gray-800 uppercase tracking-tight">Rajesh Kumar</p>
                                        <p className="text-[10px] text-hpcl-blue font-black uppercase tracking-widest">{lead.location} RO</p>
                                    </div>
                                </div>
                                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-3">
                                    <button className="bg-[#0055A4] text-white py-4 rounded-xl font-black text-[10px] uppercase tracking-[0.2em] hover:bg-[#003366] transition-all shadow-lg active:scale-95">Call Officer</button>
                                    <button className="bg-white border border-gray-200 text-gray-800 py-4 rounded-xl font-black text-[10px] uppercase tracking-[0.2em] hover:bg-gray-50 transition-all shadow-sm">Send Dispatch</button>
                                </div>
                            </div>

                            {/* Feedback Loop */}
                            <div className="mt-auto border-t border-gray-100 pt-10">
                                <h3 className="text-[#003366] font-black uppercase text-[10px] tracking-[0.2em] mb-6 opacity-60 text-center">Engine Feedback</h3>
                                {!feedback ? (
                                    <div className="flex flex-col gap-3">
                                        <button
                                            onClick={() => setFeedback('ACCEPTED')}
                                            className="w-full bg-green-600 text-white py-4 rounded-xl font-black text-[10px] uppercase tracking-[0.2em] hover:bg-green-700 transition-all shadow-lg active:scale-95 flex items-center justify-center gap-3"
                                        >
                                            Accept Intel
                                        </button>
                                        <button
                                            onClick={() => setFeedback('REJECTED')}
                                            className="w-full bg-white border border-red-100 text-red-600 py-4 rounded-xl font-black text-[10px] uppercase tracking-[0.2em] hover:bg-red-50 transition-all shadow-sm flex items-center justify-center gap-3"
                                        >
                                            Inaccurate
                                        </button>
                                    </div>
                                ) : (
                                    <div className={`p-6 rounded-2xl text-center text-[10px] font-black uppercase tracking-widest ${feedback === 'ACCEPTED' ? 'bg-green-100 text-green-700 border border-green-200' : 'bg-red-100 text-red-700 border border-red-200'}`}>
                                        {feedback === 'ACCEPTED' ? (
                                            <span className="flex items-center gap-2"><CheckCircle2 size={16} /> Data Logged</span>
                                        ) : (
                                            <span className="flex items-center gap-2"><XCircle size={16} /> Signal Rejected</span>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* WhatsApp Simulation Overlay */}
                {lead.status === 'AUTO_ASSIGNED' && (
                    <div className="mt-8 bg-green-50 border border-green-100 rounded-3xl p-6 lg:p-8 flex flex-col sm:flex-row gap-5 items-center">
                        <div className="bg-green-600 w-14 h-14 rounded-2xl flex items-center justify-center text-white text-2xl shadow-xl shrink-0">
                            <Phone size={24} />
                        </div>
                        <div className="text-center sm:text-left">
                            <p className="text-[10px] font-black text-green-700 uppercase tracking-[0.2em] mb-1">Instant Notification Sent</p>
                            <p className="text-xs lg:text-sm text-green-800 font-bold leading-snug">WhatsApp alert transmitted to Field Officer for immediate site visit.</p>
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
