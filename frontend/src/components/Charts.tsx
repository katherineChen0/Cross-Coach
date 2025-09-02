import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

type Log = {
  id: string;
  user_id: string;
  date: string;
  domain: string;
  metric: string;
  value: number;
  notes?: string | null;
};

type ChartsProps = {
  logs: Log[];
};

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

const Charts: React.FC<ChartsProps> = ({ logs }) => {
  const chartData = useMemo(() => {
    // Group logs by date and domain
    const groupedByDate = logs.reduce((acc, log) => {
      const date = log.date;
      if (!acc[date]) {
        acc[date] = {};
      }
      acc[date][log.domain] = log.value;
      return acc;
    }, {} as Record<string, Record<string, number>>);

    // Convert to array format for charts
    return Object.entries(groupedByDate)
      .map(([date, domains]) => ({
        date,
        ...domains
      }))
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
      .slice(-30); // Last 30 days
  }, [logs]);

  const domainDistribution = useMemo(() => {
    const domainCounts = logs.reduce((acc, log) => {
      acc[log.domain] = (acc[log.domain] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return Object.entries(domainCounts).map(([domain, count]) => ({
      name: domain.charAt(0).toUpperCase() + domain.slice(1),
      value: count
    }));
  }, [logs]);

  const recentLogs = useMemo(() => {
    return logs
      .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
      .slice(0, 10);
  }, [logs]);

  if (logs.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Charts & Analytics</h3>
        <div className="text-center py-8 text-gray-500">
          <p>No data available yet. Start logging entries to see your progress!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Time Series Chart */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Progress Over Time</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            {Object.keys(chartData[0] || {}).filter(key => key !== 'date').map((domain, index) => (
              <Line
                key={domain}
                type="monotone"
                dataKey={domain}
                stroke={COLORS[index % COLORS.length]}
                strokeWidth={2}
                dot={{ fill: COLORS[index % COLORS.length] }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Domain Distribution */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Activity by Domain</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={domainDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {domainDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-3">
            {recentLogs.map((log) => (
              <div key={log.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">{log.domain}</p>
                  <p className="text-sm text-gray-600">{log.metric}</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-gray-900">{log.value}</p>
                  <p className="text-xs text-gray-500">
                    {new Date(log.date).toLocaleDateString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Value Distribution */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Value Distribution by Domain</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            {Object.keys(chartData[0] || {}).filter(key => key !== 'date').map((domain, index) => (
              <Bar
                key={domain}
                dataKey={domain}
                fill={COLORS[index % COLORS.length]}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default Charts; 