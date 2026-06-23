import { useState, useEffect } from 'react';
import { api } from './useApi';
import type { Recording } from '../types';

export const useRecordings = (limit = 50) => {
  const [data, setData] = useState<Recording[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);

  const fetch = async (options?: { search?: string; speakerId?: string; startDate?: string; endDate?: string }) => {
    setLoading(true);
    setError(null);
    try {
      let response;
      if (options?.search) {
        response = await api.searchRecordings(options.search, limit, offset);
      } else if (options?.speakerId) {
        response = await api.getRecordingsBySpeaker(options.speakerId, limit, offset);
      } else if (options?.startDate && options?.endDate) {
        response = await api.getRecordingsByDate(options.startDate, options.endDate, limit, offset);
      } else {
        response = await api.getRecordings(limit, offset);
      }
      setData(response.data.data);
      setTotal(response.data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch recordings');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetch();
  }, [offset]);

  const deleteRecording = async (recordingId: number) => {
    try {
      await api.deleteRecording(recordingId);
      setOffset(0);
      await fetch();
    } catch (err) {
      throw err;
    }
  };

  const getAudioUrl = (recordingId: number) => api.downloadAudio(recordingId);

  const search = async (query: string) => {
    setOffset(0);
    await fetch({ search: query });
  };

  const filterBySpeaker = async (speakerId: string) => {
    setOffset(0);
    await fetch({ speakerId });
  };

  const filterByDate = async (startDate: string, endDate: string) => {
    setOffset(0);
    await fetch({ startDate, endDate });
  };

  return {
    recordings: data,
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
  };
};
