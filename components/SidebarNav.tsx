'use client'

export default function SidebarNav() {
  return (
    <nav className="p-4 space-y-6">
      <div className="text-lg font-semibold">Menu</div>
      <ul className="space-y-2 text-sm">
        <li><a className="block px-3 py-2 rounded hover:bg-gray-100" href="#">Overview</a></li>
        <li><a className="block px-3 py-2 rounded hover:bg-gray-100" href="#">Business Map</a></li>
        <li><a className="block px-3 py-2 rounded hover:bg-gray-100" href="#">Audits</a></li>
        <li><a className="block px-3 py-2 rounded hover:bg-gray-100" href="#">Settings</a></li>
      </ul>
      <div className="mt-8 text-xs text-gray-400">v0.1</div>
    </nav>
  )
}
