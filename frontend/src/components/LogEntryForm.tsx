import React, { useState } from 'react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

type LogEntryFormProps = {
  userId: string;
  onLogCreated: () => void;
};

const domains = [
  'fitness',
  'climbing',
  'coding',
  'mood',
  'sleep',
  'journaling',
  'nutrition',
  'meditation',
  'reading',
  'social'
] as const;

const metricNames = {
  fitness: ['workout_duration', 'calories_burned', 'strength_level', 'cardio_minutes'],
  climbing: ['grade', 'routes_completed', 'session_duration', 'technique_rating'],
  coding: ['hours_coded', 'problems_solved', 'projects_worked', 'learning_hours'],
  mood: ['happiness_level', 'energy_level', 'stress_level', 'motivation'],
  sleep: ['hours_slept', 'sleep_quality', 'bedtime', 'wake_time'],
  journaling: ['entries_written', 'reflection_time', 'gratitude_count'],
  nutrition: ['calories_consumed', 'protein_grams', 'water_intake', 'meals_eaten'],
  meditation: ['minutes_meditated', 'sessions_completed', 'focus_rating'],
  reading: ['pages_read', 'books_completed', 'reading_time'],
  social: ['social_interactions', 'quality_time', 'new_connections']
};

const LogEntryForm: React.FC<LogEntryFormProps> = ({ userId, onLogCreated }) => {
  const [domain, setDomain] = useState<typeof domains[number]>('fitness');
  const [metricName, setMetricName] = useState('');
  const [value, setValue] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        user_id: userId,
        log_date: new Date().toISOString().slice(0, 10),
        domain,
        value: value === '' ? null : Number(value),
        metrics: metricName ? { [metricName]: value === '' ? null : Number(value) } : null,
        note: notes || null
      };

      await axios.post(`${API_BASE}/api/logs`, payload);
      
      // Reset form
      setValue('');
      setNotes('');
      setMetricName('');
      
      onLogCreated();
    } catch (error) {
      console.error('Error creating log:', error);
    } finally {
      setLoading(false);
    }
  };

  const currentMetrics = metricNames[domain] || [];

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Log New Entry</h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="domain" className="block text-sm font-medium text-gray-700 mb-2">
              Domain
            </label>
            <select
              id="domain"
              value={domain}
              onChange={(e) => {
                setDomain(e.target.value as typeof domains[number]);
                setMetricName('');
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {domains.map((d) => (
                <option key={d} value={d}>
                  {d.charAt(0).toUpperCase() + d.slice(1)}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="metricName" className="block text-sm font-medium text-gray-700 mb-2">
              Metric Name
            </label>
            <select
              id="metricName"
              value={metricName}
              onChange={(e) => setMetricName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select a metric</option>
              {currentMetrics.map((metric) => (
                <option key={metric} value={metric}>
                  {metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label htmlFor="value" className="block text-sm font-medium text-gray-700 mb-2">
            Value
          </label>
          <input
            id="value"
            type="number"
            step="0.01"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Enter numeric value"
          />
        </div>

        <div>
          <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-2">
            Notes
          </label>
          <textarea
            id="notes"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Add any additional notes or observations..."
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
        >
          {loading ? 'Logging...' : 'Log Entry'}
        </button>
      </form>
    </div>
  );
};

export default LogEntryForm; 