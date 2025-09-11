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
    const {
      phone,
      industry,
      role,
      selectedUsageTypes,
      businessName,
      businessDescription,
      businessWebsite,
    } = body;

    console.log('Onboarding data received:', {
      email: session.user.email,
      phone,
      industry,
      role,
      selectedUsageTypes,
      businessName,
      businessDescription,
      businessWebsite,
    });

    // For now, just return success without saving to database
    // TODO: Re-enable database saving when Prisma is properly configured
    const mockUser = {
      id: 'temp-user-id',
      email: session.user.email,
      name: session.user.name,
      phone,
      industry,
      role,
      selectedUsageTypes,
    };

    let mockBusiness = null;
    let mockAIAgents: Array<{
      id: string;
      name: string;
      role: string;
      provider: string;
      systemPrompt: string;
    }> = [];

    // Create AI agents if business or agency is selected
    if (selectedUsageTypes.includes('business') || selectedUsageTypes.includes('agency')) {
      if (businessName) {
        mockBusiness = {
          id: 'temp-business-id',
          name: businessName,
          description: businessDescription,
          website: businessWebsite,
          industry,
        };

        // Create mock AI agents
        const aiRoles = ['CEO', 'CTO', 'CMO', 'CFO', 'COO'];
        mockAIAgents = aiRoles.map((aiRole) => ({
          id: `temp-ai-${aiRole.toLowerCase()}`,
          name: `${aiRole} ${businessName}`,
          role: aiRole,
          provider: 'OPENAI',
          systemPrompt: `You are the ${aiRole} of ${businessName}. ${businessDescription ? `Your company: ${businessDescription}` : ''} You provide expert advice and strategic guidance for ${businessName}.`,
        }));
      }
    }

    return NextResponse.json({
      success: true,
      user: mockUser,
      business: mockBusiness,
      aiAgents: mockAIAgents,
    });

  } catch (error) {
    console.error('Onboarding error:', error);
    return NextResponse.json(
      { error: 'Failed to save onboarding data' },
      { status: 500 }
    );
  }
}
