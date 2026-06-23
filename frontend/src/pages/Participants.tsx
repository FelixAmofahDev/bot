import { useState } from 'react';
import { useParticipants } from '../hooks/useParticipants';

const AGE_RANGES = [
  "Under 18",
  "18 - 25",
  "26 - 35",
  "36 - 45",
  "46 - 55",
  "56 - 65",
  "66 and above",
];

const GHANA_REGIONS = [
  "AHAFO",
  "ASHANTI",
  "BONO EAST",
  "BRONG AHAFO",
  "CENTRAL",
  "EASTERN",
  "GREATER ACCRA",
  "NORTH EAST",
  "NORTHERN",
  "OTI",
  "SAVANNAH",
  "UPPER EAST",
  "UPPER WEST",
  "VOLTA",
  "WESTERN",
  "WESTERN NORTH",
];

const GENDERS = ["Male", "Female", "Other"];

export const Participants = () => {
  const {
    participants,
    total,
    loading,
    error,
    offset,
    setOffset,
    limit,
    createParticipant,
    updateParticipant,
    deleteParticipant,
    search,
  } = useParticipants(50);

  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState({ name: '', age: '', gender: '', region: '' });
  const [searchQuery, setSearchQuery] = useState('');
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingId) {
        await updateParticipant(editingId, formData);
        setMessage({ type: 'success', text: 'Participant updated successfully' });
        setEditingId(null);
      } else {
        const result = await createParticipant(formData.name, formData.age, formData.gender, formData.region);
        setMessage({
          type: 'success',
          text: `Participant created with ID: ${result.speaker_id}`,
        });
      }
      setFormData({ name: '', age: '', gender: '', region: '' });
      setShowForm(false);
    } catch (err) {
      setMessage({
        type: 'error',
        text: err instanceof Error ? err.message : 'An error occurred',
      });
    }
  };

  const handleDelete = async (speakerId: string) => {
    if (!confirm(`Delete participant ${speakerId}?`)) return;
    try {
      await deleteParticipant(speakerId);
      setMessage({ type: 'success', text: 'Participant deleted' });
    } catch (err) {
      setMessage({
        type: 'error',
        text: err instanceof Error ? err.message : 'Failed to delete',
      });
    }
  };

  const pages = Math.ceil(total / limit);
  const currentPage = Math.floor(offset / limit) + 1;

  const selectClass = "px-4 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-600 focus:border-transparent";
  const inputClass = "px-4 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-600 focus:border-transparent";

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Participants</h1>
        <button
          onClick={() => {
            if (showForm && !editingId) {
              setShowForm(false);
              setFormData({ name: '', age: '', gender: '', region: '' });
            } else {
              setShowForm(true);
              setEditingId(null);
              setFormData({ name: '', age: '', gender: '', region: '' });
            }
          }}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          {showForm ? '✕ Cancel' : '+ Add Participant'}
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

      {/* Add/Edit Form */}
      {showForm && (
        <div className="bg-white p-6 rounded-lg shadow-md mb-6">
          <h2 className="text-xl font-bold mb-4">
            {editingId ? 'Edit Participant' : 'Add New Participant'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <input
                type="text"
                placeholder="Full Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className={inputClass}
                required
              />
              <select
                value={formData.age}
                onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                className={selectClass}
                required
              >
                <option value="">Select Age Range</option>
                {AGE_RANGES.map((r) => <option key={r} value={r}>{r}</option>)}
              </select>
              <select
                value={formData.gender}
                onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                className={selectClass}
                required
              >
                <option value="">Select Gender</option>
                {GENDERS.map((g) => <option key={g} value={g}>{g}</option>)}
              </select>
              <select
                value={formData.region}
                onChange={(e) => setFormData({ ...formData, region: e.target.value })}
                className={selectClass}
                required
              >
                <option value="">Select Region</option>
                {GHANA_REGIONS.map((r) => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
            <button
              type="submit"
              className="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700"
            >
              {editingId ? 'Update' : 'Create Participant'}
            </button>
          </form>
        </div>
      )}

      {/* Search Bar */}
      <div className="mb-6">
        <input
          type="text"
          placeholder="Search by Speaker ID, name, age, gender, or region..."
          value={searchQuery}
          onChange={handleSearch}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
        />
      </div>

      {/* Participants Table */}
      {error && <div className="text-red-600 bg-red-50 p-4 rounded mb-6">{error}</div>}

      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : (
        <>
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-6 py-3 text-left font-semibold text-gray-700">Speaker ID</th>
                    <th className="px-6 py-3 text-left font-semibold text-gray-700">Name</th>
                    <th className="px-6 py-3 text-left font-semibold text-gray-700">Age</th>
                    <th className="px-6 py-3 text-left font-semibold text-gray-700">Gender</th>
                    <th className="px-6 py-3 text-left font-semibold text-gray-700">Region</th>
                    <th className="px-6 py-3 text-left font-semibold text-gray-700">Created</th>
                    <th className="px-6 py-3 text-left font-semibold text-gray-700">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {participants.map((p) => (
                    <tr key={p.id} className="border-t hover:bg-gray-50">
                      <td className="px-6 py-4 font-mono font-bold text-blue-600">{p.speaker_id}</td>
                      <td className="px-6 py-4 text-gray-900">{p.name}</td>
                      <td className="px-6 py-4 text-gray-900">{p.age}</td>
                      <td className="px-6 py-4 text-gray-900">{p.gender}</td>
                      <td className="px-6 py-4 text-gray-900">{p.region}</td>
                      <td className="px-6 py-4 text-gray-600">
                        {new Date(p.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 space-x-2">
                        <button
                          onClick={() => {
                            setEditingId(p.speaker_id);
                            setFormData({
                              name: p.name,
                              age: p.age,
                              gender: p.gender,
                              region: p.region,
                            });
                            setShowForm(true);
                          }}
                          className="text-blue-600 hover:underline"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(p.speaker_id)}
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
