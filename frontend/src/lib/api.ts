import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

// Books
export const getBooks = (params?: Record<string, any>) => api.get('/books', { params });
export const getBook = (id: number) => api.get(`/books/${id}`);
export const getRecentBooks = (limit?: number) => api.get('/books/recent', { params: { limit } });
export const getContinueReading = (limit?: number) => api.get('/books/continue-reading', { params: { limit } });
export const updateBook = (id: number, data: any) => api.patch(`/books/${id}`, data);
export const deleteBook = (id: number) => api.delete(`/books/${id}`);
export const getBookFileUrl = (id: number) => `/api/v1/books/${id}/file`;
export const getBookCoverUrl = (id: number) => `/api/v1/books/${id}/cover`;

// Library
export const scanLibrary = (directory: string) => api.post('/library/scan', { directory });
export const getScanStatus = (taskId: string) => api.get(`/library/scan/${taskId}`);
export const importBooks = (directory?: string) => api.post('/library/import', null, { params: { directory } });
export const getLibraryStats = () => api.get('/library/stats');
export const getProcessingStatus = () => api.get('/library/processing');

// Search
export const search = (q: string, params?: Record<string, any>) => api.get('/search', { params: { q, ...params } });
export const searchSuggest = (q: string) => api.get('/search/suggest', { params: { q } });

// Insights
export const getBookInsights = (bookId: number) => api.get(`/insights/book/${bookId}`);
export const getInsightConnections = (insightId: number) => api.get(`/insights/${insightId}/connections`);
export const regenerateInsights = (bookId: number) => api.post(`/insights/book/${bookId}/regenerate`);

// Chat
export const createChatSession = (data: { title?: string; book_ids?: number[] }) => api.post('/chat/sessions', data);
export const getChatSessions = () => api.get('/chat/sessions');
export const getChatMessages = (sessionId: number) => api.get(`/chat/sessions/${sessionId}/messages`);
export const sendChatMessage = (sessionId: number, content: string) => api.post(`/chat/sessions/${sessionId}/messages`, { content });

// Feed
export const getFeed = (params?: Record<string, any>) => api.get('/feed', { params });
export const generateFeed = () => api.post('/feed/generate');
export const updateFeedItem = (id: number, data: any) => api.patch(`/feed/${id}`, data);

// Topics
export const getTopics = () => api.get('/topics');
export const getTopic = (id: number) => api.get(`/topics/${id}`);
export const getTopicGraph = () => api.get('/topics/graph');

// Recommendations
export const getRecommendations = (limit?: number) => api.get('/recommendations', { params: { limit } });
export const getSimilarBooks = (bookId: number) => api.get(`/recommendations/similar/${bookId}`);

// Reading
export const getReadingProgress = (bookId: number) => api.get(`/reading/progress/${bookId}`);
export const updateReadingProgress = (bookId: number, data: any) => api.put(`/reading/progress/${bookId}`, data);
export const getReadingStats = () => api.get('/reading/stats');

// Knowledge
export const getKnowledgeConnections = () => api.get('/knowledge/connections');
export const getLearningPaths = () => api.get('/knowledge/learning-paths');
export const getKnowledgeMap = () => api.get('/knowledge/map');

// Config
export const getConfig = () => api.get('/config');
export const updateConfig = (data: any) => api.patch('/config', data);
export const getModels = () => api.get('/config/models');
export const setModel = (taskType: string, modelId: string) => api.put('/config/models', { task_type: taskType, model_id: modelId });

export default api;
