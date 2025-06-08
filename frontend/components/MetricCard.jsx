// frontend/components/MetricCard.jsx
"use client";

import { ArrowUpIcon, ArrowDownIcon, ScaleIcon } from '@heroicons/react/24/outline';

const ProfitLossIcon = ({ value }) => {
    if (value > 0) {
        return <ArrowUpIcon className="h-6 w-6 text-green-400" aria-hidden="true" />;
    }
    if (value < 0) {
        return <ArrowDownIcon className="h-6 w-6 text-red-400" aria-hidden="true" />;
    }
    return <ScaleIcon className="h-6 w-6 text-gray-400" aria-hidden="true" />;
};


export default function MetricCard({ title, value, description, format = "default" }) {
    
    const formatValue = (val) => {
        if (val === null || val === undefined) return 'N/A';
        switch(format) {
            case 'currency':
                return val.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
            case 'percent':
                return `${val.toFixed(2)}%`;
            default:
                return val.toLocaleString();
        }
    }

    return (
        <div className="bg-gray-800 overflow-hidden shadow-lg rounded-lg">
            <div className="p-5">
                <div className="flex items-center">
                    <div className="flex-shrink-0">
                       {format === 'currency' && <ProfitLossIcon value={value} />}
                    </div>
                    <div className="ml-5 w-0 flex-1">
                        <dl>
                            <dt className="text-sm font-medium text-gray-400 truncate">{title}</dt>
                            <dd>
                                <div className="text-2xl font-bold text-white">{formatValue(value)}</div>
                                {description && <div className="text-xs text-gray-500">{description}</div>}
                            </dd>
                        </dl>
                    </div>
                </div>
            </div>
        </div>
    );
}