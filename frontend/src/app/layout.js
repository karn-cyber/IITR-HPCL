import "./globals.css";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import LeadAlert from "@/components/LeadAlert";

export const metadata = {
  title: "HPCL | B2B Lead Intelligence",
  description: "Automated B2B lead detection and qualification for HPCL Direct Sales",
  icons: {
    icon: '/hpcl_logo.png',
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet" />
      </head>
      <body className="antialiased font-montserrat min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-grow">
          {children}
        </main>
        <Footer />
        <LeadAlert />
      </body>
    </html>
  );
}




