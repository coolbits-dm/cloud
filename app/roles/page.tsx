'use client';

import { useState } from 'react';

interface RoleMapping {
  role: string;
  user: string;
  subdomain: string;
  key: string;
}

interface RoleCategory {
  name: string;
  roles: RoleMapping[];
}

const roleCategories: RoleCategory[] = [
  {
    name: "Executive",
    roles: [
      { role: "ceo", user: "ceo@coolbits.ai", subdomain: "ceo.roles.coolbits.ai", key: "xai_api_key_ceo" },
      { role: "strategy-office-cso", user: "cso@coolbits.ai", subdomain: "cso.roles.coolbits.ai", key: "xai_api_key_cso" },
      { role: "board", user: "board@coolbits.ai", subdomain: "board.roles.coolbits.ai", key: "xai_api_key_board" }
    ]
  },
  {
    name: "Technology",
    roles: [
      { role: "cto", user: "cto@coolbits.ai", subdomain: "cto.roles.coolbits.ai", key: "xai_api_key_cto" },
      { role: "engineering/backend", user: "backend@coolbits.ai", subdomain: "backend.roles.coolbits.ai", key: "xai_api_key_backend" },
      { role: "engineering/frontend", user: "frontend@coolbits.ai", subdomain: "frontend.roles.coolbits.ai", key: "xai_api_key_frontend" },
      { role: "engineering/mobile", user: "mobile@coolbits.ai", subdomain: "mobile.roles.coolbits.ai", key: "xai_api_key_mobile" },
      { role: "engineering/platform", user: "platform@coolbits.ai", subdomain: "platform.roles.coolbits.ai", key: "xai_api_key_platform" },
      { role: "engineering/architecture", user: "architecture@coolbits.ai", subdomain: "architecture.roles.coolbits.ai", key: "xai_api_key_architecture" },
      { role: "devops-sre", user: "devops@coolbits.ai", subdomain: "devops.roles.coolbits.ai", key: "xai_api_key_devops" },
      { role: "qa-quality", user: "qa@coolbits.ai", subdomain: "qa.roles.coolbits.ai", key: "xai_api_key_qa" },
      { role: "research-rnd", user: "rnd@coolbits.ai", subdomain: "rnd.roles.coolbits.ai", key: "xai_api_key_rnd" }
    ]
  },
  {
    name: "Product",
    roles: [
      { role: "cpo", user: "cpo@coolbits.ai", subdomain: "cpo.roles.coolbits.ai", key: "xai_api_key_cpo" },
      { role: "product-management", user: "productmgmt@coolbits.ai", subdomain: "productmgmt.roles.coolbits.ai", key: "xai_api_key_productmgmt" },
      { role: "product-ops", user: "productops@coolbits.ai", subdomain: "productops.roles.coolbits.ai", key: "xai_api_key_productops" },
      { role: "design-ux", user: "uxdesign@coolbits.ai", subdomain: "uxdesign.roles.coolbits.ai", key: "xai_api_key_uxdesign" },
      { role: "ux-research", user: "uxresearch@coolbits.ai", subdomain: "uxresearch.roles.coolbits.ai", key: "xai_api_key_uxresearch" },
      { role: "docs", user: "docs@coolbits.ai", subdomain: "docs.roles.coolbits.ai", key: "xai_api_key_docs" }
    ]
  },
  {
    name: "Data",
    roles: [
      { role: "cdo", user: "cdo@coolbits.ai", subdomain: "cdo.roles.coolbits.ai", key: "xai_api_key_cdo" },
      { role: "data-engineering", user: "dataeng@coolbits.ai", subdomain: "dataeng.roles.coolbits.ai", key: "xai_api_key_dataeng" },
      { role: "analytics-bi", user: "analytics@coolbits.ai", subdomain: "analytics.roles.coolbits.ai", key: "xai_api_key_analytics" },
      { role: "ml-ai", user: "mlai@coolbits.ai", subdomain: "mlai.roles.coolbits.ai", key: "xai_api_key_mlai" }
    ]
  },
  {
    name: "Security",
    roles: [
      { role: "ciso", user: "ciso@coolbits.ai", subdomain: "ciso.roles.coolbits.ai", key: "xai_api_key_ciso" },
      { role: "appsec", user: "appsec@coolbits.ai", subdomain: "appsec.roles.coolbits.ai", key: "xai_api_key_appsec" },
      { role: "secops", user: "secops@coolbits.ai", subdomain: "secops.roles.coolbits.ai", key: "xai_api_key_secops" },
      { role: "grc", user: "grc@coolbits.ai", subdomain: "grc.roles.coolbits.ai", key: "xai_api_key_grc" },
      { role: "compliance", user: "compliance@coolbits.ai", subdomain: "compliance.roles.coolbits.ai", key: "xai_api_key_compliance" }
    ]
  },
  {
    name: "IT",
    roles: [
      { role: "cio", user: "cio@coolbits.ai", subdomain: "cio.roles.coolbits.ai", key: "xai_api_key_cio" },
      { role: "helpdesk", user: "helpdesk@coolbits.ai", subdomain: "helpdesk.roles.coolbits.ai", key: "xai_api_key_helpdesk" },
      { role: "identity-access", user: "iam@coolbits.ai", subdomain: "iam.roles.coolbits.ai", key: "xai_api_key_iam" },
      { role: "networking", user: "networking@coolbits.ai", subdomain: "networking.roles.coolbits.ai", key: "xai_api_key_networking" },
      { role: "endpoint-management", user: "endpoint@coolbits.ai", subdomain: "endpoint.roles.coolbits.ai", key: "xai_api_key_endpoint" }
    ]
  },
  {
    name: "Operations",
    roles: [
      { role: "coo", user: "coo@coolbits.ai", subdomain: "coo.roles.coolbits.ai", key: "xai_api_key_coo" },
      { role: "pmo-program-management", user: "pmo@coolbits.ai", subdomain: "pmo.roles.coolbits.ai", key: "xai_api_key_pmo" },
      { role: "procurement", user: "procurement@coolbits.ai", subdomain: "procurement.roles.coolbits.ai", key: "xai_api_key_procurement" },
      { role: "facilities", user: "facilities@coolbits.ai", subdomain: "facilities.roles.coolbits.ai", key: "xai_api_key_facilities" },
      { role: "logistics", user: "logistics@coolbits.ai", subdomain: "logistics.roles.coolbits.ai", key: "xai_api_key_logistics" }
    ]
  },
  {
    name: "Finance",
    roles: [
      { role: "cfo", user: "cfo@coolbits.ai", subdomain: "cfo.roles.coolbits.ai", key: "xai_api_key_cfo" },
      { role: "accounting", user: "accounting@coolbits.ai", subdomain: "accounting.roles.coolbits.ai", key: "xai_api_key_accounting" },
      { role: "fpa", user: "fpa@coolbits.ai", subdomain: "fpa.roles.coolbits.ai", key: "xai_api_key_fpa" },
      { role: "treasury", user: "treasury@coolbits.ai", subdomain: "treasury.roles.coolbits.ai", key: "xai_api_key_treasury" },
      { role: "payroll", user: "payroll@coolbits.ai", subdomain: "payroll.roles.coolbits.ai", key: "xai_api_key_payroll" }
    ]
  },
  {
    name: "People",
    roles: [
      { role: "chro", user: "chro@coolbits.ai", subdomain: "chro.roles.coolbits.ai", key: "xai_api_key_chro" },
      { role: "recruiting-talent", user: "recruiting@coolbits.ai", subdomain: "recruiting.roles.coolbits.ai", key: "xai_api_key_recruiting" },
      { role: "people-ops-hr", user: "peopleops@coolbits.ai", subdomain: "peopleops.roles.coolbits.ai", key: "xai_api_key_peopleops" },
      { role: "learning-development", user: "learning@coolbits.ai", subdomain: "learning.roles.coolbits.ai", key: "xai_api_key_learning" },
      { role: "comp-benefits", user: "compbenefits@coolbits.ai", subdomain: "compbenefits.roles.coolbits.ai", key: "xai_api_key_compbenefits" }
    ]
  },
  {
    name: "Revenue",
    roles: [
      { role: "cro", user: "cro@coolbits.ai", subdomain: "cro.roles.coolbits.ai", key: "xai_api_key_cro" },
      { role: "sales", user: "sales@coolbits.ai", subdomain: "sales.roles.coolbits.ai", key: "xai_api_key_sales" },
      { role: "sales-ops", user: "salesops@coolbits.ai", subdomain: "salesops.roles.coolbits.ai", key: "xai_api_key_salesops" },
      { role: "partnerships", user: "partnerships@coolbits.ai", subdomain: "partnerships.roles.coolbits.ai", key: "xai_api_key_partnerships" },
      { role: "customer-success", user: "customersuccess@coolbits.ai", subdomain: "customersuccess.roles.coolbits.ai", key: "xai_api_key_customersuccess" }
    ]
  },
  {
    name: "Marketing",
    roles: [
      { role: "cmo", user: "cmo@coolbits.ai", subdomain: "cmo.roles.coolbits.ai", key: "xai_api_key_cmo" },
      { role: "brand", user: "brand@coolbits.ai", subdomain: "brand.roles.coolbits.ai", key: "xai_api_key_brand" },
      { role: "performance-growth", user: "growth@coolbits.ai", subdomain: "growth.roles.coolbits.ai", key: "xai_api_key_growth" },
      { role: "content", user: "content@coolbits.ai", subdomain: "content.roles.coolbits.ai", key: "xai_api_key_content" },
      { role: "pr-comms", user: "prcomms@coolbits.ai", subdomain: "prcomms.roles.coolbits.ai", key: "xai_api_key_prcomms" },
      { role: "events", user: "events@coolbits.ai", subdomain: "events.roles.coolbits.ai", key: "xai_api_key_events" }
    ]
  },
  {
    name: "Legal",
    roles: [
      { role: "clo-gc", user: "clo@coolbits.ai", subdomain: "clo.roles.coolbits.ai", key: "xai_api_key_clo" },
      { role: "contracts", user: "contracts@coolbits.ai", subdomain: "contracts.roles.coolbits.ai", key: "xai_api_key_contracts" },
      { role: "privacy", user: "privacy@coolbits.ai", subdomain: "privacy.roles.coolbits.ai", key: "xai_api_key_privacy" },
      { role: "ip", user: "ip@coolbits.ai", subdomain: "ip.roles.coolbits.ai", key: "xai_api_key_ip" },
      { role: "regulatory", user: "regulatory@coolbits.ai", subdomain: "regulatory.roles.coolbits.ai", key: "xai_api_key_regulatory" }
    ]
  }
];

export default function RolesPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>('Executive');
  const [selectedRole, setSelectedRole] = useState<RoleMapping | null>(null);

  const currentCategory = roleCategories.find(cat => cat.name === selectedCategory);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">CoolBits.ai Role Management</h1>
          <p className="text-gray-600">Organizational structure with role-based AI access</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Category Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-4">
              <h2 className="text-lg font-semibold mb-4">Categories</h2>
              <div className="space-y-2">
                {roleCategories.map((category) => (
                  <button
                    key={category.name}
                    onClick={() => setSelectedCategory(category.name)}
                    className={`w-full text-left px-3 py-2 rounded-md transition-colors ${
                      selectedCategory === category.name
                        ? 'bg-blue-100 text-blue-700'
                        : 'hover:bg-gray-100'
                    }`}
                  >
                    <div className="font-medium">{category.name}</div>
                    <div className="text-sm text-gray-500">{category.roles.length} roles</div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Roles Grid */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-6">{selectedCategory} Roles</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {currentCategory?.roles.map((role) => (
                  <div
                    key={role.role}
                    className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => setSelectedRole(role)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold text-gray-900 capitalize">
                        {role.role.replace('-', ' ')}
                      </h3>
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    </div>
                    
                    <div className="space-y-1 text-sm text-gray-600">
                      <div><strong>User:</strong> {role.user}</div>
                      <div><strong>Subdomain:</strong> {role.subdomain}</div>
                      <div><strong>API Key:</strong> {role.key}</div>
                    </div>
                    
                    <div className="mt-3 pt-3 border-t">
                      <a
                        href={`https://${role.subdomain}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 text-sm"
                      >
                        Access Role Portal →
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Role Details Modal */}
        {selectedRole && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-md w-full p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold capitalize">
                  {selectedRole.role.replace('-', ' ')}
                </h3>
                <button
                  onClick={() => setSelectedRole(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700">User Email</label>
                  <div className="mt-1 p-2 bg-gray-50 rounded border">{selectedRole.user}</div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Subdomain</label>
                  <div className="mt-1 p-2 bg-gray-50 rounded border">{selectedRole.subdomain}</div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">API Key Reference</label>
                  <div className="mt-1 p-2 bg-gray-50 rounded border font-mono text-sm">{selectedRole.key}</div>
                </div>
              </div>
              
              <div className="mt-6 flex space-x-3">
                <button
                  onClick={() => window.open(`https://${selectedRole.subdomain}`, '_blank')}
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                >
                  Access Portal
                </button>
                <button
                  onClick={() => setSelectedRole(null)}
                  className="flex-1 bg-gray-200 text-gray-800 px-4 py-2 rounded-md hover:bg-gray-300"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
