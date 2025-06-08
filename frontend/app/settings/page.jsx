"use client";
import { useEffect, useState } from 'react';
import Layout from '../../components/Layout';
import BotConfigurationForm from '../../components/BotConfigurationForm';
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
      // Hanya kirim field yang diubah
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
      setConfig(response.data); // Update state lokal dengan data terbaru dari server
      setSuccess('Configuration saved successfully!');
    } catch (err) {
      console.error("Failed to save configuration:", err);
      setError(err.response?.data?.detail || "Failed to save configuration.");
    } finally {
      setIsSaving(false);
      // Hapus pesan setelah beberapa detik
      setTimeout(() => setSuccess(''), 3000);
    }
  };

  return (
    <Layout>
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
    </Layout>
  );
}