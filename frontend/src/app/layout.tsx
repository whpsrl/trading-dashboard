import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Trading Dashboard - AI-Powered Trading Intelligence',
  description: 'Professional trading dashboard with real-time data and AI analysis',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body style={{ margin: 0, padding: 0 }}>
        {children}
      </body>
    </html>
  )
}
