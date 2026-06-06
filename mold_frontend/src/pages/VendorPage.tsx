import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../api';

export const VendorPage = () => {
  const [searchParams] = useSearchParams();
  const taskId = searchParams.get('task_id');
  const [task, setTask] = useState<any>(null);
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!taskId) {
      setError('缺少任务ID');
      setLoading(false);
      return;
    }
    fetchTask();
  }, [taskId]);

  const fetchTask = async () => {
    try {
      const res = await api.get(`/external-tasks/task/${taskId}`);
      setTask(res.data);
      setProgress(res.data.progress_percent);
    } catch (err) {
      setError('任务不存在或已删除');
    } finally {
      setLoading(false);
    }
  };

  const handleProgressChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setProgress(parseInt(e.target.value));
  };

  const handleSubmit = async () => {
    if (!task) return;
    try {
      await api.put(`/external-tasks/${task.id}/progress`, { progress_percent: progress });
      setMessage('进度已更新');
      setTimeout(() => setMessage(''), 3000);
    } catch (err) {
      setMessage('更新失败');
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || !task) return;
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('file', file);
    setUploading(true);
    try {
      const res = await api.post(`/external-tasks/${task.id}/upload-image`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setTask({ ...task, proof_image_path: res.data.image_path });
      setMessage('图片上传成功');
      setTimeout(() => setMessage(''), 3000);
    } catch (err) {
      setMessage('上传失败');
      setTimeout(() => setMessage(''), 3000);
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteImage = async () => {
  if (!task) return;
  try {
    await api.delete(`/external-tasks/${task.id}/image`);
    setTask({ ...task, proof_image_path: null });
    setMessage('图片已删除');
    setTimeout(() => setMessage(''), 3000);
  } catch (err) {
    setMessage('删除失败');
    setTimeout(() => setMessage(''), 3000);
  }
};

  if (loading) return <div>加载中...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;
  if (!task) return null;

  return (
    <div style={{ maxWidth: 600, margin: '2rem auto', padding: '1rem', border: '1px solid #ccc', borderRadius: 8 }}>
      <h2>外协任务进度更新</h2>
      {message && <div style={{ backgroundColor: '#d4edda', color: '#155724', padding: '8px', marginBottom: '12px', borderRadius: '4px' }}>{message}</div>}
      <p><strong>任务名称：</strong>{task.task_name}</p>
      <p><strong>责任人：</strong>{task.responsible || '未指定'}</p>
      <div>
        <label>当前进度 (%):</label>
        <input type="range" min="0" max="100" value={progress} onChange={handleProgressChange} />
        <span>{progress}%</span>
      </div>
      <button onClick={handleSubmit}>提交进度</button>
      <hr />
      <div>
        <label>上传凭证图片：</label>
        <input type="file" accept="image/*" onChange={handleImageUpload} disabled={uploading} />
        {uploading && <span>上传中...</span>}
        {task.proof_image_path && (
          <div>
            <img src={`http://localhost:8000/${task.proof_image_path}`} alt="凭证" style={{ width: '25%', maxWidth: '200px', marginTop: '8px' }} />
            <div><button onClick={handleDeleteImage}>删除图片</button></div>
          </div>
        )}
      </div>
    </div>
  );
};