import React, { useState } from 'react';
import { ChatBubbleOvalLeftEllipsisIcon } from '@heroicons/react/24/outline';
import ChatWithMap from '@/components/ChatWithMap';

const ChatDock: React.FC = () => {
  const [open, setOpen] = useState(false);

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Butonul de deschidere a chatului */}
      {!open && (
        <button 
          onClick={() => setOpen(true)} 
          className="rounded-full p-3 bg-blue-600 hover:bg-blue-700 text-white shadow-lg"
          aria-label="Deschide chatul"
        >
          <ChatBubbleOvalLeftEllipsisIcon className="h-6 w-6" />
        </button>
      )}

      {/* Fereastra de chat + Business Map */}
      <div className={`${open ? 'block' : 'hidden'} bg-white border border-gray-300 rounded-lg shadow-lg`}>
        <ChatWithMap onClose={() => setOpen(false)} />
      </div>
    </div>
  );
};

export default ChatDock;
