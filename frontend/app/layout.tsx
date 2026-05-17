import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AgentForge - AI Agent Generator",
  description: "Type one sentence. Get a deployed watsonx Orchestrate agent in 90 seconds.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}

// Made with Bob
