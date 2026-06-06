import { useState, useEffect } from 'react';
import { useProject } from '../contexts/ProjectContext';
import api from '../api';

interface OverdueNode {
  id: number;
  node_name: string;
  planned_end: string;
  overdue_days: number;
  reminder_muted: boolean;
  reminder_last: string | null;
}

export const OverdueReminders = () => {
  const { currentProject, triggerRefreshNodes } = useProject();
  const [overdueNodes, setOverdueNodes] = useState<OverdueNode[]>([]);
  const [loading, setLoading] = useState(false);

  // 从当前项目的节点中筛选逾期节点（status='delayed' 或 'overdue' 且未完成）
  const fetchOverdueNodes = async () => {
    if (!currentProject) return;
    setLoading(true);
    try {
      const res = await api.get(`/projects/${currentProject.id}/nodes`);
      const nodes = res.data;
      const today = new Date().toISOString().split('T')[0];
      const overdue = nodes
        .filter((n: any) => (n.status === 'delayed' || n.status === 'overdue') && n.actual_end === null)
        .map((n: any) => {
          const plannedEnd = n.planned_end ? n.planned_end.split('T')[0] : '';
          const overdueDays = plannedEnd ? Math.max(0, Math.floor((new Date(today).getTime() - new Date(plannedEnd).getTime()) / (1000 * 3600 * 24))) : 0;
          return {
            id: n.id,
            node_name: n.node_name,
            planned_end: plannedEnd,
            overdue_days: overdueDays,
            reminder_muted: n.reminder_muted || false,
            reminder_last: n.reminder_last || null,
          };
        })
        .filter((n: OverdueNode) => !n.reminder_muted); // 过滤掉永久静默的节点
      setOverdueNodes(overdue);
    } catch (err) {
      console.error('获取逾期节点失败', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOverdueNodes();
    // 每30秒刷新一次逾期提醒（可选）
    const interval = setInterval(fetchOverdueNodes, 30000);
    return () => clearInterval(interval);
  }, [currentProject]);

  // 标记完成（复用已有的节点完成逻辑）
  const markComplete = async (nodeId: number) => {
    try {
      await api.put(`/projects/nodes/${nodeId}`, {
        actual_end: new Date().toISOString(),
        status: 'done',
        progress_percent: 100,
      });
      triggerRefreshNodes();
      fetchOverdueNodes();
    } catch (err) {
      console.error('标记完成失败', err);
    }
  };

  // 暂不处理
  const snoozeReminder = async (nodeId: number) => {
    try {
      await api.post(`/projects/nodes/${nodeId}/remind-snooze`);
      fetchOverdueNodes();
    } catch (err) {
      console.error('暂不处理失败', err);
    }
  };

  // 不再提醒
  const muteReminder = async (nodeId: number) => {
    try {
      await api.post(`/projects/nodes/${nodeId}/remind-mute`);
      fetchOverdueNodes();
    } catch (err) {
      console.error('不再提醒失败', err);
    }
  };

  if (!currentProject) return null;
  if (loading) return <div>加载逾期提醒...</div>;
  if (overdueNodes.length === 0) return null;

  return (
    <div style={{ marginBottom: '1rem', padding: '8px', backgroundColor: '#fff3e0', borderLeft: '4px solid #ff9800' }}>
      <h4>⚠️ 逾期节点提醒</h4>
      {overdueNodes.map(node => (
        <div key={node.id} style={{ marginBottom: '8px', padding: '8px', backgroundColor: '#fff', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span>
            <strong>{node.node_name}</strong> 已逾期 <strong>{node.overdue_days}</strong> 天
          </span>
          <div>
            <button onClick={() => markComplete(node.id)} style={{ marginRight: '8px' }}>✅ 标记完成</button>
            <button onClick={() => snoozeReminder(node.id)} style={{ marginRight: '8px' }}>⏸️ 暂不处理</button>
            <button onClick={() => muteReminder(node.id)}>🔕 不再提醒</button>
          </div>
        </div>
      ))}
    </div>
  );
};