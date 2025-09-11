'use client'

import { useState } from 'react'
import { CheckCircleIcon, SparklesIcon, ArrowRightIcon } from '@heroicons/react/24/outline'

interface LeadThanksProps {
  email: string
  onContinue?: () => void
}

export default function LeadThanks({ email, onContinue }: LeadThanksProps) {
  const [showDetails, setShowDetails] = useState(false)

  return (
    <div className="max-w-2xl mx-auto p-8 bg-white rounded-xl shadow-lg text-center">
      {/* Success Icon */}
      <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-6">
        <CheckCircleIcon className="w-8 h-8 text-green-600" />
      </div>

      {/* Main Message */}
      <h1 className="text-3xl font-bold text-gray-900 mb-4">
        Thank You! 🎉
      </h1>
      
      <p className="text-lg text-gray-600 mb-6">
        We've received your submission and we're excited to work with you!
      </p>

      {/* Email Confirmation */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <p className="text-sm text-blue-800">
          A confirmation email has been sent to{' '}
          <span className="font-semibold">{email}</span>
        </p>
      </div>

      {/* What Happens Next */}
      <div className="bg-gray-50 rounded-lg p-6 mb-6 text-left">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <SparklesIcon className="w-5 h-5 text-primary-600 mr-2" />
          What happens next?
        </h3>
        
        <div className="space-y-3">
          <div className="flex items-start">
            <div className="w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-semibold mr-3 mt-0.5">
              1
            </div>
            <p className="text-gray-700">
              Our team will review your project details within 24 hours
            </p>
          </div>
          
          <div className="flex items-start">
            <div className="w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-semibold mr-3 mt-0.5">
              2
            </div>
            <p className="text-gray-700">
              We'll schedule a discovery call to discuss your needs in detail
            </p>
          </div>
          
          <div className="flex items-start">
            <div className="w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-semibold mr-3 mt-0.5">
              3
            </div>
            <p className="text-gray-700">
              You'll receive a customized proposal tailored to your project
            </p>
          </div>
        </div>
      </div>

      {/* Additional Details Toggle */}
      <div className="mb-6">
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="text-primary-600 hover:text-primary-700 font-medium flex items-center justify-center mx-auto"
        >
          {showDetails ? 'Hide' : 'Show'} additional details
          <ArrowRightIcon className={`w-4 h-4 ml-1 transition-transform ${showDetails ? 'rotate-90' : ''}`} />
        </button>
      </div>

      {/* Additional Details */}
      {showDetails && (
        <div className="bg-gray-50 rounded-lg p-6 mb-6 text-left">
          <h4 className="font-semibold text-gray-900 mb-3">Project Timeline</h4>
          <ul className="text-sm text-gray-700 space-y-2">
            <li>• Initial consultation: 1-2 business days</li>
            <li>• Proposal delivery: 3-5 business days</li>
            <li>• Project kickoff: 1-2 weeks after approval</li>
          </ul>
          
          <h4 className="font-semibold text-gray-900 mb-3 mt-4">Communication</h4>
          <ul className="text-sm text-gray-700 space-y-2">
            <li>• Weekly progress updates</li>
            <li>• Dedicated project manager</li>
            <li>• 24/7 support during development</li>
          </ul>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <button
          onClick={onContinue}
          className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center justify-center"
        >
          Continue Exploring
          <ArrowRightIcon className="w-4 h-4 ml-2" />
        </button>
        
        <a
          href="/dashboard"
          className="border border-gray-300 text-gray-700 hover:bg-gray-50 px-6 py-3 rounded-lg font-medium transition-colors"
        >
          Go to Dashboard
        </a>
      </div>

      {/* Contact Info */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <p className="text-sm text-gray-500 mb-2">
          Questions? We're here to help!
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center text-sm">
          <a
            href="mailto:hello@coolbits.com"
            className="text-primary-600 hover:text-primary-700"
          >
            hello@coolbits.com
          </a>
          <span className="text-gray-400">•</span>
          <a
            href="tel:+1234567890"
            className="text-primary-600 hover:text-primary-700"
          >
            +1 (234) 567-890
          </a>
        </div>
      </div>
    </div>
  )
}
