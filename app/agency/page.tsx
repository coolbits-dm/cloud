'use client';

import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

interface AgencyData {
  user: {
    id: string;
    email: string;
    name: string;
    phone: string;
    industry: string;
    role: string;
    accountType: string;
  };
  business: {
    id: string;
    name: string;
    description: string;
    website: string;
    industry: string;
  };
  aiAgents: Array<{
    id: string;
    name: string;
    role: string;
    provider: string;
    systemPrompt: string;
  }>;
}

export default function AgencyPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [agencyData, setAgencyData] = useState<AgencyData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/auth/signin');
    } else if (status === 'authenticated') {
      // Fetch agency data
      fetchAgencyData();
    }
  }, [status, router]);

  const fetchAgencyData = async () => {
    try {
      const response = await fetch('/api/business/profile');
      if (response.ok) {
        const data = await response.json();
        setAgencyData(data);
      }
    } catch (error) {
      console.error('Error fetching agency data:', error);
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

  if (!agencyData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">No agency data found</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                Welcome to {agencyData.business.name}
              </h1>
              <p className="text-gray-300">
                Agency Management Dashboard
              </p>
            </div>
            <div className="text-right">
              <p className="text-white font-medium">{agencyData.user.name}</p>
              <p className="text-gray-300 text-sm">{agencyData.user.email}</p>
            </div>
          </div>
        </div>

        {/* Agency Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
            <h3 className="text-white font-semibold mb-2">AI Council</h3>
            <p className="text-3xl font-bold text-blue-400">{agencyData.aiAgents.length}</p>
            <p className="text-gray-300 text-sm">Active AI Agents</p>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
            <h3 className="text-white font-semibold mb-2">Industry</h3>
            <p className="text-xl font-bold text-green-400">{agencyData.business.industry}</p>
            <p className="text-gray-300 text-sm">Specialization</p>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
            <h3 className="text-white font-semibold mb-2">Account Type</h3>
            <p className="text-xl font-bold text-purple-400">{agencyData.user.accountType}</p>
            <p className="text-gray-300 text-sm">Management Level</p>
          </div>
        </div>

        {/* AI Council */}
        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 mb-8">
          <h2 className="text-2xl font-bold text-white mb-6">Your AI Council</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {agencyData.aiAgents.map((agent) => (
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
                <p className="text-gray-300 text-sm mb-3">{agent.systemPrompt}</p>
                <button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg text-sm transition-colors">
                  Chat with {agent.role}
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Agency Tools */}
        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
          <h2 className="text-2xl font-bold text-white mb-6">Agency Management Tools</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
              <h3 className="text-white font-semibold mb-2">Client Management</h3>
              <p className="text-gray-300 text-sm mb-3">Manage multiple clients and their campaigns</p>
              <button className="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-lg text-sm transition-colors">
                Manage Clients
              </button>
            </div>
            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
              <h3 className="text-white font-semibold mb-2">Campaign Analytics</h3>
              <p className="text-gray-300 text-sm mb-3">Track performance across all campaigns</p>
              <button className="w-full bg-purple-600 hover:bg-purple-700 text-white py-2 px-4 rounded-lg text-sm transition-colors">
                View Analytics
              </button>
            </div>
            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
              <h3 className="text-white font-semibold mb-2">Team Management</h3>
              <p className="text-gray-300 text-sm mb-3">Manage your agency team and roles</p>
              <button className="w-full bg-orange-600 hover:bg-orange-700 text-white py-2 px-4 rounded-lg text-sm transition-colors">
                Manage Team
              </button>
            </div>
            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
              <h3 className="text-white font-semibold mb-2">AI Strategy</h3>
              <p className="text-gray-300 text-sm mb-3">Plan and execute AI-powered strategies</p>
              <button className="w-full bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-lg text-sm transition-colors">
                AI Strategy
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
