"use client";
import { useState } from 'react';
import apiClient from '../services/api';

// Fungsi helper formatTimeAgo dan RiskBadge tetap sama (tidak ditampilkan untuk keringkasan)
const formatTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);

    let interval = seconds / 31536000;
    if (interval > 1) return Math.floor(interval) + " years ago";
    interval = seconds / 2592000;
    if (interval > 1) return Math.floor(interval) + " months ago";
    interval = seconds / 86400;
    if (interval > 1) return Math.floor(interval) + " days ago";
    interval = seconds / 3600;
    if (interval > 1) return Math.floor(interval) + " hours ago";
    interval = seconds / 60;
    if (interval > 1) return Math.floor(interval) + " minutes ago";
    return Math.floor(seconds) + " seconds ago";
}

const RiskBadge = ({ level }) => {
    const levelLower = level?.toLowerCase();
    let colorClasses = 'bg-gray-600 text-gray-100'; // Default
    if (levelLower === 'normal') {
        colorClasses = 'bg-green-600 text-white';
    } else if (levelLower === 'high') {
        colorClasses = 'bg-yellow-500 text-black';
    } else if (levelLower === 'very high') {
        colorClasses = 'bg-red-600 text-white';
    }
    return (
        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${colorClasses}`}>
            {level || 'N/A'} Risk
        </span>
    );
};


export default function SignalCard({ signal }) {
    const [isExpanded, setIsExpanded] = useState(false);
    const [activationStatus, setActivationStatus] = useState({ loading: false, message: '', error: false });

    // --- FUNGSI HANDLEACTIVATE DIPERBARUI ---
    const handleActivate = async () => {
        setActivationStatus({ loading: true, message: 'Activating...', error: false });
        try {
            await apiClient.post('/trades/activate', { signal_id: signal.id });
            setActivationStatus({ loading: false, message: 'Monitoring Activated!', error: false });
        } catch (err) {
            console.error("Activation failed:", err.response); // Log seluruh respons error untuk debug
            
            // Logika baru untuk mem-parsing error
            let errorMessage = "An unknown error occurred.";
            if (err.response?.data?.detail) {
                const detail = err.response.data.detail;
                // Jika detail adalah array (khas error 422), ambil pesan pertama
                if (Array.isArray(detail) && detail.length > 0 && detail[0].msg) {
                    errorMessage = detail[0].msg;
                } 
                // Jika detail adalah string (khas error 400, 404, 409)
                else if (typeof detail === 'string') {
                    errorMessage = detail;
                }
            }
            
            setActivationStatus({ loading: false, message: errorMessage, error: true });
        }
    };

    return (
        <div className="bg-gray-800 rounded-lg shadow-md overflow-hidden transition-all duration-300 hover:shadow-lg hover:shadow-indigo-500/20">
            <div className="p-4 cursor-pointer" onClick={() => setIsExpanded(!isExpanded)}>
                <div className="flex justify-between items-center">
                    <h3 className="text-xl font-bold text-white">{signal.coin_pair}</h3>
                    <RiskBadge level={signal.risk_level} />
                </div>
                <div className="flex justify-between items-baseline mt-2">
                    <p className="text-sm text-gray-400">Entry Price: <span className="font-mono text-cyan-400">${signal.entry_price}</span></p>
                    <p className="text-xs text-gray-500">{formatTimeAgo(signal.timestamp)}</p>
                </div>
            </div>

            {isExpanded && (
                <div className="px-4 pb-4 bg-gray-800/50">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 text-sm">
                        {/* Targets */}
                        <div>
                            <h4 className="font-semibold text-green-400 mb-2">Targets</h4>
                            <ul className="space-y-1 font-mono">
                                {signal.targets.map(t => (
                                    <li key={t.level} className="flex justify-between">
                                        <span className="text-gray-300">Target {t.level}</span>
                                        <span className="text-gray-200">${t.price}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                        {/* Stop Losses */}
                        <div>
                            <h4 className="font-semibold text-red-400 mb-2">Stop Losses</h4>
                            <ul className="space-y-1 font-mono">
                                {signal.stop_losses.map(sl => (
                                    <li key={sl.level} className="flex justify-between">
                                        <span className="text-gray-300">SL {sl.level}</span>
                                        <span className="text-gray-200">${sl.price}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                    <div className="mt-4 pt-4 border-t border-gray-700">
                        <button 
                            onClick={handleActivate}
                            disabled={activationStatus.loading || (activationStatus.message && !activationStatus.error)}
                            className="w-full bg-indigo-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-indigo-700 transition-colors disabled:bg-gray-600 disabled:cursor-not-allowed"
                        >
                            {activationStatus.loading ? 'Activating...' : 'Aktifkan Otomatisasi'}
                        </button>
                        {activationStatus.message && (
                            <p className={`mt-2 text-sm text-center ${activationStatus.error ? 'text-red-400' : 'text-green-400'}`}>
                                {activationStatus.message}
                            </p>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}