'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { authStore } from '@/lib/stores/authStore';
import { Lock, Mail, Zap, ShieldCheck, ArrowRight } from 'lucide-react';

export default function LoginPage() {
    const router = useRouter();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            await authStore.login(email, password);
            router.push('/');
        } catch (err) {
            setError(err.message || 'Login failed. Please check your credentials.');
        } finally {
            setLoading(false);
        }
    };

    const handleDemoLogin = async () => {
        setError('');
        setLoading(true);

        try {
            await authStore.demoLogin();
            router.push('/');
        } catch (err) {
            setError(err.message || 'Demo login failed.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-[#003366] via-[#0055A4] to-[#003366] flex items-center justify-center p-4 font-montserrat">
            <div className="max-w-md w-full">
                {/* Logo & Header */}
                <div className="text-center mb-10">
                    <div className="inline-block bg-white/10 backdrop-blur-md p-5 rounded-3xl mb-6 border border-white/20">
                        <ShieldCheck size={48} className="text-white" />
                    </div>
                    <h1 className="text-3xl lg:text-4xl font-black text-white mb-2 uppercase tracking-tight">
                        HPCL Lead Intelligence
                    </h1>
                    <p className="text-blue-100 text-sm font-bold uppercase tracking-widest opacity-80">
                        B2B Sales Pipeline System
                    </p>
                </div>

                {/* Login Card */}
                <div className="bg-white rounded-3xl shadow-2xl p-8 lg:p-10">
                    {/* Demo Login Button */}
                    <button
                        onClick={handleDemoLogin}
                        disabled={loading}
                        className="w-full bg-gradient-to-r from-[#DD0000] to-[#ff4444] text-white py-4 rounded-xl font-black text-sm uppercase tracking-widest hover:shadow-2xl transition-all mb-6 flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Zap size={20} />
                        {loading ? 'Connecting...' : 'Quick Demo Login'}
                    </button>

                    {/* Divider */}
                    <div className="relative my-6">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-gray-200"></div>
                        </div>
                        <div className="relative flex justify-center text-xs uppercase">
                            <span className="bg-white px-4 text-gray-400 font-black tracking-widest">
                                Or sign in with credentials
                            </span>
                        </div>
                    </div>

                    {/* Login Form */}
                    <form onSubmit={handleSubmit} className="space-y-5">
                        {error && (
                            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm font-bold">
                                {error}
                            </div>
                        )}

                        <div>
                            <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">
                                Email Address
                            </label>
                            <div className="relative">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="admin@hpcl.com"
                                    required
                                    className="w-full pl-12 pr-4 py-4 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-hpcl-blue focus:border-transparent outline-none transition-all font-bold text-gray-800"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">
                                Password
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="Enter your password"
                                    required
                                    className="w-full pl-12 pr-4 py-4 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-hpcl-blue focus:border-transparent outline-none transition-all font-bold text-gray-800"
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-[#003366] hover:bg-[#0055A4] text-white py-4 rounded-xl font-black text-sm uppercase tracking-widest transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                        >
                            {loading ? 'Signing in...' : 'Sign In'}
                            <ArrowRight size={18} />
                        </button>
                    </form>

                    {/* Test Credentials */}
                    <div className="mt-8 pt-6 border-t border-gray-100">
                        <p className="text-xs font-black text-gray-400 uppercase tracking-widest mb-3 text-center">
                            Test Credentials
                        </p>
                        <div className="bg-gray-50 rounded-xl p-4 space-y-2 text-xs font-mono">
                            <div className="flex justify-between">
                                <span className="text-gray-500">Admin:</span>
                                <span className="text-gray-800 font-bold">admin@hpcl.com / admin123</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-500">Manager:</span>
                                <span className="text-gray-800 font-bold">manager@hpcl.com / manager123</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-500">Officer:</span>
                                <span className="text-gray-800 font-bold">officer@hpcl.com / officer123</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <p className="text-center text-blue-100 text-xs mt-8 font-bold opacity-60">
                    Powered by HPCL Digital Innovation Lab
                </p>
            </div>
        </div>
    );
}
