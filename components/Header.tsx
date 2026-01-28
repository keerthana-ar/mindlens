import Link from 'next/link';
import { UserButton, SignInButton, SignedIn, SignedOut } from '@clerk/nextjs';

export function Header() {
    return (
        <header className="sticky top-0 z-50 border-b border-white/5 bg-zinc-950/80 backdrop-blur-xl">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                <Link href="/" className="group flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-indigo-500/20 flex items-center justify-center group-hover:bg-indigo-500/30 transition-colors">
                        <span className="text-xl">✦</span>
                    </div>
                    <span className="font-serif text-xl font-bold tracking-tight text-zinc-100 group-hover:text-indigo-400 transition-colors">
                        MindLens
                    </span>
                </Link>

                <nav className="flex items-center gap-6">
                    <Link
                        href="/"
                        className="text-sm font-medium text-zinc-400 hover:text-zinc-100 transition-colors"
                    >
                        Write
                    </Link>
                    <Link
                        href="/history"
                        className="text-sm font-medium text-zinc-400 hover:text-zinc-100 transition-colors"
                    >
                        History
                    </Link>
                    <Link
                        href="/dashboard"
                        className="text-sm font-medium text-zinc-400 hover:text-zinc-100 transition-colors"
                    >
                        Analytics
                    </Link>

                    <div className="pl-4 border-l border-white/10">
                        <SignedIn>
                            <UserButton
                                appearance={{
                                    elements: {
                                        avatarBox: "w-8 h-8 ring-2 ring-white/10 hover:ring-indigo-500/50 transition-all"
                                    }
                                }}
                            />
                        </SignedIn>
                        <SignedOut>
                            <SignInButton mode="modal">
                                <button className="text-sm font-medium text-indigo-400 hover:text-indigo-300 transition-colors">
                                    Sign In
                                </button>
                            </SignInButton>
                        </SignedOut>
                    </div>
                </nav>
            </div>
        </header>
    );
}
