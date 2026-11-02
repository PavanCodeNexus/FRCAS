import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import { Camera, Users, BookOpen, FileSpreadsheet, Lock, CheckCircle, HelpCircle, UserMinus, Plus } from 'lucide-react';
import { login, getClasses, createClass, getStudents, registerStudent, deleteStudent, processAttendance, confirmAttendance, getAttendanceHistory } from './api/client';

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('frcas_token') || '');
  const [teacherName, setTeacherName] = useState(localStorage.getItem('frcas_teacher_name') || '');
  const [teacherEmail, setTeacherEmail] = useState(localStorage.getItem('frcas_teacher_email') || '');
  const [tab, setTab] = useState('capture');

  // Auth form
  const [email, setEmail] = useState('teacher@college.edu');
  const [password, setPassword] = useState('admin123');
  const [authError, setAuthError] = useState('');
  const [loading, setLoading] = useState(false);

  // Classes & Students
  const [classes, setClasses] = useState([]);
  const [selectedClassId, setSelectedClassId] = useState('');
  const [students, setStudents] = useState([]);
  const [searchSection, setSearchSection] = useState('');

  // Class creation
  const [newSubject, setNewSubject] = useState('');
  const [newSection, setNewSection] = useState('');

  // Student registration
  const [regUsn, setRegUsn] = useState('');
  const [regName, setRegName] = useState('');
  const [regSection, setRegSection] = useState('');
  const [regPhotos, setRegPhotos] = useState([]);
  const [consent, setConsent] = useState(true);
  const [regLoading, setRegLoading] = useState(false);

  // Capture & Review
  const [classPhotos, setClassPhotos] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [reviewData, setReviewData] = useState(null);
  const [autoPresent, setAutoPresent] = useState([]);
  const [needsReview, setNeedsReview] = useState([]);
  const [unmatched, setUnmatched] = useState([]);
  const [savingAttendance, setSavingAttendance] = useState(false);

  // History
  const [history, setHistory] = useState([]);
  const [historyClassId, setHistoryClassId] = useState('');

  // Toast
  const [toast, setToast] = useState('');

  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(''), 4000);
  };

  useEffect(() => {
    if (token) {
      loadInitialData();
    }
  }, [token]);

  const loadInitialData = async () => {
    try {
      const cls = await getClasses();
      setClasses(cls);
      if (cls.length > 0) {
        setSelectedClassId(cls[0].id);
        setHistoryClassId(cls[0].id);
        loadHistoryData(cls[0].id);
      }
      const st = await getStudents();
      setStudents(st);
    } catch (e) {
      console.error(e);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setAuthError('');
    try {
      const data = await login(email, password);
      localStorage.setItem('frcas_token', data.access_token);
      localStorage.setItem('frcas_teacher_name', data.teacher_name);
      localStorage.setItem('frcas_teacher_email', data.teacher_email);
      setToken(data.access_token);
      setTeacherName(data.teacher_name);
      setTeacherEmail(data.teacher_email);
      showToast(`Welcome back, ${data.teacher_name}!`);
    } catch (err) {
      setAuthError(err.response?.data?.detail || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    setToken('');
    setTeacherName('');
    setTeacherEmail('');
    setReviewData(null);
  };

  const handleCreateClass = async (e) => {
    e.preventDefault();
    try {
      await createClass(newSubject, newSection);
      showToast('Class created successfully');
      setNewSubject('');
      setNewSection('');
      const cls = await getClasses();
      setClasses(cls);
    } catch (e) {
      showToast('Failed to create class');
    }
  };

  const handleRegisterStudent = async (e) => {
    e.preventDefault();
    if (regPhotos.length === 0) return alert('Select 1-3 photos');
    setRegLoading(true);
    try {
      const fd = new FormData();
      fd.append('usn', regUsn);
      fd.append('name', regName);
      fd.append('section', regSection);
      fd.append('consent_given', consent);
      for (let p of regPhotos) fd.append('photos', p);

      const res = await registerStudent(fd);
      showToast(`Enrolled ${res.name} with ${res.valid_photos_saved} face embeddings!`);
      setRegUsn('');
      setRegName('');
      setRegSection('');
      setRegPhotos([]);
      const st = await getStudents();
      setStudents(st);
    } catch (err) {
      alert(err.response?.data?.detail || 'Registration failed');
    } finally {
      setRegLoading(false);
    }
  };

  const handleDeleteStudent = async (usn) => {
    if (!confirm(`Delete student ${usn}?`)) return;
    try {
      await deleteStudent(usn);
      showToast(`Student ${usn} deleted`);
      const st = await getStudents();
      setStudents(st);
    } catch (e) {
      showToast('Failed to delete student');
    }
  };

  const handleProcessAttendance = async () => {
    if (!selectedClassId || classPhotos.length === 0) return;
    setProcessing(true);
    try {
      const fd = new FormData();
      fd.append('class_id', selectedClassId);
      for (let p of classPhotos) fd.append('photos', p);

      const res = await processAttendance(fd);
      setReviewData(res);
      setAutoPresent(res.auto_present);
      setNeedsReview(res.needs_review);
      setUnmatched(res.unmatched_students);
      showToast(`Detected ${res.total_faces_detected} faces across photos!`);
    } catch (err) {
      alert(err.response?.data?.detail || 'Attendance processing failed');
    } finally {
      setProcessing(false);
    }
  };

  const handleConfirmAttendance = async () => {
    setSavingAttendance(true);
    try {
      const records = [
        ...autoPresent.map(p => ({ usn: p.usn, status: 'PRESENT', confidence: p.confidence || 1.0, method: p.method || 'AUTO' })),
        ...unmatched.map(u => ({ usn: u.usn, status: 'ABSENT', confidence: 1.0, method: 'AUTO' }))
      ];
      const res = await confirmAttendance({ class_id: parseInt(selectedClassId), records });
      showToast(res.message);
      setReviewData(null);
      setClassPhotos([]);
      setTab('reports');
      loadHistoryData(selectedClassId);
    } catch (e) {
      showToast('Failed to save attendance');
    } finally {
      setSavingAttendance(false);
    }
  };

  const loadHistoryData = async (classId) => {
    if (!classId) return;
    try {
      const data = await getAttendanceHistory(classId);
      setHistory(data);
    } catch (e) {
      console.error(e);
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl border border-slate-200 p-8 max-w-md w-full">
          <div className="text-center mb-6">
            <div className="inline-flex p-3 rounded-2xl bg-indigo-50 text-indigo-700 mb-3">
              <Lock className="w-8 h-8" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900">Teacher Login</h2>
            <p className="text-sm text-slate-500 mt-1">Face Recognition Classroom Attendance</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Email</label>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} required className="w-full px-4 py-2.5 rounded-lg border border-slate-300 text-sm outline-none focus:ring-2 focus:ring-indigo-600" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Password</label>
              <input type="password" value={password} onChange={e => setPassword(e.target.value)} required className="w-full px-4 py-2.5 rounded-lg border border-slate-300 text-sm outline-none focus:ring-2 focus:ring-indigo-600" />
            </div>

            {authError && <div className="p-3 rounded-lg bg-red-50 text-red-700 text-xs">{authError}</div>}

            <button type="submit" disabled={loading} className="w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm shadow">
              {loading ? 'Authenticating...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 text-center text-xs text-slate-500">
            Demo Teacher: <span className="font-semibold">teacher@college.edu</span> / <span className="font-semibold">admin123</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
      <Navbar teacherName={teacherName} teacherEmail={teacherEmail} onLogout={handleLogout} />

      {toast && (
        <div className="fixed bottom-6 right-6 z-50 p-4 rounded-xl shadow-xl bg-emerald-600 text-white font-semibold text-xs">
          {toast}
        </div>
      )}

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <nav className="flex space-x-2 border-b border-slate-200 mb-8 overflow-x-auto pb-1">
          <button onClick={() => setTab('capture')} className={`px-4 py-2.5 font-semibold text-sm rounded-t-lg border-b-2 flex items-center space-x-2 whitespace-nowrap ${tab === 'capture' ? 'border-indigo-600 text-indigo-600 bg-indigo-50/50' : 'border-transparent text-slate-600'}`}>
            <Camera className="w-4 h-4" />
            <span>Take Attendance</span>
          </button>
          <button onClick={() => setTab('students')} className={`px-4 py-2.5 font-semibold text-sm rounded-t-lg border-b-2 flex items-center space-x-2 whitespace-nowrap ${tab === 'students' ? 'border-indigo-600 text-indigo-600 bg-indigo-50/50' : 'border-transparent text-slate-600'}`}>
            <Users className="w-4 h-4" />
            <span>Student Roster</span>
          </button>
          <button onClick={() => setTab('classes')} className={`px-4 py-2.5 font-semibold text-sm rounded-t-lg border-b-2 flex items-center space-x-2 whitespace-nowrap ${tab === 'classes' ? 'border-indigo-600 text-indigo-600 bg-indigo-50/50' : 'border-transparent text-slate-600'}`}>
            <BookOpen className="w-4 h-4" />
            <span>My Classes</span>
          </button>
          <button onClick={() => setTab('reports')} className={`px-4 py-2.5 font-semibold text-sm rounded-t-lg border-b-2 flex items-center space-x-2 whitespace-nowrap ${tab === 'reports' ? 'border-indigo-600 text-indigo-600 bg-indigo-50/50' : 'border-transparent text-slate-600'}`}>
            <FileSpreadsheet className="w-4 h-4" />
            <span>Reports & History</span>
          </button>
        </nav>

        {tab === 'capture' && !reviewData && (
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8 max-w-2xl">
            <h2 className="text-xl font-bold text-slate-900 mb-2">Take Classroom Attendance</h2>
            <p className="text-sm text-slate-500 mb-6">Select section and take/upload as many photos as needed to cover every corner of the classroom (Front, Back Benches, Corners).</p>

            <div className="space-y-6">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-2">Class</label>
                <select value={selectedClassId} onChange={e => setSelectedClassId(e.target.value)} className="w-full px-4 py-2.5 rounded-lg border border-slate-300 text-sm">
                  {classes.map(c => <option key={c.id} value={c.id}>{c.subject} - Section {c.section}</option>)}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-2">Classroom Photos (Unlimited - Cover all rows & backbenches)</label>
                <input type="file" multiple accept="image/*" onChange={e => setClassPhotos(Array.from(e.target.files))} className="w-full text-xs text-slate-500 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-indigo-50 file:text-indigo-700 font-semibold" />
                <p className="text-[11px] text-slate-400 mt-1.5">{classPhotos.length} photos selected. Tip: Take multiple overlapping angles so no student is missed.</p>
              </div>

              <button onClick={handleProcessAttendance} disabled={processing || classPhotos.length === 0} className="px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm shadow">
                {processing ? 'Processing AI Recognition...' : `Process Attendance with AI (${classPhotos.length} Photos)`}
              </button>
            </div>
          </div>
        )}

        {tab === 'capture' && reviewData && (
          <div className="space-y-6">
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-slate-900">Review & Confirm</h2>
                <p className="text-xs text-slate-500">Detected {reviewData.total_faces_detected} faces</p>
              </div>
              <div className="flex space-x-3">
                <button onClick={() => setReviewData(null)} className="px-4 py-2 border rounded-lg text-xs font-semibold">Cancel</button>
                <button onClick={handleConfirmAttendance} disabled={savingAttendance} className="px-5 py-2.5 bg-emerald-600 text-white font-bold text-xs rounded-lg shadow">
                  {savingAttendance ? 'Saving...' : 'Confirm & Save'}
                </button>
              </div>
            </div>

            {needsReview.length > 0 && (
              <div className="bg-amber-50 rounded-2xl border border-amber-200 p-6">
                <h3 className="font-bold text-amber-900 text-sm mb-4">Review Queue (40% - 60% similarity)</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                  {needsReview.map((item, idx) => (
                    <div key={idx} className="bg-white rounded-xl border p-4 shadow-sm flex items-center space-x-3">
                      <img src={item.face_crop_base64} className="w-14 h-14 rounded-lg object-cover" />
                      <div>
                        <p className="text-xs font-bold text-slate-900">{item.name}</p>
                        <p className="text-xs text-slate-500">{item.usn} ({Math.round(item.confidence * 100)}%)</p>
                        <div className="mt-2 flex space-x-2">
                          <button onClick={() => { setAutoPresent([...autoPresent, item]); setNeedsReview(needsReview.filter((_, i) => i !== idx)); }} className="px-2 py-1 bg-emerald-600 text-white rounded text-[10px] font-bold">Present</button>
                          <button onClick={() => { setUnmatched([...unmatched, item]); setNeedsReview(needsReview.filter((_, i) => i !== idx)); }} className="px-2 py-1 bg-slate-200 rounded text-[10px]">Absent</button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
              <h3 className="font-bold text-slate-900 text-sm uppercase mb-4">Present Students ({autoPresent.length})</h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-3">
                {autoPresent.map((st, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs">
                    <p className="font-bold text-slate-900 truncate">{st.name}</p>
                    <p className="text-emerald-800 font-mono text-[11px]">{st.usn}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {tab === 'students' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
              <h2 className="text-lg font-bold text-slate-900 mb-4">Enroll New Student</h2>
              <form onSubmit={handleRegisterStudent} className="space-y-4">
                <input type="text" placeholder="USN (e.g. 1MS21CS001)" value={regUsn} onChange={e => setRegUsn(e.target.value)} required className="w-full px-3 py-2 border rounded-lg text-sm uppercase" />
                <input type="text" placeholder="Full Name" value={regName} onChange={e => setRegName(e.target.value)} required className="w-full px-3 py-2 border rounded-lg text-sm" />
                <input type="text" placeholder="Section (e.g. 6A)" value={regSection} onChange={e => setRegSection(e.target.value)} required className="w-full px-3 py-2 border rounded-lg text-sm uppercase" />
                <input type="file" multiple accept="image/*" onChange={e => setRegPhotos(Array.from(e.target.files))} className="w-full text-xs" />
                <div className="flex items-center space-x-2">
                  <input type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)} id="c_box" />
                  <label htmlFor="c_box" className="text-xs text-slate-600">Student consent granted</label>
                </div>
                <button type="submit" disabled={regLoading} className="w-full py-2 bg-indigo-600 text-white rounded-lg font-semibold text-xs">
                  {regLoading ? 'Validating...' : 'Enroll Student'}
                </button>
              </form>
            </div>

            <div className="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
              <h2 className="text-lg font-bold text-slate-900 mb-4">Enrolled Students ({students.length})</h2>
              <div className="divide-y text-xs">
                {students.map(s => (
                  <div key={s.usn} className="py-2.5 flex items-center justify-between">
                    <div>
                      <span className="font-bold font-mono mr-3">{s.usn}</span>
                      <span className="font-medium mr-3">{s.name}</span>
                      <span className="text-indigo-600 font-semibold">{s.section}</span>
                    </div>
                    <button onClick={() => handleDeleteStudent(s.usn)} className="text-red-500 font-semibold">Delete</button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {tab === 'classes' && (
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 max-w-lg">
            <h2 className="text-lg font-bold text-slate-900 mb-4">Create New Class</h2>
            <form onSubmit={handleCreateClass} className="space-y-4">
              <input type="text" placeholder="Subject Name (e.g. Computer Networks)" value={newSubject} onChange={e => setNewSubject(e.target.value)} required className="w-full px-3 py-2 border rounded-lg text-sm" />
              <input type="text" placeholder="Section (e.g. 6B)" value={newSection} onChange={e => setNewSection(e.target.value)} required className="w-full px-3 py-2 border rounded-lg text-sm uppercase" />
              <button type="submit" className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-xs font-semibold">Create Class</button>
            </form>
          </div>
        )}

        {tab === 'reports' && (
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-bold text-slate-900">Attendance History & Reports</h2>
              <select value={historyClassId} onChange={e => { setHistoryClassId(e.target.value); loadHistoryData(e.target.value); }} className="px-3 py-1.5 border rounded-lg text-xs">
                {classes.map(c => <option key={c.id} value={c.id}>{c.subject} ({c.section})</option>)}
              </select>
            </div>
            <div className="overflow-x-auto text-xs">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b font-semibold text-slate-600 bg-slate-50">
                    <th className="p-2.5">Date</th>
                    <th className="p-2.5">Present</th>
                    <th className="p-2.5">Absent</th>
                    <th className="p-2.5">Rate</th>
                    <th className="p-2.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {history.map(h => (
                    <tr key={h.session_id}>
                      <td className="p-2.5 font-semibold">{new Date(h.date).toLocaleString()}</td>
                      <td className="p-2.5 text-emerald-700 font-bold">{h.present_count}</td>
                      <td className="p-2.5 text-rose-600 font-bold">{h.absent_count}</td>
                      <td className="p-2.5 font-bold">{h.attendance_rate}%</td>
                      <td className="p-2.5 text-right space-x-2">
                        <a href={`/reports/session/${h.session_id}/excel`} target="_blank" className="text-indigo-600 font-bold">Download Excel</a>
                        <a href={`/reports/session/${h.session_id}/csv`} target="_blank" className="text-slate-600 font-bold">CSV</a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
