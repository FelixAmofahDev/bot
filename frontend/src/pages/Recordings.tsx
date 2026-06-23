import { useState, useRef } from 'react';
import { useRecordings } from '../hooks/useRecordings';

export const Recordings = () => {
  const {
    recordings,
    total,
    loading,
    error,
    offset,
    setOffset,
    limit,
    deleteRecording,
    getAudioUrl,
    search,
    filterBySpeaker,
    filterByDate,
  } = useRecordings(50);

  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'speaker' | 'date'>('all');
  const [filterValue, setFilterValue] = useState('');
  const [endDate, setEndDate] = useState('');
  const [playingId, setPlayingId] = useState<number | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    setFilterType('all');
    setOffset(0);
    if (query.trim()) {
      search(query);
    }
  };

  const handleFilterChange = (type: 'speaker' | 'date') => {
    setFilterType(type);
    setSearchQuery('');
    setOffset(0);
  };

  const handleApplyFilter = async () => {
    try {
      if (filterType === 'speaker' && filterValue) {
        await filterBySpeaker(filterValue);
      } else if (filterType === 'date' && filterValue && endDate) {
        await filterByDate(filterValue, endDate);
      }
    } catch (err) {
      setMessage({
        type: 'error',
        text: err instanceof Error ? err.message : 'Filter failed',
      });
    }
  };

  const handleDelete = async (recordingId: number) => {
    if (!confirm('Delete this recording?')) return;
    try {
      await deleteRecording(recordingId);
      setMessage({ type: 'success', text: 'Recording deleted' });
    } catch (err) {
      setMessage({
        type: 'error',
        text: err instanceof Error ? err.message : 'Failed to delete',
      });
    }
  };

  const handlePlayAudio = (recordingId: number) => {
    setPlayingId(recordingId);
  };

  const pages = Math.ceil(total / limit);
  const currentPage = Math.floor(offset / limit) + 1;

  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Recordings</h1>

      {message && (
        <div
          className={`p-4 rounded mb-6 ${
            message.type === 'success'
              ? 'bg-green-50 text-green-800'
              : 'bg-red-50 text-red-800'
          }`}
        >
          {message.text}
        </div>
      )}

      {/* Search and Filter Section */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Search
            </label>
            <input
              type="text"
              placeholder="Speaker ID or Sentence ID..."
              value={searchQuery}
              onChange={handleSearch}
              className="w-full px-4 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-600 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Filter Type
            </label>
            <div className="flex gap-2">
              <button
                onClick={() => handleFilterChange('speaker')}
                className={`flex-1 px-3 py-2 rounded text-sm font-medium transition-colors ${
                  filterType === 'speaker'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                By Speaker
              </button>
              <button
                onClick={() => handleFilterChange('date')}
                className={`flex-1 px-3 py-2 rounded text-sm font-medium transition-colors ${
                  filterType === 'date'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                By Date
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Filter Value
            </label>
            {filterType === 'speaker' ? (
              <input
                type="text"
                placeholder="Speaker ID (e.g., SPK0001)"
                value={filterValue}
                onChange={(e) => setFilterValue(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-600 focus:border-transparent"
              />
            ) : (
              <input
                type="date"
                value={filterValue}
                onChange={(e) => setFilterValue(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-600 focus:border-transparent"
              />
            )}
          </div>
        </div>

        {filterType === 'date' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                End Date
              </label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-600 focus:border-transparent"
              />
            </div>
          </div>
        )}

        <button
          onClick={handleApplyFilter}
          className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
        >
          Apply Filter
        </button>
      </div>

      {/* Recordings Table */}
      {error && <div className="text-red-600 bg-red-50 p-4 rounded mb-6">{error}</div>}

      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : recordings.length === 0 ? (
        <div className="text-center py-12 text-gray-500">No recordings found</div>
      ) : (
        <>
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-4 py-3 text-left font-semibold text-gray-700">
                      Speaker ID
                    </th>
                    <th className="px-4 py-3 text-left font-semibold text-gray-700">
                      Telegram ID
                    </th>
                    <th className="px-4 py-3 text-left font-semibold text-gray-700">
                      Sentence ID
                    </th>
                    <th className="px-4 py-3 text-left font-semibold text-gray-700">
                      Twi Text
                    </th>
                    <th className="px-4 py-3 text-left font-semibold text-gray-700">
                      Audio
                    </th>
                    <th className="px-4 py-3 text-left font-semibold text-gray-700">
                      Date
                    </th>
                    <th className="px-4 py-3 text-left font-semibold text-gray-700">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {recordings.map((rec) => (
                    <tr key={rec.id} className="border-t hover:bg-gray-50">
                      <td className="px-4 py-3 font-mono font-bold text-blue-600">
                        {rec.speaker_id}
                      </td>
                      <td className="px-4 py-3 text-gray-600">{rec.telegram_id}</td>
                      <td className="px-4 py-3 text-gray-600">{rec.sentence_code}</td>
                      <td className="px-4 py-3 text-gray-600 truncate max-w-xs">
                        {rec.twi_text}
                      </td>
                      <td className="px-4 py-3">
                        <button
                          onClick={() => handlePlayAudio(rec.id)}
                          className="text-blue-600 hover:underline flex items-center gap-1"
                        >
                          ▶ Play
                        </button>
                        {playingId === rec.id && (
                          <audio
                            ref={audioRef}
                            src={getAudioUrl(rec.id)}
                            controls
                            autoPlay
                            className="mt-2 w-full max-w-xs"
                          />
                        )}
                      </td>
                      <td className="px-4 py-3 text-gray-600">
                        {new Date(rec.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3 space-x-2">
                        <a
                          href={getAudioUrl(rec.id)}
                          download
                          className="text-green-600 hover:underline"
                        >
                          Download
                        </a>
                        <button
                          onClick={() => handleDelete(rec.id)}
                          className="text-red-600 hover:underline"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Pagination */}
          {pages > 1 && (
            <div className="mt-6 flex justify-center gap-2">
              <button
                onClick={() => setOffset(Math.max(0, offset - limit))}
                disabled={offset === 0}
                className="px-4 py-2 border rounded disabled:opacity-50"
              >
                ← Previous
              </button>
              <span className="px-4 py-2">
                Page {currentPage} of {pages}
              </span>
              <button
                onClick={() => setOffset(offset + limit)}
                disabled={currentPage >= pages}
                className="px-4 py-2 border rounded disabled:opacity-50"
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};
