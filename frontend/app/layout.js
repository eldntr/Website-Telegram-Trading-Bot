// frontend/app/layout.js
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from '../context/AuthContext';
import { ToastProvider } from '../context/NotificationContext'; // <-- Import

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "Auto Trade Bot Dashboard",
  description: "Dashboard to manage your auto trading bot.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-gray-900 text-gray-100`}>
        <ToastProvider> {/* <-- Bungkus dengan ToastProvider */}
            <AuthProvider>
              {children}
            </AuthProvider>
        </ToastProvider>
      </body>
    </html>
  );
}