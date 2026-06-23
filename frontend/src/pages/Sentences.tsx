import { useState } from 'react';
import { useSentences } from '../hooks/useSentences';
import { api } from '../hooks/useApi';

export const Sentences = () => {
  const {
    sentences,
    total,
    loading,
    error,
    offset,
    setOffset,
    limit,
    createSentence,
    updateSentence,
    deleteSentence,
    search,
  } = useSentences(50);

  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState({ text: '' });
  const [searchQuery, setSearchQuery] = useState('');
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [relatedCounts, setRelatedCounts] = useState<{ recordings: number; history: number } | null>(null);
  const [countsLoading, setCountsLoading] = useState(false);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    setOffset(0);
    if (query.trim()) {
      search(query);
    } else {
      search('');
    }
  };

  const openAddForm = () => {
    setEditingId(null);
    setFormData({ text: '' });
    setShowForm(true);
  };

  const openEditForm = (sentence: { id: number; sentence_id: string; text: string }) => {
    setEditingId(sentence.id);
    setFormData({ text: sentence.text });
    setShowForm(true);
  };

  const cancelForm = () => {
    setShowForm(false);
    setEditingId(null);
    setFormData({ text: '' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingId) {
        await updateSentence(editingId, formData);
        setMessage({ type: 'success', text: 'Sentence updated successfully' });
      } else {
        await createSentence(formData.text);
        setMessage({ type: 'success', text: 'Sentence created successfully' });
      }
      cancelForm();
    } catch (err) {
      setMessage({
        type: 'error',
        text: err instanceof Error ? err.message : 'An error occurred',
      });
    }
  };

  const initiateDelete = async (sentenceDbId: number) => {
    setDeletingId(sentenceDbId);
    setCountsLoading(true);
    setRelatedCounts(null);
    try {
      const res = await api.getSentenceRelatedCounts(sentenceDbId);
      setRelatedCounts(res.data);
    } catch {
      setRelatedCounts({ recordings: 0, history: 0 });
    } finally {
      setCountsLoading(false);
    }
  };

  const confirmDelete = async () => {
    if (!deletingId) return;
    try {
      const result = await deleteSentence(deletingId);
      setMessage({
        type: 'success',
        text: result?.message || 'Sentence deleted successfully',
      });
    } catch (err) {
      setMessage({
        type: 'error',
        text: err instanceof Error ? err.message : 'Failed to delete',
      });
    } finally {
      setDeletingId(null);
      setRelatedCounts(null);
    }
  };

  const cancelDelete = () => {
    setDeletingId(null);
    setRelatedCounts(null);
  };

  const pages = Math.ceil(total / limit);
  const currentPage = Math.floor(offset / limit) + 1;

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Sentences</h1>
        <button
          onClick={openAddForm}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          {showForm ? '✕ Cancel' : '+ Add Sentence'}
        </button>
      </div>

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

      {showForm && (
        <div className="bg-white p-6 rounded-lg shadow-md mb-6">
          <h2 className="text-xl font-bold mb-4">
            {editingId ? 'Edit Sentence' : 'Add New Sentence'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <input
                type="text"
                placeholder="Twi sentence text"
                value={formData.text}
                onChange={(e) => setFormData({ text: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                required
              />
            </div>
            <button
              type="submit"
              className="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700"
            >
              {editingId ? 'Update' : 'Create Sentence'}
            </button>
          </form>
        </div>
      )}

      {/* Search Bar */}
      <div className="mb-6">
        <input
          type="text"
          placeholder="Search by Sentence ID or text..."
          value={searchQuery}
          onChange={handleSearch}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
        />
      </div>

      {/* Sentences Table */}
      {error && <div className="text-red-600 bg-red-50 p-4 rounded mb-6">{error}</div>}

      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : sentences.length === 0 ? (
        <div className="text-center py-12 text-gray-500">No sentences found</div>
      ) : (
        <>
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-6 py-3 text-left font-semibold text-gray-700">ID</th>
                    <th className="px-6 py-3 text-left font-semibold text-gray-700">Sentence Code</th>
                    <th className="px-6 py-3 text-left font-semibold text-gray-700">Twi Text</th>
                    <th className="px-6 py-3 text-left font-semibold text-gray-700">Created</th>
                    <th className="px-6 py-3 text-left font-semibold text-gray-700">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {sentences.map((s) => (
                    <tr key={s.id} className="border-t hover:bg-gray-50">
                      <td className="px-6 py-4 text-gray-900">{s.id}</td>
                      <td className="px-6 py-4 font-mono font-bold text-blue-600">{s.sentence_id}</td>
                      <td className="px-6 py-4 text-gray-900">{s.text}</td>
                      <td className="px-6 py-4 text-gray-600">
                        {new Date(s.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 space-x-2">
                        <button
                          onClick={() => openEditForm(s)}
                          className="text-blue-600 hover:underline"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => initiateDelete(s.id)}
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

      {/* Delete Confirmation Modal */}
      {deletingId !== null && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl max-w-md w-full mx-4">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Delete Sentence?</h3>

            {countsLoading ? (
              <p className="text-gray-600">Loading related data...</p>
            ) : relatedCounts ? (
              <div className="mb-4">
                <p className="text-gray-700 mb-2">
                  This will <strong>permanently delete</strong> the sentence and all associated data:
                </p>
                <ul className="list-disc list-inside text-red-600 space-y-1">
                  <li>{relatedCounts.recordings} related recording(s)</li>
                  <li>{relatedCounts.history} related history entry/entries</li>
                </ul>
                <p className="text-gray-500 text-sm mt-3">This action cannot be undone.</p>
              </div>
            ) : (
              <p className="text-gray-600 mb-4">Are you sure you want to delete this sentence and all related data?</p>
            )}

            <div className="flex justify-end gap-3">
              <button
                onClick={cancelDelete}
                className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
              >
                Delete Permanently
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
