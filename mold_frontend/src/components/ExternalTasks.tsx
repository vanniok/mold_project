import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useProject } from '../contexts/ProjectContext';
import api from '../api';

interface ExternalTask {
  id?: number;
  task_name: string;
  responsible: string | null;
  progress_percent: number;
  proof_image_path?: string | null;
}

const fetchTasks = async (projectId: number) => {
  const res = await api.get(`/external-tasks/${projectId}`);
  return res.data;
};

const saveTasks = async ({ projectId, tasks }: { projectId: number; tasks: ExternalTask[] }) => {
  await api.post(`/external-tasks/${projectId}/save`, tasks);
};

const uploadImage = async ({ taskId, file }: { taskId: number; file: File }) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await api.post(`/external-tasks/${taskId}/upload-image`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data.image_path;
};

const deleteImage = async (taskId: number) => {
  await api.delete(`/external-tasks/${taskId}/image`);
};

export const ExternalTasks = () => {
  const { currentProject } = useProject();
  const queryClient = useQueryClient();
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editData, setEditData] = useState<Partial<ExternalTask>>({});
  const [uploadingId, setUploadingId] = useState<number | null>(null);

  const { data: tasks = [], isLoading } = useQuery({
    queryKey: ['externalTasks', currentProject?.id],
    queryFn: () => fetchTasks(currentProject!.id),
    enabled: !!currentProject,
    refetchInterval: 10000,
  });

  const saveMutation = useMutation({
    mutationFn: saveTasks,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['externalTasks', currentProject?.id] });
    },
    onError: (err) => console.error('保存失败', err),
  });

  const uploadMutation = useMutation({
    mutationFn: uploadImage,
    onSuccess: (imagePath, { taskId }) => {
      queryClient.setQueryData(['externalTasks', currentProject?.id], (old: ExternalTask[] | undefined) => {
        if (!old) return old;
        return old.map(t => t.id === taskId ? { ...t, proof_image_path: imagePath } : t);
      });
    },
    onError: (err) => console.error('上传失败', err),
    onSettled: () => setUploadingId(null),
  });

  const deleteImageMutation = useMutation({
    mutationFn: deleteImage,
    onSuccess: (_, taskId) => {
      queryClient.setQueryData(['externalTasks', currentProject?.id], (old: ExternalTask[] | undefined) => {
        if (!old) return old;
        return old.map(t => t.id === taskId ? { ...t, proof_image_path: null } : t);
      });
    },
    onError: (err) => console.error('删除图片失败', err),
  });

  const addTask = () => {
    const newTask: ExternalTask = {
      task_name: '新任务',
      responsible: '',
      progress_percent: 0,
    };
    queryClient.setQueryData(['externalTasks', currentProject?.id], (old: ExternalTask[] | undefined) => [
      ...(old || []),
      newTask,
    ]);
  };

  const deleteTask = (index: number) => {
    const newTasks = [...tasks];
    newTasks.splice(index, 1);
    queryClient.setQueryData(['externalTasks', currentProject?.id], newTasks);
  };

  const startEdit = (index: number) => {
    setEditingId(index);
    setEditData({ ...tasks[index] });
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditData({});
  };

  const saveEdit = (index: number) => {
    const newTasks = [...tasks];
    newTasks[index] = { ...newTasks[index], ...editData };
    queryClient.setQueryData(['externalTasks', currentProject?.id], newTasks);
    setEditingId(null);
    setEditData({});
  };

  const handleUpload = async (taskId: number | undefined, file: File) => {
    if (!taskId) return;
    setUploadingId(taskId);
    uploadMutation.mutate({ taskId, file });
  };

  const handleDeleteImage = async (taskId: number | undefined) => {
    if (!taskId) return;
    deleteImageMutation.mutate(taskId);
  };

  const handleSaveAll = () => {
    saveMutation.mutate({ projectId: currentProject!.id, tasks });
  };

  if (!currentProject) return null;

  return (
    <div style={{ marginTop: '2rem' }}>
      <h3>📱 外部进度跟踪（外协厂任务）</h3>
      <div style={{ marginBottom: '1rem' }}>
        <button onClick={addTask}>➕ 添加外协任务</button>
        <button onClick={handleSaveAll} style={{ marginLeft: '8px' }}>💾 保存所有更改</button>
      </div>
      {isLoading && <div>加载中...</div>}
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th>任务名称</th>
            <th>责任人</th>
            <th>进度(%)</th>
            <th>凭证图片</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {tasks.map((task: any, idx: number) => (
            <tr key={task.id || idx}>
              <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                {editingId === idx ? (
                  <input
                    type="text"
                    value={editData.task_name || ''}
                    onChange={e => setEditData({ ...editData, task_name: e.target.value })}
                  />
                ) : task.task_name}
               </td>
              <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                {editingId === idx ? (
                  <input
                    type="text"
                    value={editData.responsible || ''}
                    onChange={e => setEditData({ ...editData, responsible: e.target.value })}
                  />
                ) : task.responsible || '-'}
               </td>
              <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                {editingId === idx ? (
                  <input
                    type="number"
                    value={editData.progress_percent || 0}
                    onChange={e => setEditData({ ...editData, progress_percent: parseInt(e.target.value) })}
                    min="0" max="100"
                  />
                ) : `${task.progress_percent}%`}
               </td>
              <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                {task.proof_image_path && (
                  <div>
                    <img src={`/${task.proof_image_path}`} alt="凭证" style={{ width: '50px', cursor: 'pointer' }} onClick={() => window.open(`/${task.proof_image_path}`)} />
                    <button onClick={() => handleDeleteImage(task.id)}>❌</button>
                  </div>
                )}
                <input
                  type="file"
                  accept="image/*"
                  onChange={e => {
                    if (e.target.files && e.target.files[0]) handleUpload(task.id, e.target.files[0]);
                  }}
                  disabled={uploadingId === task.id}
                />
                {uploadingId === task.id && <span>上传中...</span>}
               </td>
              <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                {editingId === idx ? (
                  <>
                    <button onClick={() => saveEdit(idx)}>✅</button>
                    <button onClick={cancelEdit}>❌</button>
                  </>
                ) : (
                  <>
                    <button onClick={() => startEdit(idx)}>✏️</button>
                    <button onClick={() => deleteTask(idx)}>🗑️</button>
                  </>
                )}
               </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};