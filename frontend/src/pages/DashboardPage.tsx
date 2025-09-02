import React, { useEffect, useState } from 'react';
import { useAuth } from '../components/AuthContext';
import LogEntryForm from '../components/LogEntryForm';
import JournalEntry from '../components/JournalEntry';
import Charts from '../components/Charts';
import InsightsFeed from '../components/InsightsFeed';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

type Log = {
  id: string;
  user_id: string;
  date: string;
  domain: string;
  metric: string;
  value: number;
  notes?: string | null;
};

type Insight = {
  id: string;
  user_id: string;
  description: string;
  correlation_score: number;
  created_at: string;
};

const DashboardPage: React.FC = () => {
  const { user, token, logout } = useAuth();
  const [logs, setLogs] = useState<Log[]>([]);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    if (!user || !token) return;
    
    try {
      const [logsResponse, insightsResponse] = await Promise.all([
        axios.get(`${API_BASE}/api/logs`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }),
        axios.get(`${API_BASE}/api/insights`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
      ]);
      
      setLogs(logsResponse.data);
      setInsights(insightsResponse.data);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [user, token]);

  const handleLogCreated = () => {
    loadData();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">CrossCoach</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Welcome, {user?.name || user?.email}
              </span>
              <button
                onClick={logout}
                className="text-sm text-gray-600 hover:text-gray-900 transition duration-200"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Forms */}
          <div className="lg:col-span-1 space-y-6">
            <LogEntryForm userId={user!.id} onLogCreated={handleLogCreated} token={token!} />
            <JournalEntry userId={user!.id} onEntryCreated={handleLogCreated} token={token!} />
          </div>

          {/* Right Column - Charts and Insights */}
          <div className="lg:col-span-2 space-y-6">
            <Charts logs={logs} />
            <InsightsFeed insights={insights} />
          </div>
        </div>

        {/* Recent Logs Section */}
        <div className="mt-8">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
            {logs.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>No logs yet. Start by adding your first entry!</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Domain
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Metric
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Value
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Notes
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {logs.slice(0, 10).map((log) => (
                      <tr key={log.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {new Date(log.date).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {log.domain}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {log.metric}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {log.value}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                          {log.notes || '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default DashboardPage; 