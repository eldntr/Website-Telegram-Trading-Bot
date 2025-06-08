"use client";
import { useState, useEffect } from 'react';

// Komponen Toggle kustom untuk tampilan yang lebih baik
const Toggle = ({ label, enabled, onChange }) => (
    <label className="flex items-center cursor-pointer">
        <div className="relative">
            <input type="checkbox" className="sr-only" checked={enabled} onChange={onChange} />
            <div className={`block w-14 h-8 rounded-full ${enabled ? 'bg-indigo-600' : 'bg-gray-600'}`}></div>
            <div className={`dot absolute left-1 top-1 bg-white w-6 h-6 rounded-full transition-transform ${enabled ? 'transform translate-x-6' : ''}`}></div>
        </div>
        <div className="ml-3 text-gray-300">{label}</div>
    </label>
);


export default function BotConfigurationForm({ initialData, onSave, isLoading }) {
  const [config, setConfig] = useState(initialData);

  useEffect(() => {
    setConfig(initialData);
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setConfig(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : (type === 'number' ? parseFloat(value) : value)
    }));
  };

  const handleToggleChange = (name) => {
    setConfig(prev => ({
        ...prev,
        [name]: !prev[name]
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(config);
  };
  
  if (!config) {
      return <div className="text-center text-gray-400">Loading configuration...</div>;
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-8 divide-y divide-gray-700">
      <div className="space-y-6">
        <div>
          <h2 className="text-lg font-medium leading-6 text-white">Trading Strategy</h2>
          <p className="mt-1 text-sm text-gray-400">Customize your bot's core trading parameters.</p>
        </div>

        {/* USDT Amount per Trade */}
        <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
          <div className="sm:col-span-3">
            <label htmlFor="usdt_per_trade" className="block text-sm font-medium text-gray-300">
              USDT Amount per Trade
            </label>
            <div className="mt-1">
              <input
                type="number"
                name="usdt_per_trade"
                id="usdt_per_trade"
                value={config.usdt_per_trade || ''}
                onChange={handleChange}
                step="0.1"
                className="block w-full rounded-md border-gray-600 bg-gray-700 text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>
          </div>
        </div>

        {/* Signal Filtering */}
        <div>
          <h3 className="text-md font-medium leading-6 text-white">Signal Filtering</h3>
           <div className="mt-4 space-y-4">
              <Toggle 
                label="Filter Old Signals"
                enabled={config.filter_old_signals_enabled}
                onChange={() => handleToggleChange('filter_old_signals_enabled')}
              />
              {config.filter_old_signals_enabled && (
                <div className="sm:col-span-3 pl-16">
                    <label htmlFor="signal_validity_minutes" className="block text-sm font-medium text-gray-300">Signal Validity (minutes)</label>
                    <input type="number" name="signal_validity_minutes" id="signal_validity_minutes" value={config.signal_validity_minutes || ''} onChange={handleChange} className="mt-1 block w-full max-w-xs rounded-md border-gray-600 bg-gray-700 text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
                </div>
              )}
           </div>
        </div>

        {/* Risk Management */}
        <div>
          <h3 className="text-md font-medium leading-6 text-white">Risk Management</h3>
           <div className="mt-4 space-y-4">
              <Toggle 
                label="Prioritize Normal Risk Signals"
                enabled={config.prioritize_normal_risk}
                onChange={() => handleToggleChange('prioritize_normal_risk')}
              />
           </div>
        </div>
      </div>

      <div className="pt-8">
        <div>
          <h2 className="text-lg font-medium leading-6 text-white">Position Management</h2>
          <p className="mt-1 text-sm text-gray-400">Define rules for managing active positions.</p>
        </div>

        {/* Trailing Stop Loss */}
        <div className="mt-6 space-y-4">
            <Toggle 
                label="Enable Trailing Stop Loss"
                enabled={config.trailing_enabled}
                onChange={() => handleToggleChange('trailing_enabled')}
            />
            {config.trailing_enabled && (
                <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6 pl-16">
                    <div className="sm:col-span-2">
                        <label htmlFor="min_trailing_tp_level" className="block text-sm font-medium text-gray-300">Min TP Level to Trail</label>
                        <input type="number" name="min_trailing_tp_level" id="min_trailing_tp_level" value={config.min_trailing_tp_level || ''} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-600 bg-gray-700 text-white shadow-sm"/>
                    </div>
                    <div className="sm:col-span-2">
                        <label htmlFor="trailing_trigger_percentage" className="block text-sm font-medium text-gray-300">Trigger Percentage</label>
                        <input type="number" name="trailing_trigger_percentage" id="trailing_trigger_percentage" value={config.trailing_trigger_percentage || ''} onChange={handleChange} step="0.001" className="mt-1 block w-full rounded-md border-gray-600 bg-gray-700 text-white shadow-sm"/>
                    </div>
                </div>
            )}
        </div>

        {/* Stuck Trade Management */}
        <div className="mt-6 space-y-4">
            <Toggle 
                label="Enable Stuck Trade Closure"
                enabled={config.stuck_trade_enabled}
                onChange={() => handleToggleChange('stuck_trade_enabled')}
            />
            {config.stuck_trade_enabled && (
                <div className="sm:col-span-3 pl-16">
                    <label htmlFor="stuck_trade_duration_hours" className="block text-sm font-medium text-gray-300">Stuck Duration (hours)</label>
                    <input type="number" name="stuck_trade_duration_hours" id="stuck_trade_duration_hours" value={config.stuck_trade_duration_hours || ''} onChange={handleChange} className="mt-1 block w-full max-w-xs rounded-md border-gray-600 bg-gray-700 text-white shadow-sm"/>
                </div>
            )}
        </div>
      </div>

      <div className="pt-5">
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isLoading}
            className="ml-3 inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-800 disabled:opacity-50"
          >
            {isLoading ? 'Saving...' : 'Save Configuration'}
          </button>
        </div>
      </div>
    </form>
  );
}