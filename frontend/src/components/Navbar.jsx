import React from 'react';
import { ScanFace, LogOut } from 'lucide-react';

export default function Navbar({ teacherName, teacherEmail, onLogout, activeTab, setActiveTab }) {
  return (
    <header class="bg-indigo-900 text-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-xl shadow">
            <ScanFace className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg leading-tight tracking-wide">FRCAS</h1>
            <p className="text-xs text-indigo-200">Face Recognition Attendance</p>
          </div>
        </div>

        {teacherName && (
          <div className="flex items-center space-x-4">
            <div className="text-right hidden sm:block">
              <p className="text-sm font-semibold text-white">{teacherName}</p>
              <p className="text-xs text-indigo-300">{teacherEmail}</p>
            </div>
            <button
              onClick={onLogout}
              className="px-3 py-1.5 rounded-md bg-indigo-800 hover:bg-indigo-700 text-xs font-medium text-indigo-100 flex items-center space-x-1.5 transition"
            >
              <LogOut className="w-4 h-4" />
              <span>Logout</span>
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
