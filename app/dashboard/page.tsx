'use client';

import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

interface DashboardData {
  user: {
    id: string;
    email: string;
    name: string;
    phone: string;
    industry: string;
    role: string;
    selectedUsageTypes: string[];
  };
  business?: {
    id: string;
    name: string;
    description: string;
    website: string;
    industry: string;
  };
  aiAgents?: Array<{
    id: string;
    name: string;
    role: string;
    provider: string;
    systemPrompt: string;
  }>;
}

const FEATURE_CARDS = [
         {
         id: 'personal',
         title: 'Personal AI Assistant',
         description: 'Chat with Andrei\'s AI - Your personal strategic advisor',
         icon: '🧠',
         color: 'from-blue-500 to-blue-600',
         route: '/personal',
         features: ['Business Strategy', 'Technology Insights', 'Marketing Optimization']
       },
  {
    id: 'business',
    title: 'Business Management',
    description: 'AI-powered business tools and insights',
    icon: '🏢',
    color: 'from-green-500 to-green-600',
    route: '/business',
    features: ['AI Business Council', 'Marketing Tools', 'Business Analytics']
  },
  {
    id: 'agency',
    title: 'Marketing Agency',
    description: 'Manage clients and campaigns at MCC level',
    icon: '🎯',
    color: 'from-purple-500 to-purple-600',
    route: '/agency',
    features: ['Client Management', 'MCC Tools', 'Campaign Analytics']
  },
  {
    id: 'developer',
    title: 'Developer Tools',
    description: 'AI coding assistants and development tools',
    icon: '💻',
    color: 'from-orange-500 to-orange-600',
    route: '/dev',
    features: ['Cursor Integration', 'Code AI', 'Development Tools']
  }
];

export default function DashboardPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/auth/signin');
    } else if (status === 'authenticated') {
      fetchDashboardData();
    }
  }, [status, router]);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/user/profile');
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (status === 'loading' || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">No dashboard data found</div>
      </div>
    );
  }

  const selectedFeatures = FEATURE_CARDS.filter(card => 
    dashboardData.user.selectedUsageTypes?.includes(card.id)
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                Welcome back, {dashboardData.user.name}!
              </h1>
              <p className="text-gray-300">
                Your CoolBits.ai Dashboard
              </p>
            </div>
            <div className="text-right">
              <p className="text-white font-medium">{dashboardData.user.name}</p>
              <p className="text-gray-300 text-sm">{dashboardData.user.email}</p>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
            <h3 className="text-white font-semibold mb-2">Active Features</h3>
            <p className="text-3xl font-bold text-blue-400">{selectedFeatures.length}</p>
            <p className="text-gray-300 text-sm">Selected Tools</p>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
            <h3 className="text-white font-semibold mb-2">Industry</h3>
            <p className="text-xl font-bold text-green-400">{dashboardData.user.industry}</p>
            <p className="text-gray-300 text-sm">Specialization</p>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
            <h3 className="text-white font-semibold mb-2">Role</h3>
            <p className="text-xl font-bold text-purple-400">{dashboardData.user.role}</p>
            <p className="text-gray-300 text-sm">Position</p>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
            <h3 className="text-white font-semibold mb-2">AI Council</h3>
            <p className="text-3xl font-bold text-orange-400">{dashboardData.aiAgents?.length || 0}</p>
            <p className="text-gray-300 text-sm">AI Agents</p>
          </div>
        </div>

        {/* Feature Cards */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-6">Your CoolBits.ai Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {selectedFeatures.map((feature) => (
              <div key={feature.id} className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/10 hover:border-white/20 transition-all">
                <div className="flex items-center mb-4">
                  <div className={`w-12 h-12 bg-gradient-to-r ${feature.color} rounded-lg flex items-center justify-center mr-4`}>
                    <span className="text-white text-xl">{feature.icon}</span>
                  </div>
                  <div>
                    <h3 className="text-white font-semibold">{feature.title}</h3>
                    <p className="text-gray-300 text-sm">{feature.description}</p>
                  </div>
                </div>
                <div className="space-y-2 mb-4">
                  {feature.features.map((feat, index) => (
                    <div key={index} className="flex items-center text-sm">
                      <span className="text-green-400 mr-2">✓</span>
                      <span className="text-gray-300">{feat}</span>
                    </div>
                  ))}
                </div>
                <button
                  onClick={() => router.push(feature.route)}
                  className={`w-full bg-gradient-to-r ${feature.color} text-white py-2 px-4 rounded-lg font-medium hover:opacity-90 transition-opacity`}
                >
                  Access {feature.title}
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* AI Council Preview */}
        {dashboardData.aiAgents && dashboardData.aiAgents.length > 0 && (
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 mb-8">
            <h2 className="text-2xl font-bold text-white mb-6">Your AI Council</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {dashboardData.aiAgents.slice(0, 3).map((agent) => (
                <div key={agent.id} className="bg-white/5 rounded-lg p-4 border border-white/10">
                  <div className="flex items-center mb-3">
                    <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mr-3">
                      <span className="text-white font-bold">{agent.role.charAt(0)}</span>
                    </div>
                    <div>
                      <h3 className="text-white font-semibold">{agent.name}</h3>
                      <p className="text-gray-300 text-sm">{agent.role}</p>
                    </div>
                  </div>
                  <button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg text-sm transition-colors">
                    Chat with {agent.role}
                  </button>
                </div>
              ))}
            </div>
            {dashboardData.aiAgents.length > 3 && (
              <div className="text-center mt-4">
                <button
                  onClick={() => router.push('/business')}
                  className="text-blue-400 hover:text-blue-300 text-sm"
                >
                  View all {dashboardData.aiAgents.length} AI agents →
                </button>
              </div>
            )}
          </div>
        )}

        {/* Quick Actions */}
        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
          <h2 className="text-2xl font-bold text-white mb-6">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => router.push('/andrei')}
              className="bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 px-4 rounded-lg font-medium hover:opacity-90 transition-opacity"
            >
              🧠 Chat with Andrei's AI Council
            </button>
            <button
              onClick={() => router.push('/onboarding')}
              className="bg-gradient-to-r from-green-500 to-green-600 text-white py-3 px-4 rounded-lg font-medium hover:opacity-90 transition-opacity"
            >
              ⚙️ Update Profile Settings
            </button>
            <button
              onClick={() => router.push('/auth/signin')}
              className="bg-gradient-to-r from-red-500 to-red-600 text-white py-3 px-4 rounded-lg font-medium hover:opacity-90 transition-opacity"
            >
              🔐 Account Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
