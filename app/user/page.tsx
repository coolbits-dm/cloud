'use client';

import { useSession } from 'next-auth/react';
import { useState, useEffect } from 'react';

interface UserData {
  id: string;
  name: string;
  email: string;
  phone: string;
  industry: string;
  role: string;
  accountType: string;
}

export default function UserDashboard() {
  const { data: session, status } = useSession();
  const [userData, setUserData] = useState<UserData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (session?.user?.email) {
      fetchUserData();
    }
  }, [session]);

  const fetchUserData = async () => {
    try {
      const response = await fetch('/api/user/profile');
      if (response.ok) {
        const data = await response.json();
        setUserData(data.user);
      }
    } catch (error) {
      console.error('Error fetching user data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (status === 'loading' || isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  if (status === 'unauthenticated') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Please sign in to access your dashboard</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">U</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Personal Dashboard</h1>
                <p className="text-gray-300 text-sm">user.coolbits.ai</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <img 
                src={session?.user?.image || '/default-avatar.png'} 
                alt="Profile" 
                className="w-8 h-8 rounded-full"
              />
              <span className="text-white">{session?.user?.name}</span>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Profile Card */}
          <div className="lg:col-span-1">
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
              <h2 className="text-xl font-bold text-white mb-4">Profile</h2>
              {userData && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-gray-300 text-sm mb-1">Name</label>
                    <p className="text-white">{userData.name}</p>
                  </div>
                  <div>
                    <label className="block text-gray-300 text-sm mb-1">Email</label>
                    <p className="text-white">{userData.email}</p>
                  </div>
                  <div>
                    <label className="block text-gray-300 text-sm mb-1">Phone</label>
                    <p className="text-white">{userData.phone || 'Not provided'}</p>
                  </div>
                  <div>
                    <label className="block text-gray-300 text-sm mb-1">Industry</label>
                    <p className="text-white">{userData.industry || 'Not specified'}</p>
                  </div>
                  <div>
                    <label className="block text-gray-300 text-sm mb-1">Role</label>
                    <p className="text-white">{userData.role || 'Not specified'}</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Personal AI Assistant */}
          <div className="lg:col-span-2">
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
              <h2 className="text-xl font-bold text-white mb-4">Personal AI Assistant</h2>
              <p className="text-gray-300 mb-6">
                Your personal AI assistant is ready to help you with any task.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-blue-600/20 rounded-lg p-4 border border-blue-400/30">
                  <h3 className="text-white font-semibold mb-2">ChatGPT (Primary)</h3>
                  <p className="text-gray-300 text-sm">GPT-4 powered assistant for complex tasks</p>
                </div>
                <div className="bg-purple-600/20 rounded-lg p-4 border border-purple-400/30">
                  <h3 className="text-white font-semibold mb-2">Grok (Fallback)</h3>
                  <p className="text-gray-300 text-sm">xAI powered assistant for creative tasks</p>
                </div>
              </div>
              <button className="mt-6 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
                Start Chat
              </button>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="lg:col-span-3">
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
              <h2 className="text-xl font-bold text-white mb-4">Quick Actions</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button className="bg-green-600/20 rounded-lg p-4 border border-green-400/30 hover:bg-green-600/30 transition-colors">
                  <h3 className="text-white font-semibold mb-2">Connect Social Media</h3>
                  <p className="text-gray-300 text-sm">Link your social accounts</p>
                </button>
                <button className="bg-orange-600/20 rounded-lg p-4 border border-orange-400/30 hover:bg-orange-600/30 transition-colors">
                  <h3 className="text-white font-semibold mb-2">Personal Tools</h3>
                  <p className="text-gray-300 text-sm">Connect your favorite apps</p>
                </button>
                <button className="bg-pink-600/20 rounded-lg p-4 border border-pink-400/30 hover:bg-pink-600/30 transition-colors">
                  <h3 className="text-white font-semibold mb-2">API Keys</h3>
                  <p className="text-gray-300 text-sm">Manage your API connections</p>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
