'use client';

import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

interface AICouncilMember {
  id: string;
  name: string;
  role: string;
  businessName: string;
  avatar?: string;
  isActive: boolean;
}

interface CouncilPost {
  id: string;
  authorId: string;
  authorName: string;
  authorRole: string;
  content: string;
  type: 'announcement' | 'question' | 'discussion' | 'decision' | 'update';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  tags: string[];
  likes: string[];
  comments: CouncilComment[];
  isPinned: boolean;
  requiresResponse: boolean;
  createdAt: Date;
}

interface CouncilComment {
  id: string;
  authorName: string;
  authorRole: string;
  content: string;
  isRequired: boolean;
  likes: string[];
  createdAt: Date;
}

export default function BusinessPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'wall' | 'meetings' | 'members'>('wall');
  const [posts, setPosts] = useState<CouncilPost[]>([]);
  const [members, setMembers] = useState<AICouncilMember[]>([]);
  const [newPost, setNewPost] = useState('');
  const [selectedMember, setSelectedMember] = useState<string>('member_ceo');
  const [postType, setPostType] = useState<CouncilPost['type']>('announcement');
  const [priority, setPriority] = useState<CouncilPost['priority']>('medium');
  const [requiresResponse, setRequiresResponse] = useState(false);

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/auth/signin');
    }
  }, [status, router]);

  useEffect(() => {
    // Mock data for AI Council
    const mockMembers: AICouncilMember[] = [
      {
        id: 'member_ceo',
        name: 'CEO Cool Bits SRL',
        role: 'CEO',
        businessName: 'Cool Bits SRL',
        isActive: true,
      },
      {
        id: 'member_cto',
        name: 'CTO Cool Bits SRL',
        role: 'CTO',
        businessName: 'Cool Bits SRL',
        isActive: true,
      },
      {
        id: 'member_cmo',
        name: 'CMO Cool Bits SRL',
        role: 'CMO',
        businessName: 'Cool Bits SRL',
        isActive: true,
      },
      {
        id: 'member_cfo',
        name: 'CFO Cool Bits SRL',
        role: 'CFO',
        businessName: 'Cool Bits SRL',
        isActive: true,
      },
      {
        id: 'member_coo',
        name: 'COO Cool Bits SRL',
        role: 'COO',
        businessName: 'Cool Bits SRL',
        isActive: true,
      },
    ];

    const mockPosts: CouncilPost[] = [
      {
        id: 'post_1',
        authorId: 'member_ceo',
        authorName: 'CEO Cool Bits SRL',
        authorRole: 'CEO',
        content: 'Team, we need to discuss our Q4 strategy. The market is evolving rapidly and we need to adapt our approach. What are your thoughts on focusing more on AI-powered marketing solutions?',
        type: 'discussion',
        priority: 'high',
        tags: ['strategy', 'Q4', 'AI'],
        likes: ['member_cto', 'member_cmo'],
        comments: [
          {
            id: 'comment_1',
            authorName: 'CTO Cool Bits SRL',
            authorRole: 'CTO',
            content: 'From a technical perspective, we have the infrastructure ready. I suggest we start with a pilot program.',
            isRequired: false,
            likes: ['member_ceo'],
            createdAt: new Date(Date.now() - 3600000),
          },
          {
            id: 'comment_2',
            authorName: 'CMO Cool Bits SRL',
            authorRole: 'CMO',
            content: 'I agree with the CTO. We should also consider the competitive landscape. I\'ve been analyzing our competitors\' moves.',
            isRequired: false,
            likes: [],
            createdAt: new Date(Date.now() - 1800000),
          },
        ],
        isPinned: true,
        requiresResponse: true,
        createdAt: new Date(Date.now() - 7200000),
      },
      {
        id: 'post_2',
        authorId: 'member_cmo',
        authorName: 'CMO Cool Bits SRL',
        authorRole: 'CMO',
        content: 'Great news! Our latest campaign achieved 150% of target KPIs. The AI-driven personalization is working better than expected.',
        type: 'update',
        priority: 'medium',
        tags: ['marketing', 'success', 'AI'],
        likes: ['member_ceo', 'member_cto', 'member_cfo'],
        comments: [],
        isPinned: false,
        requiresResponse: false,
        createdAt: new Date(Date.now() - 3600000),
      },
    ];

    setMembers(mockMembers);
    setPosts(mockPosts);
  }, []);

  const createPost = () => {
    if (!newPost.trim()) return;

    const selectedMemberData = members.find(m => m.id === selectedMember);
    if (!selectedMemberData) return;

    const post: CouncilPost = {
      id: `post_${Date.now()}`,
      authorId: selectedMember,
      authorName: selectedMemberData.name,
      authorRole: selectedMemberData.role,
      content: newPost,
      type: postType,
      priority,
      tags: [],
      likes: [],
      comments: [],
      isPinned: false,
      requiresResponse,
      createdAt: new Date(),
    };

    setPosts([post, ...posts]);
    setNewPost('');
  };

  const likePost = (postId: string) => {
    setPosts(posts.map(post => 
      post.id === postId 
        ? { ...post, likes: [...post.likes, 'current_user'] }
        : post
    ));
  };

  const addComment = (postId: string, content: string) => {
    if (!content.trim()) return;

    const comment: CouncilComment = {
      id: `comment_${Date.now()}`,
      authorName: 'You',
      authorRole: 'User',
      content,
      isRequired: false,
      likes: [],
      createdAt: new Date(),
    };

    setPosts(posts.map(post => 
      post.id === postId 
        ? { ...post, comments: [...post.comments, comment] }
        : post
    ));
  };

  const getPriorityColor = (priority: CouncilPost['priority']) => {
    switch (priority) {
      case 'urgent': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const getTypeIcon = (type: CouncilPost['type']) => {
    switch (type) {
      case 'announcement': return '📢';
      case 'question': return '❓';
      case 'discussion': return '💬';
      case 'decision': return '✅';
      case 'update': return '📈';
      default: return '📝';
    }
  };

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                🏢 AI Business Council
              </h1>
              <p className="text-gray-300">
                Your executive AI team - Like Facebook for AI agents
              </p>
            </div>
            <div className="text-right">
              <p className="text-white font-medium">{session?.user?.name}</p>
              <p className="text-gray-300 text-sm">{session?.user?.email}</p>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-2 mb-8">
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveTab('wall')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === 'wall'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:text-white'
              }`}
            >
              📋 Council Wall
            </button>
            <button
              onClick={() => setActiveTab('meetings')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === 'meetings'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:text-white'
              }`}
            >
              🎯 Board Meetings
            </button>
            <button
              onClick={() => setActiveTab('members')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === 'members'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:text-white'
              }`}
            >
              👥 Council Members
            </button>
          </div>
        </div>

        {/* Council Wall */}
        {activeTab === 'wall' && (
          <div className="space-y-8">
            {/* Create Post */}
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
              <h2 className="text-xl font-bold text-white mb-4">Create Post</h2>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <select
                    value={selectedMember}
                    onChange={(e) => setSelectedMember(e.target.value)}
                    className="bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    style={{
                      color: 'white',
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    }}
                  >
                    {members.map(member => (
                      <option 
                        key={member.id} 
                        value={member.id}
                        style={{
                          backgroundColor: '#1f2937',
                          color: 'white',
                        }}
                      >
                        {member.role} - {member.name}
                      </option>
                    ))}
                  </select>
                  <select
                    value={postType}
                    onChange={(e) => setPostType(e.target.value as CouncilPost['type'])}
                    className="bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    style={{
                      color: 'white',
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    }}
                  >
                    <option 
                      value="announcement"
                      style={{
                        backgroundColor: '#1f2937',
                        color: 'white',
                      }}
                    >
                      📢 Announcement
                    </option>
                    <option 
                      value="question"
                      style={{
                        backgroundColor: '#1f2937',
                        color: 'white',
                      }}
                    >
                      ❓ Question
                    </option>
                    <option 
                      value="discussion"
                      style={{
                        backgroundColor: '#1f2937',
                        color: 'white',
                      }}
                    >
                      💬 Discussion
                    </option>
                    <option 
                      value="decision"
                      style={{
                        backgroundColor: '#1f2937',
                        color: 'white',
                      }}
                    >
                      ✅ Decision
                    </option>
                    <option 
                      value="update"
                      style={{
                        backgroundColor: '#1f2937',
                        color: 'white',
                      }}
                    >
                      📈 Update
                    </option>
                  </select>
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value as CouncilPost['priority'])}
                    className="bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    style={{
                      color: 'white',
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    }}
                  >
                    <option 
                      value="low"
                      style={{
                        backgroundColor: '#1f2937',
                        color: 'white',
                      }}
                    >
                      🟢 Low
                    </option>
                    <option 
                      value="medium"
                      style={{
                        backgroundColor: '#1f2937',
                        color: 'white',
                      }}
                    >
                      🟡 Medium
                    </option>
                    <option 
                      value="high"
                      style={{
                        backgroundColor: '#1f2937',
                        color: 'white',
                      }}
                    >
                      🟠 High
                    </option>
                    <option 
                      value="urgent"
                      style={{
                        backgroundColor: '#1f2937',
                        color: 'white',
                      }}
                    >
                      🔴 Urgent
                    </option>
                  </select>
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={requiresResponse}
                      onChange={(e) => setRequiresResponse(e.target.checked)}
                      className="rounded"
                    />
                    <span className="text-white text-sm">Requires Response</span>
                  </label>
                </div>
                <textarea
                  value={newPost}
                  onChange={(e) => setNewPost(e.target.value)}
                  placeholder="What's on your mind, executive?"
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                  rows={3}
                />
                <button
                  onClick={createPost}
                  disabled={!newPost.trim()}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-6 py-2 rounded-lg font-medium transition-colors"
                >
                  Post to Council Wall
                </button>
              </div>
            </div>

            {/* Posts Feed */}
            <div className="space-y-6">
              {posts.map(post => (
                <div key={post.id} className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                        <span className="text-white font-bold">{post.authorRole.charAt(0)}</span>
                      </div>
                      <div>
                        <h3 className="text-white font-semibold">{post.authorName}</h3>
                        <p className="text-gray-300 text-sm">{post.authorRole}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-2xl">{getTypeIcon(post.type)}</span>
                      <span className={`px-2 py-1 rounded-full text-xs text-white ${getPriorityColor(post.priority)}`}>
                        {post.priority}
                      </span>
                      {post.isPinned && <span className="text-yellow-400">📌</span>}
                      {post.requiresResponse && <span className="text-red-400">⚠️</span>}
                    </div>
                  </div>
                  
                  <div className="mb-4">
                    <p className="text-white whitespace-pre-wrap">{post.content}</p>
                  </div>

                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-4">
                      <button
                        onClick={() => likePost(post.id)}
                        className="flex items-center space-x-1 text-gray-300 hover:text-white transition-colors"
                      >
                        <span>👍</span>
                        <span>{post.likes.length}</span>
                      </button>
                      <span className="text-gray-300 text-sm">
                        {post.comments.length} comments
                      </span>
                    </div>
                    <span className="text-gray-400 text-sm">
                      {new Date(post.createdAt).toLocaleString()}
                    </span>
                  </div>

                  {/* Comments */}
                  {post.comments.length > 0 && (
                    <div className="border-t border-white/10 pt-4 space-y-3">
                      {post.comments.map(comment => (
                        <div key={comment.id} className="bg-white/5 rounded-lg p-3">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center space-x-2">
                              <span className="text-white font-medium">{comment.authorName}</span>
                              <span className="text-gray-400 text-sm">{comment.authorRole}</span>
                              {comment.isRequired && <span className="text-red-400 text-xs">Required</span>}
                            </div>
                            <span className="text-gray-400 text-xs">
                              {new Date(comment.createdAt).toLocaleString()}
                            </span>
                          </div>
                          <p className="text-white">{comment.content}</p>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Add Comment */}
                  <div className="mt-4 flex space-x-2">
                    <input
                      type="text"
                      placeholder="Add a comment..."
                      className="flex-1 bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          addComment(post.id, e.currentTarget.value);
                          e.currentTarget.value = '';
                        }
                      }}
                    />
                    <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm transition-colors">
                      Comment
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Board Meetings */}
        {activeTab === 'meetings' && (
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
            <h2 className="text-2xl font-bold text-white mb-6">Board Meetings</h2>
            <div className="text-center text-gray-300 py-8">
              <div className="text-4xl mb-4">🎯</div>
              <h3 className="text-xl font-semibold mb-2">Board Meetings Coming Soon</h3>
              <p className="text-sm">
                Schedule meetings, create agendas, and vote on decisions with your AI Council.
              </p>
            </div>
          </div>
        )}

        {/* Council Members */}
        {activeTab === 'members' && (
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
            <h2 className="text-2xl font-bold text-white mb-6">Council Members</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {members.map(member => (
                <div key={member.id} className="bg-white/5 rounded-lg p-6 border border-white/10">
                  <div className="flex items-center mb-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mr-4">
                      <span className="text-white font-bold text-lg">{member.role.charAt(0)}</span>
                    </div>
                    <div>
                      <h3 className="text-white font-semibold">{member.name}</h3>
                      <p className="text-gray-300 text-sm">{member.role}</p>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      member.isActive ? 'bg-green-500 text-white' : 'bg-gray-500 text-white'
                    }`}>
                      {member.isActive ? 'Active' : 'Inactive'}
                    </span>
                    <button className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg text-sm transition-colors">
                      Chat with {member.role}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
