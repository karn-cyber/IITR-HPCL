'use client';

import { useState, useEffect } from 'react';
import { generateMockLeads } from '@/lib/intelligence/mockData';
import Link from 'next/link';
import {
  Search,
  Zap,
  CheckCircle2,
  IndianRupee,
  ArrowRight,
  TrendingUp,
  Globe
} from 'lucide-react';

export default function Dashboard() {
  const [leads, setLeads] = useState([]);
  const [stats, setStats] = useState({
    total: 0,
    highConfidence: 0,
    autoAssigned: 0,
    byCategory: {}
  });

  useEffect(() => {
    const mockLeads = generateMockLeads(250);
    setLeads(mockLeads);

    const newStats = {
      total: mockLeads.length,
      highConfidence: mockLeads.filter(l => l.confidence >= 0.85).length,
      autoAssigned: mockLeads.filter(l => l.status === 'AUTO_ASSIGNED').length,
      byCategory: mockLeads.reduce((acc, lead) => {
        acc[lead.primaryProduct] = (acc[lead.primaryProduct] || 0) + 1;
        return acc;
      }, {})
    };
    setStats(newStats);
  }, []);

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
          <div className="bg-white p-1 rounded-lg shadow-sm border border-gray-200 flex w-full md:w-auto">
            <button className="flex-1 md:flex-none px-4 py-1.5 text-[10px] lg:text-xs font-bold bg-[#0055A4] text-white rounded shadow-sm uppercase tracking-widest">Executive</button>
            <button className="flex-1 md:flex-none px-4 py-1.5 text-[10px] lg:text-xs font-bold text-gray-400 hover:bg-gray-100 transition-colors uppercase tracking-widest">Territory View</button>
          </div>
        </div>

        {/* Stats Grid - Responsive Cols */}
        <div className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6 mb-8 lg:mb-10">
          <StatCard title="Detected" value={stats.total} color="border-hpcl-blue" icon={<Search size={24} className="text-hpcl-blue" />} />
          <StatCard title="High Intent" value={stats.highConfidence} color="border-hpcl-red" icon={<Zap size={24} className="text-hpcl-red" />} />
          <StatCard title="Assigned" value={stats.autoAssigned} color="border-green-600" icon={<CheckCircle2 size={24} className="text-green-600" />} />
          <StatCard title="Value Est." value="₹14.2 Cr" color="border-amber-500" icon={<IndianRupee size={24} className="text-amber-500" />} />
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
                        {(lead.confidence * 100).toFixed(0)}%
                      </span>
                      <h3 className="font-bold text-gray-800 text-sm lg:text-base leading-none tracking-tight truncate max-w-[140px] sm:max-w-none">{lead.company}</h3>
                    </div>
                    <span className="text-[10px] text-gray-400 font-bold">{timeAgo(lead.timestamp)}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex gap-3 text-[11px] text-gray-500 font-medium">
                      <span className="bg-gray-100 px-2 py-0.5 rounded text-gray-600 font-bold text-[9px] uppercase">{lead.primaryProduct}</span>
                      <span className="truncate max-w-[100px]">{lead.industry}</span>
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
              <h3 className="font-bold text-[#003366] uppercase tracking-widest text-[11px] mb-6 border-b border-gray-100 pb-2">Category Split</h3>
              <div className="space-y-4">
                {Object.entries(stats.byCategory).sort((a, b) => b[1] - a[1]).slice(0, 6).map(([cat, count]) => (
                  <div key={cat}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="font-bold text-gray-700">{cat}</span>
                      <span className="text-gray-400 font-bold">{count}</span>
                    </div>
                    <div className="w-full bg-gray-100 h-1.5 rounded-full overflow-hidden">
                      <div
                        className="bg-hpcl-blue h-full"
                        style={{ width: `${(count / stats.total) * 100 * 2.5}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-[#003366] rounded-2xl shadow-xl p-6 text-white text-center relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -mr-16 -mt-16 group-hover:scale-110 transition-transform duration-700"></div>
              <h3 className="text-lg font-black mb-2 relative z-10 uppercase tracking-tight">Geo-Routing Active</h3>
              <p className="text-blue-100 text-[10px] mb-6 relative z-10 leading-relaxed font-semibold">Leads are currently being routed to {leads.filter(l => l.status === 'AUTO_ASSIGNED').length} ROs based on field location.</p>
              <button className="w-full bg-[#DD0000] hover:bg-[#b20000] text-white py-3 rounded-xl font-black text-xs uppercase tracking-widest transition-all shadow-lg active:scale-95 relative z-10">
                Territory Check
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
