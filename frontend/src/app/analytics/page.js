'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getDashboardStats } from '@/lib/services/dashboardService';
import { authStore } from '@/lib/stores/authStore';
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
    const router = useRouter();
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        if (!authStore.isAuthenticated()) {
            router.push('/login');
            return;
        }

        fetchStats();
    }, [router]);

    const fetchStats = async () => {
        setLoading(true);
        setError('');

        try {
            const data = await getDashboardStats();
            setStats(data);
        } catch (err) {
            console.error('Failed to fetch analytics:', err);
            setError(err.message || 'Failed to load analytics');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="bg-gray-50 min-h-screen flex items-center justify-center font-montserrat">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-hpcl-blue mx-auto mb-4"></div>
                    <p className="text-gray-600 font-bold">Loading Analytics...</p>
                </div>
            </div>
        );
    }

    if (!stats) {
        return (
            <div className="bg-gray-50 min-h-screen flex items-center justify-center font-montserrat p-4">
                <div className="bg-white rounded-2xl p-8 shadow-xl max-w-md w-full">
                    <div className="text-red-600 text-center">
                        <p className="text-lg font-bold mb-2">No Analytics Data</p>
                        <p className="text-sm">{error || 'No data available'}</p>
                    </div>
                </div>
            </div>
        );
    }

    // Data Mapping from API Response
    const totalLeads = stats.summary?.totalLeads || 0;
    const qualifiedLeads = (stats.byStatus?.QUALIFIED || 0) + (stats.byStatus?.REVIEW_REQUIRED || 0);
    const acceptedLeads = stats.byStatus?.ACCEPTED || 0;
    const convertedLeads = stats.byStatus?.CONVERTED || 0;

    const conversionRate = totalLeads > 0 ? ((convertedLeads / totalLeads) * 100).toFixed(1) : 0;
    const acceptanceRate = totalLeads > 0 ? ((acceptedLeads / totalLeads) * 100).toFixed(1) : 0;

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
                        <button className="px-4 py-2 bg-hpcl-blue text-white text-[10px] font-black rounded-xl shadow-md uppercase tracking-widest">Live Data</button>
                        <button className="px-4 py-2 text-gray-400 text-[10px] font-black rounded-xl uppercase tracking-widest hover:bg-gray-50">Historical</button>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-10">
                    {/* Hero Stat: Conversion Funnel */}
                    <div className="lg:col-span-2 bg-white rounded-[2.5rem] p-8 lg:p-10 shadow-xl border border-gray-100">
                        <div className="flex justify-between items-center mb-10">
                            <h2 className="text-[#003366] text-xs lg:text-sm font-black uppercase tracking-[0.25em]">Lead Conversion Funnel</h2>
                            <Target className="text-hpcl-blue" size={28} />
                        </div>

                        <div className="space-y-8">
                            <FunnelStage label="Detected" count={totalLeads} percentage={100} color="blue" />
                            <FunnelStage label="Qualified" count={qualifiedLeads} percentage={(qualifiedLeads / totalLeads) * 100} color="green" />
                            <FunnelStage label="Accepted" count={acceptedLeads} percentage={acceptanceRate} color="amber" />
                            <FunnelStage label="Converted" count={convertedLeads} percentage={conversionRate} color="purple" trend={`${conversionRate}%`} />
                        </div>
                    </div>

                    {/* Revenue Projection */}
                    <div className="bg-gradient-to-br from-[#003366] to-[#0055A4] rounded-[2.5rem] p-8 text-white shadow-2xl flex flex-col justify-between relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-48 h-48 bg-white/5 rounded-full -mr-24 -mt-24"></div>
                        <div className="relative z-10">
                            <p className="text-blue-100 text-[9px] font-black uppercase tracking-[0.2em] mb-4 opacity-70">Pipeline Value</p>
                            <h3 className="text-4xl lg:text-5xl font-black mb-2 tabular-nums tracking-tight">₹{(stats.summary?.estimatedValue || 0).toFixed(1)}Cr</h3>
                            <p className="text-[10px] text-blue-100 font-bold uppercase tracking-widest opacity-60">Estimated potential</p>
                        </div>
                        <div className="relative z-10 mt-10">
                            <div className="flex items-center gap-3 text-sm font-black">
                                <span className="bg-green-400 text-green-900 px-3 py-1 rounded-full text-[10px] uppercase tracking-widest shadow-lg">+{conversionRate}%</span>
                                <span className="text-blue-100 text-xs opacity-80">vs. target</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Product Demand Mix */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div className="bg-white rounded-[2.5rem] p-8 lg:p-10 shadow-xl border border-gray-100">
                        <div className="flex justify-between items-center mb-8">
                            <h2 className="text-[#003366] text-xs lg:text-sm font-black uppercase tracking-[0.25em]">Signal Types</h2>
                            <PieChart className="text-hpcl-blue" size={24} />
                        </div>

                        <div className="space-y-5">
                            {Object.entries(stats.byCategory || {}).map(([type, count]) => (
                                <div key={type}>
                                    <div className="flex justify-between text-xs mb-2">
                                        <span className="font-black text-gray-700 uppercase">{type}</span>
                                        <span className="text-gray-400 font-bold">{count}</span>
                                    </div>
                                    <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                                        <div
                                            className="bg-gradient-to-r from-hpcl-blue to-[#0055A4] h-full transition-all duration-1000 ease-out"
                                            style={{ width: `${(count / totalLeads) * 100}%` }}
                                        ></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="bg-white rounded-[2.5rem] p-8 lg:p-10 shadow-xl border border-gray-100">
                        <div className="flex justify-between items-center mb-8">
                            <h2 className="text-[#003366] text-xs lg:text-sm font-black uppercase tracking-[0.25em]">Confidence Distribution</h2>
                            <BarChart3 className="text-hpcl-blue" size={24} />
                        </div>

                        <div className="space-y-5">
                            {Object.entries(stats.byConfidence || {}).map(([level, count]) => (
                                <div key={level}>
                                    <div className="flex justify-between text-xs mb-2">
                                        <span className="font-black text-gray-700 uppercase">{level}</span>
                                        <span className="text-gray-400 font-bold">{count}</span>
                                    </div>
                                    <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                                        <div
                                            className={`h-full transition-all duration-1000 ease-out ${getConfidenceColor(level)}`}
                                            style={{ width: `${(count / totalLeads) * 100}%` }}
                                        ></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function FunnelStage({ label, count, percentage, color, trend }) {
    return (
        <div className="relative">
            <div className="flex justify-between items-center mb-3">
                <span className="text-xs lg:text-sm font-black text-gray-800 uppercase tracking-tight">{label}</span>
                <div className="flex items-center gap-4">
                    {trend && (
                        <span className="text-green-600 text-xs font-black flex items-center gap-1">
                            <TrendingUp size={14} /> {trend}
                        </span>
                    )}
                    <span className="text-lg lg:text-2xl font-black text-gray-900 tabular-nums">{count}</span>
                </div>
            </div>
            <div className="w-full bg-gray-100 h-4 rounded-full overflow-hidden shadow-inner">
                <div
                    className={`h-full ${getColorClass(color)} transition-all duration-1000 ease-out`}
                    style={{ width: `${percentage}%` }}
                ></div>
            </div>
        </div>
    );
}

function getColorClass(color) {
    const colorMap = {
        blue: 'bg-gradient-to-r from-blue-500 to-blue-600',
        green: 'bg-gradient-to-r from-green-500 to-green-600',
        amber: 'bg-gradient-to-r from-amber-500 to-amber-600',
        purple: 'bg-gradient-to-r from-purple-500 to-purple-600'
    };
    return colorMap[color] || 'bg-gray-500';
}

function getConfidenceColor(level) {
    const colorMap = {
        high: 'bg-gradient-to-r from-green-500 to-green-600',
        medium: 'bg-gradient-to-r from-blue-500 to-blue-600',
        low: 'bg-gradient-to-r from-amber-500 to-amber-600'
    };
    return colorMap[level?.toLowerCase()] || 'bg-gray-500';
}
