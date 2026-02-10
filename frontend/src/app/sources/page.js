'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getSources, triggerScrape } from '@/lib/services/sourcesService';
import { authStore } from '@/lib/stores/authStore';
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
    const router = useRouter();
    const [sources, setSources] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [scraping, setScraping] = useState({});

    useEffect(() => {
        if (!authStore.isAuthenticated()) {
            router.push('/login');
            return;
        }

        fetchSources();
    }, [router]);

    const fetchSources = async () => {
        setLoading(true);
        setError('');

        try {
            const data = await getSources();
            setSources(data.sources || []);
        } catch (err) {
            console.error('Failed to fetch sources:', err);
            setError(err.message || 'Failed to load sources');
        } finally {
            setLoading(false);
        }
    };

    const handleTriggerScrape = async (sourceId) => {
        setScraping(prev => ({ ...prev, [sourceId]: true }));
        try {
            await triggerScrape(sourceId);
            alert('Scrape triggered successfully!');
        } catch (err) {
            console.error('Failed to trigger scrape:', err);
            alert('Failed to trigger scrape: ' + err.message);
        } finally {
            setScraping(prev => ({ ...prev, [sourceId]: false }));
        }
    };

    if (loading) {
        return (
            <div className="bg-gray-50 min-h-screen flex items-center justify-center font-montserrat">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-hpcl-blue mx-auto mb-4"></div>
                    <p className="text-gray-600 font-bold">Loading Sources...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-gray-50 min-h-screen p-4 lg:p-10 font-montserrat pb-24 lg:pb-10">
            <div className="max-w-7xl mx-auto">
                <div className="mb-10">
                    <div className="flex items-center gap-4">
                        <span className="w-2 h-10 bg-[#DD0000]"></span>
                        <div>
                            <h1 className="text-2xl lg:text-4xl font-black text-[#003366] uppercase tracking-tight">Intelligence Sources</h1>
                            <p className="text-gray-400 text-[10px] lg:text-xs uppercase tracking-[0.2em] mt-1 font-black opacity-70">Signal Collection Network</p>
                        </div>
                    </div>
                </div>

                {error && (
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-6">
                        {error}
                    </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
                    {sources.map(source => (
                        <div key={source.id} className="bg-white rounded-3xl p-8 shadow-lg border border-gray-100 hover:shadow-2xl transition-all hover:translate-y-[-4px] group">
                            <div className="flex items-start justify-between mb-6">
                                <div className="w-14 h-14 bg-blue-100 rounded-2xl flex items-center justify-center shadow-inner">
                                    {getSourceIcon(source.source_type)}
                                </div>
                                <span className={`px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest ${source.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                                    {source.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </div>

                            <h3 className="font-black text-lg text-gray-800 mb-2 uppercase tracking-tight leading-tight">{source.name}</h3>
                            <p className="text-xs text-gray-500 mb-6 font-medium leading-relaxed line-clamp-2">{source.description || `Data collection from ${source.source_type}`}</p>

                            <div className="flex items-center justify-between text-xs pt-6 border-t border-gray-100">
                                <div className="text-center">
                                    <p className="text-gray-400 text-[9px] uppercase font-black tracking-widest mb-1">Type</p>
                                    <p className="text-hpcl-blue font-black uppercase">{source.source_type}</p>
                                </div>
                                <div className="text-center">
                                    <p className="text-gray-400 text-[9px] uppercase font-black tracking-widest mb-1">Frequency</p>
                                    <p className="text-gray-700 font-bold">{source.scrape_frequency || 'Daily'}</p>
                                </div>
                            </div>

                            {source.is_active && (
                                <button
                                    onClick={() => handleTriggerScrape(source.id)}
                                    disabled={scraping[source.id]}
                                    className="mt-6 w-full bg-[#003366] text-white py-3 rounded-xl font-black text-[10px] uppercase tracking-widest hover:bg-hpcl-blue transition-all shadow-md active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {scraping[source.id] ? 'Triggering...' : 'Trigger Manual Scrape'}
                                </button>
                            )}
                        </div>
                    ))}
                </div>

                {sources.length === 0 && !loading && (
                    <div className="text-center py-20">
                        <p className="text-gray-400 font-bold">No sources configured</p>
                    </div>
                )}
            </div>
        </div>
    );
}

function getSourceIcon(sourceType) {
    const iconMap = {
        'tender': <FileText className="text-blue-600" />,
        'news': <Newspaper className="text-emerald-600" />,
        'directory': <Globe className="text-amber-600" />
    };
    return iconMap[sourceType?.toLowerCase()] || <Globe className="text-gray-600" />;
}
