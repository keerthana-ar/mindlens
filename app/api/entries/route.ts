import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { auth } from '@clerk/nextjs/server';

export async function GET() {
    try {
        const { userId } = await auth();
        if (!userId) {
            return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
        }

        const entries = await prisma.journalEntry.findMany({
            where: {
                userId: userId,
            },
            orderBy: { createdAt: 'desc' },
            take: 50,
        });
        return NextResponse.json(entries);
    } catch (error) {
        return NextResponse.json({ error: 'Failed to fetch entries' }, { status: 500 });
    }
}
