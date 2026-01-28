import { PrismaClient } from '@prisma/client';

const prismaClientSingleton = () => {
    // NUCLEAR FIX: Hardcoded URL. No Env Var dependency.
    const url = "postgresql://neondb_owner:npg_DQGx25YyNiWz@ep-wispy-band-ahcjkbi5-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require";

    console.log("Initializing Prisma Client with URL length:", url?.length);

    return new PrismaClient({
        log: ['query', 'error', 'warn'],
        datasources: {
            db: {
                url: url
            }
        }
    });
};

const globalForPrisma = global as unknown as { prisma: ReturnType<typeof prismaClientSingleton> };

export const prisma = globalForPrisma.prisma || prismaClientSingleton();

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;
