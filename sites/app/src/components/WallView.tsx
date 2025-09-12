// src/components/WallView.tsx
'use client'

import { useState, useEffect } from 'react'
import { useWallStore } from '@/stores/wallStore'
import { useTokensStore } from '@/stores/tokensStore'
import { getTariffCost } from '@/lib/cbtokens'
import { MessageSquare, Send, Bot, Clock, CheckCircle, XCircle } from 'lucide-react'

interface WallViewProps {
  panel: string
}

export function WallView({ panel }: WallViewProps) {
  const [newPostText, setNewPostText] = useState('')
  const [newCommentText, setNewCommentText] = useState('')
  const [commentingPostId, setCommentingPostId] = useState<string | null>(null)
  
  const { walls, loading, error, loadWall, addPost, addComment } = useWallStore()
  const { debitTokens } = useTokensStore()

  const wall = walls[panel]

  useEffect(() => {
    loadWall(panel)
  }, [panel, loadWall])

  const handleSubmitPost = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newPostText.trim()) return

    try {
      const r = await fetch("/api/gw/nha/invoke", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ panel, text: newPostText })
      });
      const j = await r.json(); // { post_id, invocations: [...] }
      addLocalPost(j.post_id, newPostText);
      startPollingInvocations(j.post_id);
      setNewPostText('');
    } catch (error) {
      console.error('Failed to submit post:', error)
    }
  }

  function addLocalPost(postId: string, text: string) {
    // Add post locally for immediate UI feedback
    const newPost = {
      id: postId,
      author: 'current_user',
      ts: new Date().toISOString(),
      text,
      attachments: [],
      mentions: text.match(/@\w+/g) || [],
      nha_invocations: [],
      comments: []
    };
    // This would integrate with your wall store
    console.log('Added local post:', newPost);
  }

  function startPollingInvocations(postId: string) {
    let tries = 0;
    const timer = setInterval(async () => {
      tries++;
      try {
        const r = await fetch(`/api/gw/invocations?post_id=${encodeURIComponent(postId)}`);
        if (!r.ok) return;
        const j = await r.json();
        if (Array.isArray(j.comments) && j.comments.length) {
          mergeComments(postId, j.comments);
          clearInterval(timer);
        }
      } catch {}
      if (tries > 20) clearInterval(timer); // ~30s cap
    }, 1500);
  }

  function mergeComments(postId: string, comments: any[]) {
    // Merge NHA comments into local post
    console.log('Merging comments for post:', postId, comments);
  }

  const handleSubmitComment = async (postId: string, e: React.FormEvent) => {
    e.preventDefault()
    if (!newCommentText.trim()) return

    try {
      await addComment(panel, postId, newCommentText, 'current_user')
      setNewCommentText('')
      setCommentingPostId(null)
    } catch (error) {
      console.error('Failed to submit comment:', error)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'queued': return <Clock className="w-3 h-3 text-yellow-500" />
      case 'running': return <Bot className="w-3 h-3 text-blue-500 animate-spin" />
      case 'done': return <CheckCircle className="w-3 h-3 text-green-500" />
      case 'error': return <XCircle className="w-3 h-3 text-red-500" />
      default: return null
    }
  }

  if (loading) {
    return <div className="p-4 text-center">Loading wall...</div>
  }

  if (error) {
    return <div className="p-4 text-center text-red-600">Error: {error}</div>
  }

  if (!wall) {
    return <div className="p-4 text-center">No wall data</div>
  }

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-6">
      <div className="flex items-center gap-2 mb-6">
        <MessageSquare className="w-6 h-6" />
        <h1 className="text-2xl font-bold capitalize">{panel} Wall</h1>
      </div>

      {/* Post Composer */}
      <form onSubmit={handleSubmitPost} className="bg-white border rounded-lg p-4">
        <textarea
          value={newPostText}
          onChange={(e) => setNewPostText(e.target.value)}
          placeholder={`Post to ${panel} wall... Use @nha:sentiment, @nha:summarize, @nha:tagging for AI analysis`}
          className="w-full p-3 border rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows={3}
        />
        <div className="flex justify-between items-center mt-3">
          <span className="text-sm text-gray-500">
            Cost: {Math.abs(getTariffCost('WALL_POST'))} cbT
            {newPostText.match(/@nha:\w+/g)?.length && (
              <span className="ml-2 text-orange-600">
                + {newPostText.match(/@nha:\w+/g)!.length * Math.abs(getTariffCost('NHA_INVOCATION'))} cbT for NHA
              </span>
            )}
          </span>
          <button
            type="submit"
            disabled={!newPostText.trim()}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
            Post
          </button>
        </div>
      </form>

      {/* Posts */}
      <div className="space-y-4">
        {wall.posts.map((post) => (
          <div key={post.id} className="bg-white border rounded-lg p-4">
            <div className="flex items-start justify-between mb-3">
              <div>
                <div className="font-medium">{post.author}</div>
                <div className="text-sm text-gray-500">
                  {new Date(post.ts).toLocaleString()}
                </div>
              </div>
              <button
                onClick={() => setCommentingPostId(commentingPostId === post.id ? null : post.id)}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                {commentingPostId === post.id ? 'Cancel' : 'Comment'}
              </button>
            </div>

            <div className="mb-3">
              <p className="whitespace-pre-wrap">{post.text}</p>
            </div>

            {/* NHA Invocations */}
            {post.nha_invocations.length > 0 && (
              <div className="mb-3 p-3 bg-gray-50 rounded-lg">
                <div className="text-sm font-medium mb-2">AI Analysis:</div>
                <div className="space-y-2">
                  {post.nha_invocations.map((invocation, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-sm">
                      {getStatusIcon(invocation.status)}
                      <span className="font-medium">{invocation.role}</span>
                      <span className="text-gray-500">({invocation.status})</span>
                      {invocation.result_ref && (
                        <span className="text-blue-600">→ {invocation.result_ref}</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Comments */}
            {post.comments.length > 0 && (
              <div className="space-y-2">
                {post.comments.map((comment, idx) => (
                  <div key={idx} className="pl-4 border-l-2 border-gray-200">
                    <div className="text-sm font-medium">{comment.author}</div>
                    <div className="text-sm text-gray-500">
                      {new Date(comment.ts).toLocaleString()}
                    </div>
                    <p className="text-sm">{comment.text}</p>
                  </div>
                ))}
              </div>
            )}

            {/* Comment Form */}
            {commentingPostId === post.id && (
              <form onSubmit={(e) => handleSubmitComment(post.id, e)} className="mt-3">
                <textarea
                  value={newCommentText}
                  onChange={(e) => setNewCommentText(e.target.value)}
                  placeholder="Add a comment..."
                  className="w-full p-2 border rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={2}
                />
                <div className="flex justify-end gap-2 mt-2">
                  <button
                    type="button"
                    onClick={() => setCommentingPostId(null)}
                    className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={!newCommentText.trim()}
                    className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                  >
                    Comment
                  </button>
                </div>
              </form>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
