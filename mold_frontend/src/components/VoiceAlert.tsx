import { useState } from 'react';
import { useProject } from '../contexts/ProjectContext';
import api from '../api';

export const VoiceAlert = () => {
  const { currentProject } = useProject();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSpeak = async () => {
    if (!currentProject) return;
    setLoading(true);
    setMessage('');
    try {
      const res = await api.post('/tts/speak', { project_id: currentProject.id });
      if (res.data.error) {
        setMessage(res.data.error);
      } else if (res.data.audio_base64) {
        // 播放音频
        const audio = new Audio(`data:audio/mp3;base64,${res.data.audio_base64}`);
        audio.play().catch(e => console.error('播放失败', e));
        setMessage('语音播报中...');
        setTimeout(() => setMessage(''), 3000);
      } else {
        setMessage(res.data.message || '无预警节点');
      }
    } catch (err) {
      setMessage('请求失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ margin: '1rem 0' }}>
      <button onClick={handleSpeak} disabled={loading || !currentProject}>
        🔊 播报当前预警
      </button>
      {loading && <span> 生成中...</span>}
      {message && <div style={{ marginTop: '8px', color: 'blue' }}>{message}</div>}
    </div>
  );
};