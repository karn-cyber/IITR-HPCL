'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { getLeads } from '@/lib/services/leadsService';
import { getDashboardStats } from '@/lib/services/dashboardService';
import { authStore } from '@/lib/stores/authStore';
import Link from 'next/link';
import {
  Search,
  Zap,
  CheckCircle2,
  IndianRupee,
  ArrowRight,
  TrendingUp,
  Globe,
  LogOut
} from 'lucide-react';
import StatusBadge from '@/components/StatusBadge';

export default function Dashboard() {
  const router = useRouter();
  const [leads, setLeads] = useState([]);
  const [stats, setStats] = useState({
    total_leads: 0,
    new_leads: 0,
    accepted_leads: 0,
    converted_leads: 0,
    total_companies: 0,
    leads_by_type: {},
    leads_by_confidence: {}
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [timeFilter, setTimeFilter] = useState('7d'); // Default to 7 days

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError('');

    try {
      // Fetch leads and dashboard stats in parallel
      const [leadsData, statsData] = await Promise.all([
        getLeads({ limit: 50, skip: 0 }),
        getDashboardStats({ dateRange: timeFilter })
      ]);

      setLeads(leadsData.leads || []);
      setStats(statsData);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  }, [timeFilter]);

  useEffect(() => {
    // Check authentication
    if (!authStore.isAuthenticated()) {
      router.push('/login');
      return;
    }

    fetchData();
  }, [router, fetchData]); // Refetch when fetchData changes

  const handleLogout = async () => {
    await authStore.logout();
    router.push('/login');
  };

  if (loading) {
    return (
      <div className="bg-gray-50 min-h-screen flex items-center justify-center font-montserrat">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-hpcl-blue mx-auto mb-4"></div>
          <p className="text-gray-600 font-bold">Loading Dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-50 min-h-screen flex items-center justify-center font-montserrat p-4">
        <div className="bg-white rounded-2xl p-8 shadow-xl max-w-md w-full">
          <div className="text-red-600 text-center mb-4">
            <p className="text-lg font-bold mb-2">Error Loading Dashboard</p>
            <p className="text-sm">{error}</p>
          </div>
          <button
            onClick={fetchData}
            className="w-full bg-hpcl-blue text-white py-3 rounded-xl font-bold hover:bg-opacity-90 transition-all"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const highConfidence = stats.summary?.highConfidence || 0;
  const autoAssigned = stats.summary?.autoAssigned || 0;
  const totalCompanies = stats.byCategory ? Object.keys(stats.byCategory).length : 0;

  return (
    <div className="bg-gray-50 min-h-screen p-4 lg:p-10 font-montserrat pb-24 lg:pb-10">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 lg:mb-8 gap-4">
          <div>
            <h1 className="text-xl lg:text-3xl font-bold text-[#0055A4] flex items-center gap-3">
              <span className="w-1.5 h-6 lg:w-2 lg:h-8 bg-[#DD0000]"></span>
              Lead Dashboard
            </h1>
            <p className="text-gray-500 text-[10px] lg:text-[14px] mt-1 font-bold uppercase tracking-widest opacity-70">B2B Intel System</p>
          </div>
          <div className="flex gap-2">
            <div className="bg-white p-1 rounded-lg shadow-sm border border-gray-200 flex">
              {[
                { label: '7 Days', value: '7d' },
                { label: '30 Days', value: '30d' },
                { label: 'All Time', value: 'all' }
              ].map((filter) => (
                <button
                  key={filter.value}
                  onClick={() => setTimeFilter(filter.value)}
                  className={`px-4 py-1.5 text-[10px] lg:text-xs font-bold rounded shadow-sm uppercase tracking-widest transition-colors ${timeFilter === filter.value
                    ? 'bg-[#0055A4] text-white'
                    : 'text-gray-400 hover:bg-gray-100 bg-white'
                    }`}
                >
                  {filter.label}
                </button>
              ))}
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-1.5 text-[10px] lg:text-xs font-bold text-red-600 hover:bg-red-50 transition-colors uppercase tracking-widest rounded flex items-center gap-2"
            >
              <LogOut size={14} />
              Logout
            </button>
          </div>
        </div>

        {/* Stats Grid - Responsive Cols */}
        <div className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6 mb-8 lg:mb-10">
          <StatCard title="Detected" value={stats.summary?.totalLeads || 0} color="border-hpcl-blue" icon={<Search size={24} className="text-hpcl-blue" />} />
          <StatCard title="High Intent" value={highConfidence} color="border-hpcl-red" icon={<Zap size={24} className="text-hpcl-red" />} />
          <StatCard title="Assigned" value={autoAssigned} color="border-green-600" icon={<CheckCircle2 size={24} className="text-green-600" />} />
          <StatCard title="Companies" value={totalCompanies} color="border-amber-500" icon={<Globe size={24} className="text-amber-500" />} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8">
          {/* Recent High-Intent Leads */}
          <div className="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="bg-gray-50 px-5 py-4 border-b border-gray-200 flex justify-between items-center">
              <h2 className="font-bold text-[#003366] uppercase tracking-widest text-[11px] lg:text-sm">Priority Queue</h2>
              <Link href="/leads" className="text-[10px] lg:text-xs text-hpcl-blue hover:underline font-bold uppercase tracking-tighter flex items-center gap-1">
                View All <ArrowRight size={12} />
              </Link>
            </div>
            <div className="divide-y divide-gray-100">
              {leads.slice(0, 8).map(lead => (
                <Link key={lead.id} href={`/leads/${lead.id}`} className="block px-5 py-4 hover:bg-blue-50/30 transition-colors group">
                  <div className="flex justify-between items-start mb-1">
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-black ${getScoreColor(lead.confidence)} shadow-sm`}>
                        {Math.round(lead.confidence * 100)}%
                      </span>
                      <h3 className="font-bold text-gray-800 text-sm lg:text-base leading-none tracking-tight truncate max-w-[140px] sm:max-w-none">{lead.company}</h3>
                    </div>
                    <span className="text-[10px] text-gray-400 font-bold">{timeAgo(lead.timestamp || lead.createdAt)}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex gap-3 text-[11px] text-gray-500 font-medium items-center">
                      <span className="bg-gray-100 px-2 py-0.5 rounded text-gray-600 font-bold text-[9px] uppercase">{lead.primaryProduct || lead.signalType || lead.signal_type || 'N/A'}</span>
                      <StatusBadge status={lead.status} />
                      <span className="truncate max-w-[80px] lg:max-w-[100px]">{lead.source}</span>
                    </div>
                    <span className="text-[10px] text-[#DD0000] font-black uppercase tracking-tighter opacity-100 lg:opacity-0 lg:group-hover:opacity-100 transition-all flex items-center gap-1">
                      Analyze <ArrowRight size={12} />
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          </div>

          {/* Right Column: Category Split & Distribution */}
          <div className="flex flex-col gap-6 lg:gap-8">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
              <h3 className="font-bold text-[#003366] uppercase tracking-widest text-[11px] mb-6 border-b border-gray-100 pb-2">Signal Types</h3>
              <div className="space-y-4">
                {Object.entries(stats.byCategory || {}).map(([type, count]) => (
                  <div key={type}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="font-bold text-gray-700 capitalize">{type}</span>
                      <span className="text-gray-400 font-bold">{count}</span>
                    </div>
                    <div className="w-full bg-gray-100 h-1.5 rounded-full overflow-hidden">
                      <div
                        className="bg-hpcl-blue h-full"
                        style={{ width: `${(count / stats.total_leads) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-[#003366] rounded-2xl shadow-xl p-6 text-white text-center relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -mr-16 -mt-16 group-hover:scale-110 transition-transform duration-700"></div>
              <h3 className="text-lg font-black mb-2 relative z-10 uppercase tracking-tight">Live System</h3>
              <p className="text-blue-100 text-[10px] mb-6 relative z-10 leading-relaxed font-semibold">
                Real-time lead intelligence from {stats.total_leads} signals across multiple sources.
              </p>
              <button
                onClick={fetchData}
                className="w-full bg-[#DD0000] hover:bg-[#b20000] text-white py-3 rounded-xl font-black text-xs uppercase tracking-widest transition-all shadow-lg active:scale-95 relative z-10"
              >
                Refresh Data
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, color, icon }) {
  return (
    <div className={`bg-white p-5 lg:p-6 rounded-2xl shadow-sm border-l-4 ${color} hover:translate-y-[-2px] transition-all cursor-default`}>
      <div className="flex flex-col gap-1">
        <span className="mb-2">{icon}</span>
        <h4 className="text-xl lg:text-3xl font-black text-[#003366] tracking-tight tabular-nums">{value}</h4>
        <p className="text-gray-400 text-[9px] lg:text-[10px] font-black uppercase tracking-widest leading-none mt-1">{title}</p>
      </div>
    </div>
  );
}

function getScoreColor(score) {
  if (score >= 0.90) return 'bg-green-100 text-green-700';
  if (score >= 0.75) return 'bg-blue-100 text-blue-700';
  return 'bg-amber-100 text-amber-700';
}

function timeAgo(dateStr) {
  const seconds = Math.floor((new Date() - new Date(dateStr)) / 1000);
  let interval = seconds / 31536000;
  if (interval > 1) return Math.floor(interval) + "y";
  interval = seconds / 2592000;
  if (interval > 1) return Math.floor(interval) + "mo";
  interval = seconds / 86400;
  if (interval > 1) return Math.floor(interval) + "d";
  interval = seconds / 3600;
  if (interval > 1) return Math.floor(interval) + "h";
  interval = seconds / 60;
  if (interval > 1) return Math.floor(interval) + "m";
  return "now";
}
