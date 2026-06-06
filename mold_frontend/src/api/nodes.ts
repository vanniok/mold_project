import api from './index';

export const getNodes = (projectId: number) => {
  return api.get(`/projects/${projectId}/nodes`);
};