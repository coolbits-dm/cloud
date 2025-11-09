'use client';

import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Suspense } from 'react';

function AuthErrorContent() {
  const searchParams = useSearchParams();
  const error = searchParams.get('error');

  const getErrorMessage = (error: string | null) => {
    switch (error) {
      case 'Configuration':
        return 'There is a problem with the server configuration. Please contact support.';
      case 'AccessDenied':
        return 'You do not have permission to sign in.';
      case 'Verification':
        return 'The verification token has expired or has already been used.';
      case 'Default':
      default:
        return 'An error occurred during authentication. Please try again.';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
      <div className="bg-white/10 backdrop-blur-sm rounded-lg p-8 max-w-md w-full">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-white text-2xl">⚠️</span>
          </div>
          <h1 className="text-2xl font-bold text-white mb-4">Authentication Error</h1>
          <p className="text-gray-300 mb-6">{getErrorMessage(error)}</p>
          
          <div className="space-y-3">
            <Link 
              href="/onboarding"
              className="block w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              Try Again
            </Link>
            <Link 
              href="/"
              className="block w-full bg-white/10 text-white py-3 px-4 rounded-lg font-medium hover:bg-white/20 transition-colors"
            >
              Go Home
            </Link>
          </div>
          
          <div className="mt-6 text-sm text-gray-400">
            <p>Error Code: {error || 'Unknown'}</p>
            <p>If this problem persists, please contact support.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function AuthErrorPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    }>
      <AuthErrorContent />
    </Suspense>
  );
}
