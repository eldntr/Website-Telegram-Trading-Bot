"use client";
import { useState, useEffect, useCallback } from 'react';
import Layout from '../../components/Layout';
import PositionsTable from '../../components/PositionsTable';
import apiClient from '../../services/api';

const TABS = {
    ACTIVE: 'ACTIVE',
    HISTORY: 'HISTORY',
};

export default function PositionsPage() {
    const [activeTab, setActiveTab] = useState(TABS.ACTIVE);
    const [trades, setTrades] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [refreshTrigger, setRefreshTrigger] = useState(0); // Untuk memicu refresh data

    const fetchTrades = useCallback(async () => {
        setIsLoading(true);
        setError('');
        
        // Menentukan status yang akan di-query berdasarkan tab
        const statusQuery = activeTab === TABS.ACTIVE ? 'ACTIVE' : 'CLOSED_TP,CLOSED_SL,CLOSED_MANUAL';

        try {
            const promises = statusQuery.split(',').map(status => 
                apiClient.get(`/trades?status=${status}`)
            );
            const responses = await Promise.all(promises);
            const allTrades = responses.flatMap(res => res.data);
            
            // Urutkan berdasarkan tanggal
            allTrades.sort((a, b) => new Date(b.opened_at) - new Date(a.opened_at));
            
            setTrades(allTrades);
        } catch (err) {
            console.error("Failed to fetch trades:", err);
            setError("Could not load trades.");
        } finally {
            setIsLoading(false);
        }
    }, [activeTab, refreshTrigger]);

    useEffect(() => {
        fetchTrades();
    }, [fetchTrades]);
    
    const handleManualClose = async (tradeId) => {
        if (!window.confirm("Are you sure you want to manually close this position? This action cannot be undone.")) {
            return;
        }
        
        try {
            await apiClient.post(`/trades/${tradeId}/close-manual`);
            // Refresh data setelah berhasil menutup
            setRefreshTrigger(prev => prev + 1);
        } catch (err) {
            alert(err.response?.data?.detail || "Failed to close the trade.");
        }
    }

    const tabClasses = (tabName) => `px-4 py-2 text-sm font-medium rounded-t-lg
        ${activeTab === tabName 
            ? 'border-b-2 border-indigo-500 text-indigo-400'
            : 'text-gray-400 hover:text-gray-200'
        }`;

    return (
        <Layout>
            <div className="bg-gray-800 shadow-lg rounded-lg p-6">
                <div className="border-b border-gray-700 mb-4">
                    <nav className="-mb-px flex space-x-4" aria-label="Tabs">
                        <button onClick={() => setActiveTab(TABS.ACTIVE)} className={tabClasses(TABS.ACTIVE)}>
                            Active Positions
                        </button>
                        <button onClick={() => setActiveTab(TABS.HISTORY)} className={tabClasses(TABS.HISTORY)}>
                            Trade History
                        </button>
                    </nav>
                </div>
                
                {error && <div className="text-center text-red-500 p-4">{error}</div>}

                <PositionsTable trades={trades} isLoading={isLoading} onManualClose={handleManualClose} />
            </div>
        </Layout>
    );
}