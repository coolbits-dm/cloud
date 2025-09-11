'use client';

import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

const INDUSTRIES = [
  { value: 'marketing_advertising', label: 'Marketing & Advertising' },
  { value: 'technology', label: 'Technology' },
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'finance', label: 'Finance' },
  { value: 'education', label: 'Education' },
  { value: 'retail', label: 'Retail' },
  { value: 'manufacturing', label: 'Manufacturing' },
  { value: 'consulting', label: 'Consulting' },
  { value: 'real_estate', label: 'Real Estate' },
  { value: 'other', label: 'Other' },
];

const ROLES = [
  { value: 'ceo_founder', label: 'CEO / Founder' },
  { value: 'cto', label: 'CTO' },
  { value: 'cmo', label: 'CMO' },
  { value: 'cfo', label: 'CFO' },
  { value: 'manager', label: 'Manager' },
  { value: 'director', label: 'Director' },
  { value: 'consultant', label: 'Consultant' },
  { value: 'freelancer', label: 'Freelancer' },
  { value: 'student', label: 'Student' },
  { value: 'other', label: 'Other' },
];

const USAGE_TYPES = [
  {
    id: 'personal',
    title: 'Personal User',
    description: 'Connect personal apps, social media, and personal tools',
    icon: '👤',
    features: ['Social Media Integration', 'Personal AI Assistant', 'Personal Tools']
  },
  {
    id: 'business',
    title: 'Business Management',
    description: 'Manage a business with AI-powered tools and insights',
    icon: '🏢',
    features: ['AI Business Council', 'Marketing Tools', 'Business Analytics']
  },
  {
    id: 'agency',
    title: 'Marketing Agency',
    description: 'Manage multiple clients and campaigns at MCC level',
    icon: '🎯',
    features: ['Client Management', 'MCC Tools', 'Campaign Analytics']
  },
  {
    id: 'developer',
    title: 'Developer Tools',
    description: 'Access development tools and AI coding assistants',
    icon: '💻',
    features: ['Cursor Integration', 'Code AI', 'Development Tools']
  }
];

interface OnboardingData {
  step: number;
  phone: string;
  industry: string;
  role: string;
  selectedUsageTypes: string[];
  businessName: string;
  businessDescription: string;
  businessWebsite: string;
}

export default function OnboardingPage() {
  const { data: session } = useSession();
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [data, setData] = useState<OnboardingData>({
    step: 1,
    phone: '',
    industry: '',
    role: '',
    selectedUsageTypes: [],
    businessName: '',
    businessDescription: '',
    businessWebsite: '',
  });

  const updateData = (key: keyof OnboardingData, value: any) => {
    setData(prev => ({ ...prev, [key]: value }));
  };

  const toggleUsageType = (usageTypeId: string) => {
    setData(prev => ({
      ...prev,
      selectedUsageTypes: prev.selectedUsageTypes.includes(usageTypeId)
        ? prev.selectedUsageTypes.filter(id => id !== usageTypeId)
        : [...prev.selectedUsageTypes, usageTypeId]
    }));
  };

  const nextStep = () => {
    if (data.step < 7) {
      updateData('step', data.step + 1);
    }
  };

  const prevStep = () => {
    if (data.step > 1) {
      updateData('step', data.step - 1);
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const response = await fetch('/api/onboarding', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        // Redirect to main dashboard - user can access all selected features
        router.push('/dashboard');
      } else {
        throw new Error('Failed to save onboarding data');
      }
    } catch (error) {
      console.error('Onboarding error:', error);
      alert('Failed to save your information. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStep = () => {
    switch (data.step) {
      case 1:
        return (
          <div className="text-center">
            <h2 className="text-2xl font-bold text-white mb-4">Welcome, {session?.user?.name}!</h2>
            <p className="text-gray-300 mb-8">Let's set up your CoolBits.ai experience</p>
            <div className="bg-white/10 rounded-lg p-6 mb-6">
              <div className="flex items-center space-x-4 mb-4">
                <img 
                  src={session?.user?.image || '/default-avatar.png'} 
                  alt="Profile" 
                  className="w-16 h-16 rounded-full"
                />
                <div className="text-left">
                  <p className="text-white font-medium">{session?.user?.name}</p>
                  <p className="text-gray-400">{session?.user?.email}</p>
                </div>
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div>
            <h2 className="text-2xl font-bold text-white mb-4">Contact Information</h2>
            <p className="text-gray-300 mb-6">Help us stay in touch</p>
            <div className="space-y-4">
              <div>
                <label className="block text-gray-300 mb-2">Phone Number</label>
                <input
                  type="tel"
                  value={data.phone}
                  onChange={(e) => updateData('phone', e.target.value)}
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="+40 123 456 789"
                />
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div>
            <h2 className="text-2xl font-bold text-white mb-4">What industry are you in?</h2>
            <p className="text-gray-300 mb-6">This helps us personalize your experience</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-96 overflow-y-auto">
              {INDUSTRIES.map((industry) => (
                <button
                  key={industry.value}
                  onClick={() => updateData('industry', industry.value)}
                  className={`p-4 rounded-lg text-left transition-all ${
                    data.industry === industry.value
                      ? 'bg-blue-600 border border-blue-400'
                      : 'bg-white/10 border border-white/20 hover:bg-white/20'
                  }`}
                >
                  <span className="text-white font-medium">{industry.label}</span>
                </button>
              ))}
            </div>
          </div>
        );

      case 4:
        return (
          <div>
            <h2 className="text-2xl font-bold text-white mb-4">What's your role?</h2>
            <p className="text-gray-300 mb-6">This helps us tailor your AI assistants</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-96 overflow-y-auto">
              {ROLES.map((role) => (
                <button
                  key={role.value}
                  onClick={() => updateData('role', role.value)}
                  className={`p-4 rounded-lg text-left transition-all ${
                    data.role === role.value
                      ? 'bg-blue-600 border border-blue-400'
                      : 'bg-white/10 border border-white/20 hover:bg-white/20'
                  }`}
                >
                  <span className="text-white font-medium">{role.label}</span>
                </button>
              ))}
            </div>
          </div>
        );

      case 5:
        return (
          <div>
            <h2 className="text-2xl font-bold text-white mb-4">How will you use CoolBits.ai?</h2>
            <p className="text-gray-300 mb-6">Select all that apply - you can access all features from your dashboard</p>
            <div className="space-y-4">
              {USAGE_TYPES.map((usageType) => (
                <button
                  key={usageType.id}
                  onClick={() => toggleUsageType(usageType.id)}
                  className={`w-full p-6 rounded-lg text-left transition-all ${
                    data.selectedUsageTypes.includes(usageType.id)
                      ? 'bg-blue-600 border border-blue-400'
                      : 'bg-white/10 border border-white/20 hover:bg-white/20'
                  }`}
                >
                  <div className="flex items-start space-x-4">
                    <span className="text-2xl">{usageType.icon}</span>
                    <div className="flex-1">
                      <h3 className="text-white font-bold text-lg mb-2">{usageType.title}</h3>
                      <p className="text-gray-300 text-sm mb-3">{usageType.description}</p>
                      <div className="flex flex-wrap gap-2">
                        {usageType.features.map((feature, index) => (
                          <span key={index} className="bg-white/10 px-2 py-1 rounded text-xs text-gray-300">
                            {feature}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                      data.selectedUsageTypes.includes(usageType.id)
                        ? 'bg-blue-500 border-blue-500'
                        : 'border-white/30'
                    }`}>
                      {data.selectedUsageTypes.includes(usageType.id) && (
                        <span className="text-white text-xs">✓</span>
                      )}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        );

      case 6:
        if (data.selectedUsageTypes.includes('business') || data.selectedUsageTypes.includes('agency')) {
          return (
            <div>
              <h2 className="text-2xl font-bold text-white mb-4">Tell us about your business</h2>
              <p className="text-gray-300 mb-6">This helps us create your personalized AI team</p>
              <div className="space-y-4">
                <div>
                  <label className="block text-gray-300 mb-2">Business Name</label>
                  <input
                    type="text"
                    value={data.businessName}
                    onChange={(e) => updateData('businessName', e.target.value)}
                    className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Your Company Name"
                  />
                </div>
                <div>
                  <label className="block text-gray-300 mb-2">Description</label>
                  <textarea
                    value={data.businessDescription}
                    onChange={(e) => updateData('businessDescription', e.target.value)}
                    className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    placeholder="What does your business do?"
                  />
                </div>
                <div>
                  <label className="block text-gray-300 mb-2">Website (optional)</label>
                  <input
                    type="url"
                    value={data.businessWebsite}
                    onChange={(e) => updateData('businessWebsite', e.target.value)}
                    className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="https://yourwebsite.com"
                  />
                </div>
              </div>
            </div>
          );
        }
        return (
          <div className="text-center">
            <h2 className="text-2xl font-bold text-white mb-4">Almost there!</h2>
            <p className="text-gray-300 mb-8">Let's review your selections</p>
          </div>
        );

      case 7:
        return (
          <div className="text-center">
            <h2 className="text-2xl font-bold text-white mb-4">You're all set!</h2>
            <p className="text-gray-300 mb-8">Let's create your personalized CoolBits.ai experience</p>
            <div className="bg-white/10 rounded-lg p-6 mb-6">
              <h3 className="text-white font-bold mb-4">Summary</h3>
              <div className="text-left space-y-2 text-sm">
                <p><span className="text-gray-400">Name:</span> {session?.user?.name}</p>
                <p><span className="text-gray-400">Email:</span> {session?.user?.email}</p>
                <p><span className="text-gray-400">Phone:</span> {data.phone}</p>
                <p><span className="text-gray-400">Industry:</span> {INDUSTRIES.find(i => i.value === data.industry)?.label}</p>
                <p><span className="text-gray-400">Role:</span> {ROLES.find(r => r.value === data.role)?.label}</p>
                <p><span className="text-gray-400">Selected Features:</span></p>
                <div className="ml-4 space-y-1">
                  {data.selectedUsageTypes.map(typeId => {
                    const usageType = USAGE_TYPES.find(t => t.id === typeId);
                    return (
                      <p key={typeId} className="text-blue-300">• {usageType?.title}</p>
                    );
                  })}
                </div>
                {data.businessName && (
                  <p><span className="text-gray-400">Business:</span> {data.businessName}</p>
                )}
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900">
      <div className="max-w-2xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">CoolBits.ai</h1>
          <p className="text-gray-300">Your AI-Powered Business Platform</p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-gray-400 mb-2">
            <span>Step {data.step} of 7</span>
            <span>{Math.round((data.step / 7) * 100)}%</span>
          </div>
          <div className="w-full bg-white/20 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(data.step / 7) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Step Content */}
        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-8 mb-8">
          {renderStep()}
        </div>

        {/* Navigation */}
        <div className="flex justify-between">
          <button
            onClick={prevStep}
            disabled={data.step === 1}
            className="px-6 py-3 bg-white/10 text-white rounded-lg hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Previous
          </button>
          
          {data.step === 7 ? (
            <button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isSubmitting ? 'Creating Account...' : 'Create Account'}
            </button>
          ) : (
            <button
              onClick={nextStep}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Next
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
