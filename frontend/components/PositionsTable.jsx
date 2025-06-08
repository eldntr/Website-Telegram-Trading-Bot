"use client";

const formatCurrency = (value) => {
    if (typeof value !== 'number') return 'N/A';
    return value.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
};

const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('en-GB', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
};

const ProfitLossPill = ({ value }) => {
    if (typeof value !== 'number') {
        return <span className="px-2 py-1 text-xs font-medium text-gray-300 bg-gray-600 rounded-full">Pending</span>;
    }
    const isProfit = value >= 0;
    const colorClasses = isProfit ? 'bg-green-800 text-green-200' : 'bg-red-800 text-red-200';
    return (
        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${colorClasses}`}>
            {formatCurrency(value)}
        </span>
    );
};

const StatusPill = ({ status }) => {
    let colorClasses = 'bg-gray-600';
    if (status?.includes('ACTIVE')) colorClasses = 'bg-blue-600';
    if (status?.includes('TP')) colorClasses = 'bg-green-600';
    if (status?.includes('SL')) colorClasses = 'bg-red-600';
    if (status?.includes('MANUAL')) colorClasses = 'bg-yellow-600';
    
    return (
         <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${colorClasses} text-white`}>
            {status || 'UNKNOWN'}
        </span>
    )
}

export default function PositionsTable({ trades, isLoading, onManualClose }) {
    if (isLoading) {
        return <p className="text-center text-gray-400">Loading positions...</p>;
    }

    if (trades.length === 0) {
        return <p className="text-center text-gray-400">No positions found.</p>;
    }

    const isHistory = trades[0]?.status !== 'ACTIVE';

    return (
        <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-700">
                <thead className="bg-gray-800">
                    <tr>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Symbol</th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Status</th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Entry Price</th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Quantity</th>
                        {isHistory && <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Exit Price</th>}
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">{isHistory ? 'Net P/L' : 'Opened At'}</th>
                        {!isHistory && <th scope="col" className="relative px-6 py-3"><span className="sr-only">Close</span></th>}
                    </tr>
                </thead>
                <tbody className="bg-gray-800 divide-y divide-gray-700">
                    {trades.map((trade) => (
                        <tr key={trade.id} className="hover:bg-gray-700/50">
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">{trade.symbol}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm"><StatusPill status={trade.status} /></td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-cyan-400">{formatCurrency(trade.entry_price)}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{trade.quantity}</td>
                            {isHistory && <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-cyan-400">{formatCurrency(trade.exit_price)}</td>}
                            <td className="px-6 py-4 whitespace-nowrap text-sm">
                                {isHistory ? <ProfitLossPill value={trade.net_profit_loss} /> : <span className="text-gray-400">{formatDate(trade.opened_at)}</span>}
                            </td>
                            {!isHistory && (
                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <button 
                                        onClick={() => onManualClose(trade.id)}
                                        className="text-red-500 hover:text-red-700"
                                    >
                                        Close
                                    </button>
                                </td>
                            )}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}