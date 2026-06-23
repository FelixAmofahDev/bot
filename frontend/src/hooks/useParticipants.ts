import { useState, useEffect } from 'react';
import { api } from './useApi';
import type { Participant } from '../types';

export const useParticipants = (limit = 50) => {
  const [data, setData] = useState<Participant[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);

  const fetch = async (searchQuery?: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = searchQuery
        ? await api.searchParticipants(searchQuery, limit, offset)
        : await api.getParticipants(limit, offset);
      setData(response.data.data);
      setTotal(response.data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch participants');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetch();
  }, [offset]);

  const createParticipant = async (name: string, age: string, gender: string, region: string) => {
    try {
      const res = await api.createParticipant(name, age, gender, region);
      setOffset(0);
      await fetch();
      return res.data;
    } catch (err) {
      throw err;
    }
  };

  const updateParticipant = async (speakerId: string, updates: Partial<Participant>) => {
    try {
      await api.updateParticipant(speakerId, updates);
      await fetch();
    } catch (err) {
      throw err;
    }
  };

  const deleteParticipant = async (speakerId: string) => {
    try {
      await api.deleteParticipant(speakerId);
      await fetch();
    } catch (err) {
      throw err;
    }
  };

  const search = async (query: string) => {
    setOffset(0);
    await fetch(query);
  };

  return {
    participants: data,
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
  };
};
