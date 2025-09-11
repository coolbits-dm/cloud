import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    
    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // For now, return mock data since we don't have database properly configured
    // TODO: Re-enable database queries when Prisma is properly configured
    const mockUser = {
      id: 'temp-user-id',
      name: session.user.name,
      email: session.user.email,
      phone: '+40 123 456 789',
      industry: 'marketing_advertising',
      role: 'ceo_founder',
      selectedUsageTypes: ['personal', 'business', 'agency', 'developer'],
      image: session.user.image,
      createdAt: new Date().toISOString(),
    };

    // Mock business data
    const mockBusiness = {
      id: 'temp-business-id',
      name: 'Cool Bits SRL',
      description: 'AI Digital Marketing Agency',
      website: 'https://coolbits.ai',
      industry: 'marketing_advertising',
    };

    // Mock AI agents
    const mockAIAgents = [
      {
        id: 'temp-ai-ceo',
        name: 'CEO Cool Bits SRL',
        role: 'CEO',
        provider: 'OPENAI',
        systemPrompt: 'You are the CEO of Cool Bits SRL. Your company: AI Digital Marketing Agency. You provide expert advice and strategic guidance for Cool Bits SRL.',
      },
      {
        id: 'temp-ai-cto',
        name: 'CTO Cool Bits SRL',
        role: 'CTO',
        provider: 'OPENAI',
        systemPrompt: 'You are the CTO of Cool Bits SRL. Your company: AI Digital Marketing Agency. You provide expert advice and strategic guidance for Cool Bits SRL.',
      },
      {
        id: 'temp-ai-cmo',
        name: 'CMO Cool Bits SRL',
        role: 'CMO',
        provider: 'OPENAI',
        systemPrompt: 'You are the CMO of Cool Bits SRL. Your company: AI Digital Marketing Agency. You provide expert advice and strategic guidance for Cool Bits SRL.',
      },
      {
        id: 'temp-ai-cfo',
        name: 'CFO Cool Bits SRL',
        role: 'CFO',
        provider: 'OPENAI',
        systemPrompt: 'You are the CFO of Cool Bits SRL. Your company: AI Digital Marketing Agency. You provide expert advice and strategic guidance for Cool Bits SRL.',
      },
      {
        id: 'temp-ai-coo',
        name: 'COO Cool Bits SRL',
        role: 'COO',
        provider: 'OPENAI',
        systemPrompt: 'You are the COO of Cool Bits SRL. Your company: AI Digital Marketing Agency. You provide expert advice and strategic guidance for Cool Bits SRL.',
      },
    ];

    return NextResponse.json({
      user: mockUser,
      business: mockBusiness,
      aiAgents: mockAIAgents,
    });

  } catch (error) {
    console.error('Profile fetch error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch profile' },
      { status: 500 }
    );
  }
}
