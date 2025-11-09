import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { prisma } from '@/lib/db';

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    
    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const user = await prisma.user.findUnique({
      where: { email: session.user.email },
      include: {
        businesses: {
          include: {
            aiAgents: {
              select: {
                id: true,
                name: true,
                role: true,
                provider: true,
                isActive: true,
              },
            },
          },
        },
      },
    });

    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    if (user.businesses.length === 0) {
      return NextResponse.json({ error: 'No business found' }, { status: 404 });
    }

    // For now, return the first business (we can add business selection later)
    const business = user.businesses[0];

    return NextResponse.json({ business });

  } catch (error) {
    console.error('Business profile fetch error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch business profile' },
      { status: 500 }
    );
  }
}
