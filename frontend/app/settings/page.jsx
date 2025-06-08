// frontend/app/settings/page.jsx
"use client";
import { useEffect, useState } from 'react';
import Layout from '../../components/Layout';
import BotConfigurationForm from '../../components/BotConfigurationForm';
import BinanceKeysForm from '../../components/BinanceKeysForm'; // <-- Import komponen baru
import apiClient from '../../services/api';

export default function SettingsPage() {
  const [config, setConfig] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Fetch initial configuration
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        setIsLoading(true);
        const response = await apiClient.get('/configurations');
        setConfig(response.data);
      } catch (err) {
        console.error("Failed to fetch configuration:", err);
        setError("Could not load your configuration. Please try again later.");
      } finally {
        setIsLoading(false);
      }
    };
    fetchConfig();
  }, []);

  const handleSave = async (updatedConfig) => {
    setIsSaving(true);
    setError('');
    setSuccess('');
    try {
      const payload = {};
      for (const key in updatedConfig) {
        if (updatedConfig[key] !== config[key]) {
            payload[key] = updatedConfig[key];
        }
      }

      if (Object.keys(payload).length === 0) {
          setSuccess("No changes to save.");
          setIsSaving(false);
          return;
      }

      const response = await apiClient.put('/configurations', payload);
      setConfig(response.data); 
      setSuccess('Configuration saved successfully!');
    } catch (err) {
      console.error("Failed to save configuration:", err);
      setError(err.response?.data?.detail || "Failed to save configuration.");
    } finally {
      setIsSaving(false);
      setTimeout(() => setSuccess(''), 3000);
    }
  };

  return (
    <Layout>
      <div className="space-y-10">
        {/* Bagian untuk Kunci API Binance */}
        <div className="bg-gray-800 shadow-lg rounded-lg p-6">
          <BinanceKeysForm />
        </div>

        {/* Bagian untuk Konfigurasi Bot */}
        <div className="bg-gray-800 shadow-lg rounded-lg p-6">
          {error && <div className="mb-4 p-3 bg-red-800 border border-red-600 text-red-200 rounded-md">{error}</div>}
          {success && <div className="mb-4 p-3 bg-green-800 border border-green-600 text-green-200 rounded-md">{success}</div>}

          {isLoading ? (
            <p>Loading settings...</p>
          ) : (
            <BotConfigurationForm
              initialData={config}
              onSave={handleSave}
              isLoading={isSaving}
            />
          )}
        </div>
      </div>
    </Layout>
  );
}