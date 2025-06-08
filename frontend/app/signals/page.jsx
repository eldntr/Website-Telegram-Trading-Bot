"use client";
import { useEffect, useState, useCallback } from 'react';
import Layout from '../../components/Layout';
import SignalCard from '../../components/SignalCard';
import apiClient from '../../services/api';
import { useDebounce } from '../../hooks/useDebounce'; // Hook kustom (akan dibuat di bawah)

// Komponen FilterBar terpisah untuk kebersihan kode
const FilterBar = ({ riskLevel, setRiskLevel, searchTerm, setSearchTerm }) => {
    return (
        <div className="mb-6 p-4 bg-gray-800 rounded-lg flex flex-col sm:flex-row gap-4 items-center">
            <div className="flex-grow w-full sm:w-auto">
                <input
                    type="text"
                    placeholder="Search by coin pair (e.g., BTC)"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full px-3 py-2 text-gray-100 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
            </div>
            <div>
                <select
                    value={riskLevel}
                    onChange={(e) => setRiskLevel(e.target.value)}
                    className="w-full sm:w-auto px-3 py-2 text-gray-100 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                    <option value="">All Risk Levels</option>
                    <option value="Normal">Normal</option>
                    <option value="High">High</option>
                    <option value="Very High">Very High</option>
                </select>
            </div>
        </div>
    );
};

export default function SignalsPage() {
    const [signals, setSignals] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');

    // State untuk filter
    const [riskLevel, setRiskLevel] = useState('');
    const [searchTerm, setSearchTerm] = useState('');
    const debouncedSearchTerm = useDebounce(searchTerm, 500); // Debounce input pencarian

    const fetchSignals = useCallback(async () => {
        setIsLoading(true);
        setError('');
        try {
            const params = new URLSearchParams();
            if (riskLevel) params.append('risk_level', riskLevel);
            if (debouncedSearchTerm) params.append('search', debouncedSearchTerm);

            const response = await apiClient.get(`/signals?${params.toString()}`);
            setSignals(response.data);
        } catch (err) {
            console.error("Failed to fetch signals:", err);
            setError("Could not load signals. Please try refreshing the page.");
        } finally {
            setIsLoading(false);
        }
    }, [riskLevel, debouncedSearchTerm]);

    useEffect(() => {
        fetchSignals();
    }, [fetchSignals]);

    return (
        <Layout>
            <FilterBar
                riskLevel={riskLevel}
                setRiskLevel={setRiskLevel}
                searchTerm={searchTerm}
                setSearchTerm={setSearchTerm}
            />

            {isLoading ? (
                <div className="text-center text-gray-400">Loading signals...</div>
            ) : error ? (
                <div className="text-center text-red-500">{error}</div>
            ) : signals.length === 0 ? (
                <div className="text-center text-gray-400">No signals found matching your criteria.</div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {signals.map((signal) => (
                        <SignalCard key={signal.id} signal={signal} />
                    ))}
                </div>
            )}
        </Layout>
    );
}