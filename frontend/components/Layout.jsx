// frontend/components/Layout.jsx
"use client";
import { useAuth } from '../context/AuthContext';
import { useRouter, usePathname } from 'next/navigation';
import { useEffect, useRef } from 'react';
import Link from 'next/link';
import { useToast } from '../context/NotificationContext'; // <-- Import useToast

export default function Layout({ children }) {
  const { isAuthenticated, logout, user } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const { addToast } = useToast(); // <-- Gunakan hook toast
  const ws = useRef(null); // <-- Ref untuk menyimpan objek WebSocket

  // --- Logika WebSocket ---
  useEffect(() => {
    if (isAuthenticated) {
      const token = localStorage.getItem('authToken');
      // Ganti ws:// dengan wss:// untuk produksi (HTTPS)
      const wsUrl = `ws://localhost:8000/api/v1/ws/user-feed?token=${token}`;
      
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        console.log("WebSocket connected");
        addToast("Connected to real-time feed!", "success");
      };

      ws.current.onmessage = (event) => {
        const message = JSON.parse(event.data);
        console.log("WebSocket message received:", message);

        if (message.type === 'TRADE_OPENED') {
          addToast(`Trade Opened: ${message.data.symbol} @ ${message.data.entry_price.toFixed(4)}`);
        } else if (message.type === 'TRADE_CLOSED') {
          const pl = message.data.net_profit_loss;
          const plFormatted = pl.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
          addToast(
            `Trade Closed: ${message.data.symbol} | P/L: ${plFormatted}`,
            pl >= 0 ? 'success' : 'error'
          );
        }
      };

      ws.current.onclose = () => {
        console.log("WebSocket disconnected");
      };

      ws.current.onerror = (error) => {
        console.error("WebSocket error:", error);
      };

      // Cleanup function untuk menutup koneksi saat komponen unmount atau user logout
      return () => {
        if (ws.current) {
          ws.current.close();
        }
      };
    }
  }, [isAuthenticated, addToast]);

  if (!isAuthenticated) {
    return <div className="min-h-screen bg-gray-900 flex items-center justify-center text-white">Loading...</div>;
  }

  const navLinkClasses = (path) => 
    `px-3 py-2 rounded-md text-sm font-medium ${
      pathname.startsWith(path) // Menggunakan startsWith untuk handle sub-routes jika ada
        ? 'bg-gray-900 text-white' 
        : 'text-gray-300 hover:bg-gray-700 hover:text-white'
    }`;

  return (
    <div className="min-h-screen bg-gray-900">
      <nav className="bg-gray-800">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center">
              <div className="flex-shrink-0 text-white font-bold">
                TradeBot
              </div>
              <div className="hidden md:block">
                <div className="ml-10 flex items-baseline space-x-4">
                  {/* -- BARU: Link ke Dashboard -- */}
                  <Link href="/dashboard" className={navLinkClasses('/dashboard')}>
                    Dashboard
                  </Link>
                  <Link href="/signals" className={navLinkClasses('/signals')}>
                    Signals
                  </Link>
                  <Link href="/positions" className={navLinkClasses('/positions')}>
                    Positions
                  </Link>
                  <Link href="/settings" className={navLinkClasses('/settings')}>
                    Settings
                  </Link>
                </div>
              </div>
            </div>
            <div className="hidden md:block">
              <div className="ml-4 flex items-center md:ml-6">
                <span className="text-gray-400 text-sm mr-3">Welcome, {user?.email}</span>
                <button
                  onClick={logout}
                  className="bg-red-600 px-3 py-2 rounded-md text-sm font-medium text-white hover:bg-red-700"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <header className="bg-gray-800 shadow-sm">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <h1 className="text-xl font-semibold tracking-tight text-white capitalize">
            {pathname.split('/')[1] || 'Dashboard'}
          </h1>
        </div>
      </header>
      <main>
        <div className="mx-auto max-w-7xl py-6 sm:px-6 lg:px-8">
          {children}
        </div>
      </main>
    </div>
  );
}