import { useState, useEffect } from 'react';
import api from '../api';

export const GlobalStats = () => {
  const [stats, setStats] = useState({ total_projects: 0, delayed_count: 0, warning_count: 0 });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await api.get('/stats/overview');
        setStats(res.data);
      } catch (err) {
        console.error('获取统计失败', err);
      }
    };
    fetchStats();
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ display: 'flex', gap: '16px', marginBottom: '1rem', padding: '8px', backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
      <div><strong>📁 项目总数</strong><br/>{stats.total_projects}</div>
      <div><strong>🔴 延期节点</strong><br/>{stats.delayed_count}</div>
      <div><strong>🟡 即将到期</strong><br/>{stats.warning_count}</div>
    </div>
  );
};