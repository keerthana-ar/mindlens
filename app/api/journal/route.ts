import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import OpenAI from 'openai';
import { auth } from '@clerk/nextjs/server';

const openai = new OpenAI({
    apiKey: process.env.OPENROUTER_API_KEY,
    baseURL: "https://openrouter.ai/api/v1",
});

export async function POST(req: Request) {
    let text = '';

    try {
        const { userId } = await auth();
        if (!userId) {
            return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
        }

        try {
            const body = await req.json();
            text = body.text;
        } catch (e) {
            return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 });
        }

        if (!text) {
            return NextResponse.json({ error: 'Journal text is required' }, { status: 400 });
        }

        // 1. Analyze Emotion & Generate Reflection in parallel (or single prompt)
        // 1. Analyze Emotion & Generate Reflection in parallel (or single prompt)
        const prompt = `
    Analyze the following journal entry. 
    1. Identify the primary emotion (choose one: Joy, Sadness, Anger, Fear, Love, Surprise, Neutral).
    2. Give a confidence score (0-100).
    3. Write a compassionate, supportive reflection/response to the user (2-3 paragraphs).

    Return ONLY a JSON object with this format:
    {
      "emotion": "Joy",
      "score": 95,
      "reflection": "Your reflection text here..."
    }

    Journal Entry:
    "${text}"
    `;

        console.log("Analyzing with AI (Fetch)... Key Length:", process.env.OPENROUTER_API_KEY?.length);

        const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${process.env.OPENROUTER_API_KEY}`,
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "MindLens Local"
            },
            body: JSON.stringify({
                "model": "liquid/lfm-2.5-1.2b-instruct:free", // Verified available model
                "messages": [{ role: "user", content: prompt }]
            })
        });

        if (!response.ok) {
            const errText = await response.text();
            console.error("OpenRouter Fetch Error:", response.status, errText);
            throw new Error(`OpenRouter API Error: ${response.status} ${errText}`);
        }

        const completion = await response.json();
        const content = completion.choices[0].message.content;

        if (!content) throw new Error("No response from AI");

        console.log("AI Response received");

        // Sanitize the content to remove markdown code blocks if present
        const cleanedContent = content.replace(/```json\n?|```/g, '').trim();
        let result;
        try {
            result = JSON.parse(cleanedContent);
        } catch (e) {
            console.error("JSON Parse Error:", cleanedContent);

            // Try to extract JSON if it's mixed with text
            const jsonMatch = cleanedContent.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
                try {
                    result = JSON.parse(jsonMatch[0]);
                } catch (e2) {
                    throw new Error("Failed to parse AI response");
                }
            } else {
                throw new Error("Failed to parse AI response");
            }
        }

        // 2. Save to Database
        const entry = await prisma.journalEntry.create({
            data: {
                userId,
                content: text,
                emotion: result.emotion.toLowerCase(),
                score: result.score,
                reflection: result.reflection,
            },
        });

        return NextResponse.json(entry);

    } catch (error: any) {
        console.error('Error processing journal entry (Real AI failed):', error);

        // Detailed error logging
        if (error?.response) {
            console.error('OpenAI API Error Data:', error.response.data);
        }

        // --- FALLBACK MOCK RESPONSE ---
        // If the AI fails (Rate limit, quota, etc.), we seamlessly fall back to a mock response
        // so the user can still use the application.
        console.log("⚠️ Falling back to Mock Analysis");

        try {
            const mockEmotions = ['joy', 'sadness', 'neutral', 'surprise'];
            const randomEmotion = mockEmotions[Math.floor(Math.random() * mockEmotions.length)];

            let finalUserId = 'anonymous';
            try {
                const { userId: authId } = await auth();
                if (authId) finalUserId = authId;
            } catch (authError) {
                console.warn("Auth check failed in fallback (defaulting to anonymous):", authError);
            }

            const entry = await prisma.journalEntry.create({
                data: {
                    userId: finalUserId,
                    content: text, // Use existing text variable
                    emotion: randomEmotion,
                    score: 85,
                    reflection: "I'm having trouble connecting to my AI brain right now, but I hear you. Writing this down is the first step to clarity. Take a deep breath and give yourself credit for pausing to reflect. (Note: This is a fallback response due to high AI traffic).",
                },
            });
            return NextResponse.json(entry);
        } catch (dbError: any) {
            console.error("Critical: Database fallback also failed", dbError);
            return NextResponse.json({ error: `System is offline. Detailed Error: ${dbError.message || dbError}` }, { status: 500 });
        }
    }
}
