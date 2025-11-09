// src/components/BoardView.tsx
'use client'

import { useState, useEffect } from 'react'
import { useBoardStore } from '@/stores/boardStore'
import { useTokensStore } from '@/stores/tokensStore'
import { getTariffCost } from '@/lib/cbtokens'
import { Users, User, Bot, Calendar, Plus, FileText } from 'lucide-react'

interface BoardViewProps {
  panel: string
}

export function BoardView({ panel }: BoardViewProps) {
  const [newMeetingNotes, setNewMeetingNotes] = useState('')
  const [showMeetingForm, setShowMeetingForm] = useState(false)
  const [newMember, setNewMember] = useState({
    display: '',
    role: 'reviewer',
    agent_type: 'human' as 'human' | 'non-human'
  })
  const [showMemberForm, setShowMemberForm] = useState(false)
  
  const { boards, loading, error, loadBoard, startMeeting, addMember } = useBoardStore()
  const { debitTokens } = useTokensStore()

  const board = boards[panel]

  useEffect(() => {
    loadBoard(panel)
  }, [panel, loadBoard])

  const handleStartMeeting = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newMeetingNotes.trim()) return

    try {
      // Debit tokens for board meeting
      await debitTokens(Math.abs(getTariffCost('BOARD_MEETING')), 'BOARD_MEETING', `meeting_${Date.now()}`)
      
      // Start meeting
      await startMeeting(panel, newMeetingNotes)
      setNewMeetingNotes('')
      setShowMeetingForm(false)
    } catch (error) {
      console.error('Failed to start meeting:', error)
    }
  }

  const handleAddMember = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newMember.display.trim()) return

    try {
      await addMember(panel, newMember)
      setNewMember({ display: '', role: 'reviewer', agent_type: 'human' })
      setShowMemberForm(false)
    } catch (error) {
      console.error('Failed to add member:', error)
    }
  }

  if (loading) {
    return <div className="p-4 text-center">Loading board...</div>
  }

  if (error) {
    return <div className="p-4 text-center text-red-600">Error: {error}</div>
  }

  if (!board) {
    return <div className="p-4 text-center">No board data</div>
  }

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-6">
      <div className="flex items-center gap-2 mb-6">
        <Users className="w-6 h-6" />
        <h1 className="text-2xl font-bold capitalize">{board.board_name}</h1>
      </div>

      {/* Charter */}
      <div className="bg-white border rounded-lg p-4">
        <h2 className="font-medium mb-2">Charter</h2>
        <p className="text-gray-700">{board.charter}</p>
      </div>

      {/* Members */}
      <div className="bg-white border rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-medium">Members</h2>
          <button
            onClick={() => setShowMemberForm(!showMemberForm)}
            className="flex items-center gap-2 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            <Plus className="w-4 h-4" />
            Add Member
          </button>
        </div>

        {/* Add Member Form */}
        {showMemberForm && (
          <form onSubmit={handleAddMember} className="mb-4 p-3 bg-gray-50 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <input
                type="text"
                value={newMember.display}
                onChange={(e) => setNewMember({ ...newMember, display: e.target.value })}
                placeholder="Member name"
                className="p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              <select
                value={newMember.role}
                onChange={(e) => setNewMember({ ...newMember, role: e.target.value })}
                className="p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="chair">Chair</option>
                <option value="reviewer">Reviewer</option>
                <option value="analyst">Analyst</option>
                <option value="scribe">Scribe</option>
              </select>
              <select
                value={newMember.agent_type}
                onChange={(e) => setNewMember({ ...newMember, agent_type: e.target.value as 'human' | 'non-human' })}
                className="p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="human">Human</option>
                <option value="non-human">AI Agent</option>
              </select>
            </div>
            <div className="flex justify-end gap-2 mt-3">
              <button
                type="button"
                onClick={() => setShowMemberForm(false)}
                className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Add Member
              </button>
            </div>
          </form>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {board.members.map((member) => (
            <div key={member.id} className="flex items-center gap-3 p-3 border rounded-lg">
              {member.agent_type === 'human' ? (
                <User className="w-5 h-5 text-blue-500" />
              ) : (
                <Bot className="w-5 h-5 text-green-500" />
              )}
              <div className="flex-1">
                <div className="font-medium">{member.display}</div>
                <div className="text-sm text-gray-500 capitalize">{member.role}</div>
              </div>
              <div className="text-xs text-gray-400 capitalize">
                {member.agent_type}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Meetings */}
      <div className="bg-white border rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-medium">Meetings</h2>
          <button
            onClick={() => setShowMeetingForm(!showMeetingForm)}
            className="flex items-center gap-2 px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
          >
            <Calendar className="w-4 h-4" />
            Start Meeting
          </button>
        </div>

        {/* Start Meeting Form */}
        {showMeetingForm && (
          <form onSubmit={handleStartMeeting} className="mb-4 p-3 bg-gray-50 rounded-lg">
            <textarea
              value={newMeetingNotes}
              onChange={(e) => setNewMeetingNotes(e.target.value)}
              placeholder="Meeting notes..."
              className="w-full p-3 border rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={4}
              required
            />
            <div className="flex justify-between items-center mt-3">
              <span className="text-sm text-gray-500">
                Cost: {Math.abs(getTariffCost('BOARD_MEETING'))} cbT
              </span>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setShowMeetingForm(false)}
                  className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex items-center gap-2 px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                >
                  <FileText className="w-4 h-4" />
                  Start Meeting
                </button>
              </div>
            </div>
          </form>
        )}

        <div className="space-y-3">
          {board.meetings.map((meeting) => (
            <div key={meeting.id} className="p-3 border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Calendar className="w-4 h-4 text-gray-500" />
                <span className="text-sm text-gray-500">
                  {new Date(meeting.ts).toLocaleString()}
                </span>
              </div>
              <p className="text-sm whitespace-pre-wrap">{meeting.notes}</p>
              {meeting.attendees.length > 0 && (
                <div className="mt-2 text-xs text-gray-500">
                  Attendees: {meeting.attendees.join(', ')}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
