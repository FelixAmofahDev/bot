import { useState, useEffect } from 'react';
import { api } from './useApi';
import type { Sentence } from '../types';

export const useSentences = (limit = 50) => {
  const [data, setData] = useState<Sentence[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);

  const fetch = async (searchQuery?: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = searchQuery
        ? await api.searchSentences(searchQuery, limit, offset)
        : await api.getSentences(limit, offset);
      setData(response.data.data);
      setTotal(response.data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch sentences');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetch();
  }, [offset]);

  const createSentence = async (text: string) => {
    try {
      const res = await api.createSentence(text);
      setOffset(0);
      await fetch();
      return res.data;
    } catch (err) {
      throw err;
    }
  };

  const updateSentence = async (sentenceDbId: number, updates: { sentence_id?: string; text?: string }) => {
    try {
      await api.updateSentence(sentenceDbId, updates);
      await fetch();
    } catch (err) {
      throw err;
    }
  };

  const deleteSentence = async (sentenceDbId: number) => {
    try {
      const res = await api.deleteSentence(sentenceDbId);
      await fetch();
      return res.data;
    } catch (err) {
      throw err;
    }
  };

  const search = async (query: string) => {
    setOffset(0);
    await fetch(query);
  };

  return {
    sentences: data,
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
  };
};
