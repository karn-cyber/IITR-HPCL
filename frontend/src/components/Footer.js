export default function Footer() {
    return (
        <footer className="bg-gray-100 border-t border-gray-200 pt-10 pb-6 px-4 lg:px-20 font-montserrat">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-10">
                <div>
                    <h3 className="text-[#0055A4] font-bold mb-4 uppercase text-sm border-b-2 border-hpcl-red pb-1 inline-block">Product Portfolio</h3>
                    <ul className="text-gray-600 text-sm space-y-2">
                        <li><Link href="#" className="hover:text-hpcl-blue">Industrial Fuels</Link></li>
                        <li><Link href="#" className="hover:text-hpcl-blue">Specialty Products</Link></li>
                        <li><Link href="#" className="hover:text-hpcl-blue">Bitumen</Link></li>
                        <li><Link href="#" className="hover:text-hpcl-blue">Marine Bunker Fuels</Link></li>
                    </ul>
                </div>
                <div>
                    <h3 className="text-[#0055A4] font-bold mb-4 uppercase text-sm border-b-2 border-hpcl-red pb-1 inline-block">Direct Sales</h3>
                    <ul className="text-gray-600 text-sm space-y-2">
                        <li><Link href="#" className="hover:text-hpcl-blue">Regional Offices</Link></li>
                        <li><Link href="#" className="hover:text-hpcl-blue">Depot Locations</Link></li>
                        <li><Link href="#" className="hover:text-hpcl-blue">Pricing Information</Link></li>
                        <li><Link href="#" className="hover:text-hpcl-blue">Product Specifications</Link></li>
                    </ul>
                </div>
                <div>
                    <h3 className="text-[#0055A4] font-bold mb-4 uppercase text-sm border-b-2 border-hpcl-red pb-1 inline-block">Quick Links</h3>
                    <ul className="text-gray-600 text-sm space-y-2">
                        <li><Link href="#" className="hover:text-hpcl-blue">B2B Portal Login</Link></li>
                        <li><Link href="#" className="hover:text-hpcl-blue">Employee Corner</Link></li>
                        <li><Link href="#" className="hover:text-hpcl-blue">Tenders & RFPs</Link></li>
                        <li><Link href="#" className="hover:text-hpcl-blue">Media Center</Link></li>
                    </ul>
                </div>
                <div>
                    <h3 className="text-[#0055A4] font-bold mb-4 uppercase text-sm border-b-2 border-hpcl-red pb-1 inline-block">Contact Us</h3>
                    <div className="text-gray-600 text-sm space-y-2">
                        <p>HPCL Lead Intelligence Cell</p>
                        <p>Hindustan Bhavan, 8, Shoorji Vallabhdas Marg</p>
                        <p>Mumbai, Maharashtra 400001</p>
                        <p className="font-semibold text-hpcl-blue">Toll Free: 1800 2333 555</p>
                    </div>
                </div>
            </div>

            <div className="border-t border-gray-300 pt-6 flex flex-col md:flex-row justify-between items-center text-[11px] text-gray-500">
                <p>© 2026 Hindustan Petroleum Corporation Limited. All rights reserved.</p>
                <div className="flex gap-4 mt-4 md:mt-0">
                    <Link href="#" className="hover:text-gray-800">Privacy Policy</Link>
                    <Link href="#" className="hover:text-gray-800">Terms of Use</Link>
                    <Link href="#" className="hover:text-gray-800">Disclaimers</Link>
                    <Link href="#" className="hover:text-gray-800">Hyperlink Policy</Link>
                    <Link href="#" className="hover:text-gray-800">Sitemap</Link>
                </div>
            </div>
        </footer>
    );
}

import Link from 'next/link';
