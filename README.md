# 🧠 MindLens: AI-Powered Journaling & Mood Tracking

MindLens is an intelligent journaling application that uses AI to analyze your daily entries, track your mood over time, and provide personalized feedback to help you understand your emotional well-being.

## 🚀 Live Demo

[**View Live Demo**](https://mindlens-ten.vercel.app/)
*(Note: If your Vercel URL is different, please update this link!)*

## ✨ Features

- **AI Journal Analysis**: Get instant feedback on your journal entries with sentiment analysis and key insights.
- **Mood Tracking**: Visualize your mood history with interactive charts and graphs.
- **Secure Authentication**: User accounts and data protection powered by Clerk.
- **Glassmorphism UI**: A beautiful, modern "Deep Dark Mode" interface designed for focus and clarity.
- **Responsive Design**: Works seamlessly on desktop and mobile devices.

## 🛠️ Tech Stack

- **Framework**: [Next.js 15](https://nextjs.org/) (App Router)
- **Language**: [TypeScript](https://www.typescriptlang.org/)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **Database**: [PostgreSQL](https://www.postgresql.org/) (via [Neon](https://neon.tech/))
- **ORM**: [Prisma](https://www.prisma.io/)
- **Authentication**: [Clerk](https://clerk.com/)
- **AI Integration**: [OpenAI](https://openai.com/) / [OpenRouter](https://openrouter.ai/)

## 🚀 Getting Started

Follow these steps to set up the project locally.

### Prerequisites

- Node.js (v18 or higher)
- npm or yarn

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/keerthana-ar/mindlens.git
    cd mindlens
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Set up Environment Variables:**
    Create a `.env` file in the root directory and add the following keys:

    ```env
    DATABASE_URL="your_neon_postgres_url"
    NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="your_clerk_publishable_key"
    CLERK_SECRET_KEY="your_clerk_secret_key"
    OPENROUTER_API_KEY="your_openrouter_api_key"
    ```

4.  **Set up the Database:**
    Push the Prisma schema to your database:
    ```bash
    npx prisma db push
    ```

5.  **Run the application:**
    ```bash
    npm run dev
    ```

    Open [http://localhost:3000](http://localhost:3000) in your browser.

## 📦 Deployment

This project is optimized for deployment on [Vercel](https://vercel.com).

1.  Push your code to GitHub.
2.  Import the project in Vercel.
3.  Add the environment variables in the Vercel dashboard.
4.  Deploy!

> **Note:** The `postinstall` script in `package.json` automatically generates the Prisma client during deployment.

## 📄 License

This project is licensed under the MIT License.
