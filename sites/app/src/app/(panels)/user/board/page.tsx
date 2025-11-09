// src/app/(panels)/user/board/page.tsx
import { BoardView } from '@/components/BoardView'

export default function UserBoardPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <BoardView panel="user" />
    </div>
  )
}
