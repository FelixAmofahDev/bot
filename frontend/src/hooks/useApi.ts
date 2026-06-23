import axios from 'axios';
import type { Participant, Recording, DashboardStats, CompletionStat, PaginatedResponse, Sentence } from '../types';

// Use relative path for API - works in both development and production
// In dev: http://localhost:8000/api
// In prod: https://your-render-app.onrender.com/api
const API_BASE = '/api';

export const api = {
  // Sentences
  getSentences: (limit = 50, offset = 0) =>
    axios.get<PaginatedResponse<Sentence>>(`${API_BASE}/sentences`, {
      params: { limit, offset },
    }),

  searchSentences: (query: string, limit = 50, offset = 0) =>
    axios.get<PaginatedResponse<Sentence>>(`${API_BASE}/sentences/search`, {
      params: { q: query, limit, offset },
    }),

  getSentence: (sentenceId: number) =>
    axios.get<Sentence>(`${API_BASE}/sentences/${sentenceId}`),

  getSentenceRelatedCounts: (sentenceId: number) =>
    axios.get<{ recordings: number; history: number }>(`${API_BASE}/sentences/${sentenceId}/related-counts`),

  createSentence: (text: string) =>
    axios.post<Sentence>(`${API_BASE}/sentences`, { text }),

  updateSentence: (sentenceId: number, data: { sentence_id?: string; text?: string }) =>
    axios.put(`${API_BASE}/sentences/${sentenceId}`, data),

  deleteSentence: (sentenceId: number) =>
    axios.delete(`${API_BASE}/sentences/${sentenceId}`),

  // Participants
  getParticipants: (limit = 50, offset = 0) =>
    axios.get<PaginatedResponse<Participant>>(`${API_BASE}/participants`, {
      params: { limit, offset },
    }),

  searchParticipants: (query: string, limit = 50, offset = 0) =>
    axios.get<PaginatedResponse<Participant>>(`${API_BASE}/participants/search`, {
      params: { q: query, limit, offset },
    }),

  getParticipant: (speakerId: string) =>
    axios.get<Participant>(`${API_BASE}/participants/${speakerId}`),

  createParticipant: (name: string, age: string, gender: string, region: string) =>
    axios.post(`${API_BASE}/participants`, { name, age, gender, region }),

  updateParticipant: (speakerId: string, data: Partial<Participant>) =>
    axios.put(`${API_BASE}/participants/${speakerId}`, data),

  deleteParticipant: (speakerId: string) =>
    axios.delete(`${API_BASE}/participants/${speakerId}`),

  // Recordings
  getRecordings: (limit = 50, offset = 0) =>
    axios.get<PaginatedResponse<Recording>>(`${API_BASE}/recordings`, {
      params: { limit, offset },
    }),

  searchRecordings: (query: string, limit = 50, offset = 0) =>
    axios.get<PaginatedResponse<Recording>>(`${API_BASE}/recordings/search`, {
      params: { q: query, limit, offset },
    }),

  getRecordingsByDate: (startDate: string, endDate: string, limit = 50, offset = 0) =>
    axios.get<PaginatedResponse<Recording>>(`${API_BASE}/recordings/by-date`, {
      params: { start_date: startDate, end_date: endDate, limit, offset },
    }),

  getRecordingsBySpeaker: (speakerId: string, limit = 50, offset = 0) =>
    axios.get<PaginatedResponse<Recording>>(`${API_BASE}/recordings/by-speaker/${speakerId}`, {
      params: { limit, offset },
    }),

  downloadAudio: (recordingId: number) =>
    `${API_BASE}/recordings/${recordingId}/audio`,

  deleteRecording: (recordingId: number) =>
    axios.delete(`${API_BASE}/recordings/${recordingId}`),

  // Dashboard
  getDashboardStats: () =>
    axios.get<DashboardStats>(`${API_BASE}/dashboard/stats`),

  getRecentRecordings: (limit = 10) =>
    axios.get<Recording[]>(`${API_BASE}/dashboard/recent-recordings`, {
      params: { limit },
    }),

  getCompletionStats: () =>
    axios.get<CompletionStat[]>(`${API_BASE}/dashboard/completion-stats`),
};
