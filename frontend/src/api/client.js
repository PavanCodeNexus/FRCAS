import axios from 'axios';

const api = axios.create({
  baseURL: '',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('frcas_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const login = async (email, password) => {
  const response = await api.post('/auth/login', { email, password });
  return response.data;
};

export const getClasses = async () => {
  const response = await api.get('/classes');
  return response.data;
};

export const createClass = async (subject, section) => {
  const response = await api.post('/classes', { subject, section });
  return response.data;
};

export const getStudents = async (section = '') => {
  const url = section ? `/students?section=${encodeURIComponent(section)}` : '/students';
  const response = await api.get(url);
  return response.data;
};

export const registerStudent = async (formData) => {
  const response = await api.post('/students/register', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const deleteStudent = async (usn) => {
  const response = await api.delete(`/students/${usn}`);
  return response.data;
};

export const processAttendance = async (formData) => {
  const response = await api.post('/attendance/process', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const confirmAttendance = async (payload) => {
  const response = await api.post('/attendance/confirm', payload);
  return response.data;
};

export const getAttendanceHistory = async (classId) => {
  const response = await api.get(`/attendance/history/${classId}`);
  return response.data;
};

export default api;
