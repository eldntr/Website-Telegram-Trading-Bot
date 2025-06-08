// frontend/components/BinanceKeysForm.jsx
"use client";
import { useState } from 'react';
import apiClient from '../services/api';

export default function BinanceKeysForm() {
  const [apiKey, setApiKey] = useState('');
  const [apiSecret, setApiSecret] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setMessage('');
    setError('');

    try {
      await apiClient.put('/users/me/binance-keys', {
        api_key: apiKey,
        api_secret: apiSecret,
      });
      setMessage('Binance API keys saved successfully!');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save keys.');
    } finally {
      setIsSaving(false);
      // Hapus pesan setelah beberapa detik
      setTimeout(() => {
        setMessage('');
        setError('');
      }, 5000);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h2 className="text-lg font-medium leading-6 text-white">Binance API Keys</h2>
        <p className="mt-1 text-sm text-gray-400">
          Your keys are encrypted before being stored. They are only used to execute trades on your behalf.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-y-6 gap-x-4">
        <div className="sm:col-span-4">
          <label htmlFor="api_key" className="block text-sm font-medium text-gray-300">
            API Key
          </label>
          <div className="mt-1">
            <input
              type="password"
              name="api_key"
              id="api_key"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              required
              className="block w-full rounded-md border-gray-600 bg-gray-700 text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
        </div>

        <div className="sm:col-span-4">
          <label htmlFor="api_secret" className="block text-sm font-medium text-gray-300">
            API Secret
          </label>
          <div className="mt-1">
            <input
              type="password"
              name="api_secret"
              id="api_secret"
              value={apiSecret}
              onChange={(e) => setApiSecret(e.target.value)}
              required
              className="block w-full rounded-md border-gray-600 bg-gray-700 text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
        </div>
      </div>

      {error && <div className="p-3 bg-red-800 border border-red-600 text-red-200 rounded-md text-sm">{error}</div>}
      {message && <div className="p-3 bg-green-800 border border-green-600 text-green-200 rounded-md text-sm">{message}</div>}

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isSaving}
          className="ml-3 inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-800 disabled:opacity-50"
        >
          {isSaving ? 'Saving...' : 'Save Keys'}
        </button>
      </div>
    </form>
  );
}