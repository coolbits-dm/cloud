import { BoardView } from '@/components/BoardView'

export default function DevBoardPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <BoardView panel="dev" />
    </div>
  )
}
