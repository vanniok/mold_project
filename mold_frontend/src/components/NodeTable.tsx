import { useState, useEffect } from 'react';
import api from '../api';
import { useProject } from '../contexts/ProjectContext';

interface Node {
  id: number;
  node_name: string;
  planned_start: string | null;
  planned_end: string | null;
  actual_start: string | null;
  actual_end: string | null;
  status: string;
  responsible_person: string | null;
  progress_percent: number;
  display_order: number;
}

const toDateInput = (iso: string | null) => {
  if (!iso) return '';
  return iso.split('T')[0];
};

const calcProgressTime = (node: Node): number => {
  if (node.actual_end && node.actual_start) {
    const start = new Date(node.actual_start);
    const end = new Date(node.actual_end);
    return Math.floor((end.getTime() - start.getTime()) / (1000 * 3600 * 24));
  } else if (node.actual_start && !node.actual_end) {
    const start = new Date(node.actual_start);
    const today = new Date();
    return Math.max(0, Math.floor((today.getTime() - start.getTime()) / (1000 * 3600 * 24)));
  } else {
    return 0;
  }
};

export const NodeTable = () => {
  const { currentProject, refreshNodes, triggerRefreshNodes } = useProject();
  const [nodes, setNodes] = useState<Node[]>([]);
  const [loading, setLoading] = useState(false);
  const [pendingUpdates, setPendingUpdates] = useState<Map<number, Partial<Node>>>(new Map());
  const [editingCell, setEditingCell] = useState<{ nodeId: number; field: keyof Node } | null>(null);
  const [editValue, setEditValue] = useState<string>('');

  useEffect(() => {
    if (currentProject) {
      fetchNodes();
    } else {
      setNodes([]);
      clearPending();
    }
  }, [currentProject, refreshNodes]);

  const fetchNodes = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/projects/${currentProject!.id}/nodes`);
      setNodes(res.data);
      clearPending();
    } catch (err) {
      console.error('加载节点失败', err);
    } finally {
      setLoading(false);
    }
  };

  const clearPending = () => {
    setPendingUpdates(new Map());
  };

  const saveAllChanges = async () => {
    if (pendingUpdates.size === 0) return;
    
    const updatePromises: Promise<any>[] = [];
    for (const [nodeId, updates] of pendingUpdates.entries()) {
      if (Object.keys(updates).length === 0) continue;
      updatePromises.push(api.put(`/projects/nodes/${nodeId}`, updates));
    }
    
    if (updatePromises.length === 0) return;
    
    try {
      await Promise.all(updatePromises);
      triggerRefreshNodes();
      clearPending();
    } catch (err) {
      console.error('批量保存失败', err);
    }
  };

  const discardAllChanges = () => {
    if (pendingUpdates.size === 0) return;
    clearPending();
  };

  const getDisplayValue = (node: Node, field: keyof Node) => {
    const pending = pendingUpdates.get(node.id);
    if (pending && field in pending) {
      const val = pending[field];
      if (field === 'actual_start' || field === 'actual_end' || field === 'planned_start' || field === 'planned_end') {
        return val ? toDateInput(val as string) : '';
      }
      return val;
    }
    const original = node[field];
    if (field === 'actual_start' || field === 'actual_end' || field === 'planned_start' || field === 'planned_end') {
      return original ? toDateInput(original as string) : '';
    }
    return original;
  };

  const startEdit = (nodeId: number, field: keyof Node, currentDisplayValue: any) => {
    setEditingCell({ nodeId, field });
    setEditValue(String(currentDisplayValue ?? ''));
  };

  const applyEdit = (nodeId: number, field: keyof Node) => {
    const value = editValue;
    setEditingCell(null);
    
    const currentNode = nodes.find(n => n.id === nodeId);
    if (!currentNode) return;
    
    let updates: Partial<Node> = {};
    
    if (field === 'planned_start' || field === 'planned_end' || field === 'actual_start' || field === 'actual_end') {
      let newDate: string | null = null;
      if (value && value.trim() !== '') {
        const date = new Date(value);
        if (!isNaN(date.getTime())) {
          newDate = date.toISOString();
        }
      }
      updates[field] = newDate;
    } else if (field === 'node_name') {
      updates.node_name = value;
    } else if (field === 'responsible_person') {
      updates.responsible_person = value || null;
    } else if (field === 'progress_percent') {
      updates.progress_percent = parseInt(value);
    }
    
    if (Object.keys(updates).length === 0) return;
    
    setPendingUpdates(prev => {
      const newMap = new Map(prev);
      const existing = newMap.get(nodeId) || {};
      newMap.set(nodeId, { ...existing, ...updates });
      return newMap;
    });
  };

  const moveNode = async (nodeId: number, direction: 'up' | 'down') => {
    try {
      await api.post(`/projects/nodes/${nodeId}/move`, null, { params: { direction } });
      triggerRefreshNodes();
      clearPending();
    } catch (err) {
      console.error('移动失败', err);
    }
  };

  const deleteNode = async (nodeId: number) => {
    try {
      await api.delete(`/projects/nodes/${nodeId}`);
      triggerRefreshNodes();
      clearPending();
    } catch (err: any) {
      console.error('删除失败', err.response?.data?.error || err.message);
    }
  };

  const addNode = async () => {
    const name = prompt('请输入节点名称');
    if (!name) return;
    const days = prompt('计划天数（整数）', '5');
    if (!days) return;
    const responsible = prompt('责任人（可选）');
    try {
      await api.post(`/projects/${currentProject!.id}/nodes`, {
        node_name: name,
        planned_days: parseInt(days),
        responsible: responsible || null,
        prev_node_id: null,
      });
      triggerRefreshNodes();
      clearPending();
    } catch (err: any) {
      console.error('添加失败', err.response?.data?.error || err.message);
    }
  };

  const initBlankNodes = async () => {
    try {
      await api.post(`/projects/${currentProject!.id}/init-blank`);
      triggerRefreshNodes();
      clearPending();
    } catch (err) {
      console.error('初始化失败', err);
    }
  };

  const resetPlanned = async () => {
    try {
      await api.post(`/projects/${currentProject!.id}/reset-planned`);
      triggerRefreshNodes();
      clearPending();
    } catch (err) {
      console.error('重置计划时间失败', err);
    }
  };

  const resetActual = async () => {
    try {
      await api.post(`/projects/${currentProject!.id}/reset-actual`);
      triggerRefreshNodes();
      clearPending();
    } catch (err) {
      console.error('重置实际时间失败', err);
    }
  };

  const completeOverdue = async () => {
    try {
      await api.post(`/projects/${currentProject!.id}/complete-overdue`);
      triggerRefreshNodes();
      clearPending();
    } catch (err) {
      console.error('批量完成逾期节点失败', err);
    }
  };

  if (!currentProject) return null;
  if (loading) return <div>加载节点...</div>;

  const currentDate = new Date().toISOString().split('T')[0];
  const hasPending = pendingUpdates.size > 0;

  return (
    <div>
      <div style={{ marginBottom: '1rem', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
        <button onClick={addNode}>➕ 添加自定义节点</button>
        <button onClick={initBlankNodes}>🚀 一键初始化（仅空白）</button>
        <button onClick={resetPlanned}>🧹 重置计划时间为空白</button>
        <button onClick={resetActual}>🧹 重置实际时间为空白</button>
        <button onClick={completeOverdue}>✅ 批量完成逾期节点</button>
        
        {hasPending && (
          <>
            <button onClick={saveAllChanges} style={{ backgroundColor: '#4caf50', color: 'white' }}>
              💾 保存所有更改 ({pendingUpdates.size})
            </button>
            <button onClick={discardAllChanges} style={{ backgroundColor: '#f44336', color: 'white' }}>
              🗑️ 放弃更改
            </button>
          </>
        )}
      </div>

      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th>移动</th>
            <th>节点名称</th>
            <th>计划开始</th>
            <th>计划结束</th>
            <th>实际开始</th>
            <th>实际结束</th>
            <th>当前日期</th>
            <th>进程时间(天)</th>
            <th>进度(%)</th>
            <th>状态</th>
            <th>责任人</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {nodes.map((node, idx) => {
            const hasNodePending = pendingUpdates.has(node.id);
            const rowStyle = hasNodePending ? { backgroundColor: '#fffbe6' } : {};
            
            return (
              <tr key={node.id} style={rowStyle}>
                <td>
                  <button onClick={() => moveNode(node.id, 'up')} disabled={idx === 0}>⬆️</button>
                  <button onClick={() => moveNode(node.id, 'down')} disabled={idx === nodes.length-1}>⬇️</button>
                </td>
                
                <td onClick={() => startEdit(node.id, 'node_name', getDisplayValue(node, 'node_name'))} style={{ cursor: 'pointer' }}>
                  {editingCell?.nodeId === node.id && editingCell.field === 'node_name' ? (
                    <input type="text" value={editValue} onChange={e => setEditValue(e.target.value)} onBlur={() => applyEdit(node.id, 'node_name')} autoFocus />
                  ) : getDisplayValue(node, 'node_name')}
                </td>
                
                <td onClick={() => startEdit(node.id, 'planned_start', getDisplayValue(node, 'planned_start'))} style={{ cursor: 'pointer' }}>
                  {editingCell?.nodeId === node.id && editingCell.field === 'planned_start' ? (
                    <input type="date" value={editValue} onChange={e => setEditValue(e.target.value)} onBlur={() => applyEdit(node.id, 'planned_start')} autoFocus />
                  ) : getDisplayValue(node, 'planned_start') || '-'}
                </td>
                
                <td onClick={() => startEdit(node.id, 'planned_end', getDisplayValue(node, 'planned_end'))} style={{ cursor: 'pointer' }}>
                  {editingCell?.nodeId === node.id && editingCell.field === 'planned_end' ? (
                    <input type="date" value={editValue} onChange={e => setEditValue(e.target.value)} onBlur={() => applyEdit(node.id, 'planned_end')} autoFocus />
                  ) : getDisplayValue(node, 'planned_end') || '-'}
                </td>
                
                <td onClick={() => startEdit(node.id, 'actual_start', getDisplayValue(node, 'actual_start'))} style={{ cursor: 'pointer' }}>
                  {editingCell?.nodeId === node.id && editingCell.field === 'actual_start' ? (
                    <input type="date" value={editValue} onChange={e => setEditValue(e.target.value)} onBlur={() => applyEdit(node.id, 'actual_start')} autoFocus />
                  ) : getDisplayValue(node, 'actual_start') || '-'}
                </td>
                
                <td onClick={() => startEdit(node.id, 'actual_end', getDisplayValue(node, 'actual_end'))} style={{ cursor: 'pointer' }}>
                  {editingCell?.nodeId === node.id && editingCell.field === 'actual_end' ? (
                    <input type="date" value={editValue} onChange={e => setEditValue(e.target.value)} onBlur={() => applyEdit(node.id, 'actual_end')} autoFocus />
                  ) : getDisplayValue(node, 'actual_end') || '-'}
                </td>
                
                <td>{currentDate}</td>
                <td>{calcProgressTime(node)}</td>
                
                <td onClick={() => startEdit(node.id, 'progress_percent', getDisplayValue(node, 'progress_percent'))} style={{ cursor: 'pointer' }}>
                  {editingCell?.nodeId === node.id && editingCell.field === 'progress_percent' ? (
                    <input type="number" value={editValue} onChange={e => setEditValue(e.target.value)} onBlur={() => applyEdit(node.id, 'progress_percent')} autoFocus />
                  ) : getDisplayValue(node, 'progress_percent')}
                </td>
                
                <td>{node.status}</td>
                
                <td onClick={() => startEdit(node.id, 'responsible_person', getDisplayValue(node, 'responsible_person'))} style={{ cursor: 'pointer' }}>
                  {editingCell?.nodeId === node.id && editingCell.field === 'responsible_person' ? (
                    <input type="text" value={editValue} onChange={e => setEditValue(e.target.value)} onBlur={() => applyEdit(node.id, 'responsible_person')} autoFocus />
                  ) : getDisplayValue(node, 'responsible_person') || '-'}
                </td>
                
                <td>
                  <button onClick={() => deleteNode(node.id)}>🗑️</button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};