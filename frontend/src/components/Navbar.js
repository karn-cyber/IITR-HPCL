'use client';

import Link from 'next/link';
import { useState } from 'react';
import { usePathname } from 'next/navigation';
import {
    LayoutDashboard,
    ClipboardList,
    Globe,
    BarChart3,
    Search,
    Settings,
    Menu,
    X
} from 'lucide-react';

export default function Navbar() {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const pathname = usePathname();

    const navLinks = [
        { name: 'Dashboard', href: '/', icon: <LayoutDashboard size={20} /> },
        { name: 'Leads', href: '/leads', icon: <ClipboardList size={20} /> },
        { name: 'Sources', href: '/sources', icon: <Globe size={20} /> },
        { name: 'Analytics', href: '/analytics', icon: <BarChart3 size={20} /> },
    ];

    return (
        <>
            <header className="w-full flex flex-col font-montserrat sticky top-0 z-40 bg-white">
                {/* Top Utility Bar - Hidden on small mobile */}
                <div className="hidden sm:flex bg-[#0055A4] text-white text-[10px] lg:text-[12px] py-1 px-4 lg:px-20 justify-between items-center">
                    <div className="flex gap-4">
                        <Link href="#" className="hover:underline">Skip to content</Link>
                        <Link href="#" className="hover:underline">Complaints</Link>
                    </div>
                    <div className="flex gap-4 items-center">
                        <button className="hover:text-gray-200">A+</button>
                        <button className="hover:text-gray-200 text-xs">A-</button>
                        <div className="h-3 w-[1px] bg-white/30 mx-1"></div>
                        <Link href="#" className="hover:underline">Login</Link>
                    </div>
                </div>

                {/* Brand Bar */}
                <div className="bg-white py-3 px-4 lg:px-20 flex justify-between items-center shadow-sm border-b border-gray-100">
                    <Link href="/" className="flex items-center gap-3">
                        <img
                            src="/hpcl_logo.png"
                            alt="HP Logo"
                            className="h-9 w-9 sm:h-12 sm:w-12 object-contain"
                        />
                        <div className="flex flex-col">
                            <h1 className="text-[#0055A4] font-bold text-sm sm:text-lg leading-tight uppercase tracking-tight">
                                HPCL Leads
                            </h1>
                            <p className="text-gray-500 text-[8px] sm:text-[10px] font-bold italic tracking-widest leading-none">
                                Delivering Happiness
                            </p>
                        </div>
                    </Link>

                    <button
                        onClick={() => setIsMenuOpen(!isMenuOpen)}
                        className="lg:hidden text-[#0055A4] focus:outline-none p-1 bg-gray-50 rounded"
                    >
                        {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
                    </button>

                    {/* Desktop Search */}
                    <div className="hidden lg:flex items-center ml-auto mr-8">
                        <div className="relative">
                            <input
                                type="text"
                                placeholder="Search Intel..."
                                className="bg-gray-100 border border-transparent rounded-full py-2 px-10 text-sm focus:ring-2 focus:ring-hpcl-blue focus:bg-white focus:border-hpcl-blue transition-all w-64 outline-none"
                            />
                            <Search className="absolute left-3 top-2.5 opacity-40 text-[#0055A4]" size={16} />
                        </div>
                    </div>
                </div>

                {/* Desktop Navigation Menu */}
                <nav className="hidden lg:flex bg-[#003366] text-white px-20 items-center h-12 shadow-inner">
                    {navLinks.map((link) => (
                        <Link
                            key={link.name}
                            href={link.href}
                            className={`h-full flex items-center px-6 text-[12px] font-bold uppercase tracking-[0.15em] transition-all hover:bg-white/10 ${pathname === link.href ? 'bg-[#DD0000] shadow-lg' : ''}`}
                        >
                            {link.name}
                        </Link>
                    ))}
                    <Link href="/settings" className="ml-auto flex items-center gap-2 hover:text-blue-200 transition-colors text-xs font-bold uppercase tracking-widest">
                        <Settings size={14} /> Admin
                    </Link>
                </nav>

                {/* Mobile Dropdown Menu (Secondary) */}
                <div className={`lg:hidden bg-white border-b border-gray-200 transition-all duration-300 overflow-hidden ${isMenuOpen ? 'max-h-64' : 'max-h-0'}`}>
                    <div className="flex flex-col p-4 gap-4">
                        {navLinks.map((link) => (
                            <Link
                                key={link.name}
                                href={link.href}
                                onClick={() => setIsMenuOpen(false)}
                                className={`flex justify-between items-center font-bold text-xs uppercase tracking-widest ${pathname === link.href ? 'text-[#DD0000]' : 'text-gray-600'}`}
                            >
                                {link.name}
                                <span>{link.icon}</span>
                            </Link>
                        ))}
                        <div className="h-[1px] bg-gray-100 my-1"></div>
                        <Link href="/settings" className="text-gray-400 text-[10px] font-bold uppercase tracking-widest">System Settings</Link>
                    </div>
                </div>
            </header>

            {/* MOBILE BOTTOM NAVIGATION BAR */}
            <div className="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50 px-8 py-3 pb-6 flex justify-between items-center shadow-[0_-8px_15px_rgba(0,0,0,0.05)]">
                {navLinks.map((link) => (
                    <Link
                        key={link.name}
                        href={link.href}
                        className={`flex flex-col items-center gap-1 transition-all group ${pathname === link.href ? 'text-[#DD0000]' : 'text-gray-400'}`}
                    >
                        <span className={`text-xl transition-transform ${pathname === link.href ? 'scale-110' : 'group-hover:scale-105'}`}>{link.icon}</span>
                        <span className={`text-[9px] font-black uppercase tracking-tighter ${pathname === link.href ? 'opacity-100' : 'opacity-60'}`}>{link.name}</span>
                    </Link>
                ))}
            </div>
        </>
    );
}

