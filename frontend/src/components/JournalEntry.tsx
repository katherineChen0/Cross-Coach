import React, { useState } from 'react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

type JournalEntryProps = {
  userId: string;
  onEntryCreated: () => void;
};

const JournalEntry: React.FC<JournalEntryProps> = ({ userId, onEntryCreated }) => {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;

    setLoading(true);

    try {
      const payload = {
        user_id: userId,
        log_date: new Date().toISOString().slice(0, 10),
        domain: 'journaling',
        note: content,
        value: null,
        metrics: null
      };

      await axios.post(`${API_BASE}/api/logs`, payload);
      
      // Reset form
      setContent('');
      onEntryCreated();
    } catch (error) {
      console.error('Error creating journal entry:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Journal Entry</h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="journalContent" className="block text-sm font-medium text-gray-700 mb-2">
            What's on your mind today?
          </label>
          <textarea
            id="journalContent"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={6}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            placeholder="Reflect on your day, goals, challenges, or anything you'd like to remember..."
          />
        </div>

        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-500">
            {content.length} characters
          </span>
          <button
            type="submit"
            disabled={loading || !content.trim()}
            className="bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {loading ? 'Saving...' : 'Save Entry'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default JournalEntry; 