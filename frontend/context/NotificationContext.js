// frontend/context/NotificationContext.js
"use client";
import { createContext, useContext, useState, useCallback } from 'react';

const ToastContext = createContext();

export const useToast = () => useContext(ToastContext);

export const ToastProvider = ({ children }) => {
    const [toasts, setToasts] = useState([]);

    const addToast = useCallback((message, type = 'info') => {
        const id = Date.now();
        setToasts(prev => [...prev, { id, message, type }]);
        setTimeout(() => {
            removeToast(id);
        }, 5000); // Hapus toast setelah 5 detik
    }, []);

    const removeToast = (id) => {
        setToasts(prev => prev.filter(toast => toast.id !== id));
    };

    return (
        <ToastContext.Provider value={{ addToast }}>
            {children}
            <div className="fixed bottom-5 right-5 z-50 space-y-3">
                {toasts.map(toast => (
                    <div key={toast.id} className={`max-w-sm rounded-lg shadow-lg p-4 text-white ${
                        toast.type === 'success' ? 'bg-green-600' : 
                        toast.type === 'error' ? 'bg-red-600' : 'bg-blue-600'
                    }`}>
                        {toast.message}
                    </div>
                ))}
            </div>
        </ToastContext.Provider>
    );
};