import { Link, useLocation } from 'react-router-dom';
import { useState } from 'react';

export const Layout = ({ children }: { children: React.ReactNode }) => {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const isActive = (path: string) => location.pathname === path;

  const navLinks = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/participants', label: 'Participants', icon: '👥' },
    { path: '/recordings', label: 'Recordings', icon: '🎙️' },
    { path: '/sentences', label: 'Sentences', icon: '📝' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out md:relative md:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="p-6">
          <h1 className="text-2xl font-bold text-gray-900">Twi Admin</h1>
          <p className="text-sm text-gray-600">Speech Data Dashboard</p>
        </div>

        <nav className="mt-8">
          {navLinks.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              onClick={() => setSidebarOpen(false)}
              className={`block px-6 py-3 text-lg transition-colors ${
                isActive(link.path)
                  ? 'bg-blue-50 text-blue-600 border-r-4 border-blue-600'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <span className="mr-3">{link.icon}</span>
              {link.label}
            </Link>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Top Bar */}
        <div className="bg-white shadow md:hidden p-4 flex items-center">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded hover:bg-gray-100"
          >
            ☰
          </button>
          <h1 className="ml-4 text-xl font-semibold text-gray-900">Twi Admin</h1>
        </div>

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>

      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
};
