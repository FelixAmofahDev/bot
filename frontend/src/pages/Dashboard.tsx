import { useEffect, useState } from 'react';
import { api } from '../hooks/useApi';
import type { DashboardStats, Recording } from '../types';

const StatCard = ({ title, value, icon }: { title: string; value: number; icon: string }) => (
  <div className="bg-white p-6 rounded-lg shadow-md">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-gray-600">{title}</p>
        <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
      </div>
      <span className="text-4xl">{icon}</span>
    </div>
  </div>
);

export const Dashboard = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recent, setRecent] = useState<Recording[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [statsRes, recentRes] = await Promise.all([
          api.getDashboardStats(),
          api.getRecentRecordings(10),
        ]);
        setStats(statsRes.data);
        setRecent(recentRes.data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="text-center py-12">Loading...</div>;
  if (error) return <div className="text-red-600 bg-red-50 p-4 rounded">{error}</div>;
  if (!stats) return null;

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        <StatCard
          title="Total Participants"
          value={stats.total_participants}
          icon="👥"
        />
        <StatCard
          title="Total Recordings"
          value={stats.total_recordings}
          icon="🎙️"
        />
        <StatCard
          title="Total Sentences"
          value={stats.total_sentences}
          icon="📝"
        />
        <StatCard
          title="Completed"
          value={stats.total_completed}
          icon="✅"
        />
        <StatCard
          title="Today"
          value={stats.submitted_today}
          icon="📅"
        />
      </div>

      {/* Recent Recordings */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Recordings</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left font-semibold text-gray-700">
                  Speaker ID
                </th>
                <th className="px-4 py-2 text-left font-semibold text-gray-700">
                  Sentence
                </th>
                <th className="px-4 py-2 text-left font-semibold text-gray-700">
                  Text
                </th>
                <th className="px-4 py-2 text-left font-semibold text-gray-700">
                  Date
                </th>
              </tr>
            </thead>
            <tbody>
              {recent.map((rec) => (
                <tr key={rec.id} className="border-t hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-900">{rec.speaker_id}</td>
                  <td className="px-4 py-3 text-gray-600">{rec.sentence_code}</td>
                  <td className="px-4 py-3 text-gray-600 truncate">{rec.twi_text}</td>
                  <td className="px-4 py-3 text-gray-600">
                    {new Date(rec.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
