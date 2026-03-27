import { useCallback, useEffect, useRef, useState } from 'react';

export default function useRemoteResource(loader, deps = []) {
  const loaderRef = useRef(loader);
  loaderRef.current = loader;

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [data, setData] = useState(null);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const result = await loaderRef.current();
      setData(result);
      return result;
    } catch (err) {
      const message = err?.message || 'A apărut o eroare la încărcarea datelor.';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load().catch(() => {});
  }, deps);

  return { loading, error, data, load, setData };
}
