import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    
    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body = await request.json();
    const { message, conversationId } = body;

    if (!message) {
      return NextResponse.json({ error: 'Message is required' }, { status: 400 });
    }

    // For now, return mock response since we don't have Vertex AI fully configured
    // TODO: Integrate with PersonalAI class when Vertex AI is set up
    const mockResponse = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      content: `Thank you for your message: "${message}". This is Andrei's AI responding. I'm currently in development mode, but I'm designed to help you with business strategy, technology insights, and marketing optimization. What specific area would you like to explore?`,
      model: 'gpt-4',
      conversationId: conversationId || `conv_${Date.now()}`,
    };

    // Simulate some processing time
    await new Promise(resolve => setTimeout(resolve, 1000));

    return NextResponse.json(mockResponse);

  } catch (error) {
    console.error('Personal chat error:', error);
    return NextResponse.json(
      { error: 'Failed to process message' },
      { status: 500 }
    );
  }
}
