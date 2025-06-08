// frontend/app/dashboard/page.jsx
"use client";
import { useEffect, useState } from 'react';
import Layout from '../../components/Layout';
import MetricCard from '../../components/MetricCard';
import apiClient from '../../services/api';

export default function DashboardPage() {
    const [summary, setSummary] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchSummary = async () => {
            setIsLoading(true);
            try {
                const response = await apiClient.get('/dashboard/summary');
                setSummary(response.data);
            } catch (err) {
                console.error("Failed to fetch dashboard summary:", err);
                setError("Could not load dashboard data. Please try again later.");
            } finally {
                setIsLoading(false);
            }
        };

        fetchSummary();
    }, []);

    if (isLoading) {
        return <Layout><p className="text-center">Loading dashboard...</p></Layout>;
    }
    
    if (error) {
        return <Layout><p className="text-center text-red-500">{error}</p></Layout>;
    }

    return (
        <Layout>
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
                <MetricCard 
                    title="Current Portfolio Value"
                    value={summary.current_portfolio_value}
                    description={summary.portfolio_error}
                    format="currency"
                />
                <MetricCard 
                    title="Total Net Profit/Loss"
                    value={summary.total_net_pl}
                    description={`From ${summary.total_trades_closed} closed trades`}
                    format="currency"
                />
                <MetricCard 
                    title="Win Rate"
                    value={summary.win_rate}
                    description={`${summary.winning_trades} wins / ${summary.losing_trades} losses`}
                    format="percent"
                />
                 <MetricCard 
                    title="Total Trades Closed"
                    value={summary.total_trades_closed}
                />
            </div>
            {/* Di sini nantinya bisa ditambahkan komponen Chart */}
        </Layout>
    );
}