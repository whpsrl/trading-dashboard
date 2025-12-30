'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

export default function Navbar() {
  const pathname = usePathname()

  const links = [
    { href: '/', label: 'Home' },
    { href: '/crypto', label: 'Crypto' },
    { href: '/results', label: 'Results' },
    { href: '/diagnostics', label: 'Diagnostics' },
    { href: '/indices', label: 'Indices' },
    { href: '/stocks', label: 'Stocks' },
    { href: '/commodities', label: 'Commodities' },
    { href: '/forex', label: 'Forex' },
  ]

  return (
    <nav style={{
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '1rem 0',
      boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
      marginBottom: '2rem'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        display: 'flex',
        gap: '2rem',
        alignItems: 'center',
        padding: '0 2rem'
      }}>
        <div style={{
          fontSize: '1.5rem',
          fontWeight: 'bold',
          color: 'white',
          marginRight: 'auto'
        }}>
          🤖 AI Trading Bot
        </div>

        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            style={{
              color: pathname === link.href ? '#fbbf24' : 'white',
              textDecoration: 'none',
              fontSize: '1rem',
              fontWeight: pathname === link.href ? 'bold' : '600',
              transition: 'color 0.2s',
              padding: '0.5rem 1rem',
              borderRadius: '8px',
              background: pathname === link.href ? 'rgba(255,255,255,0.2)' : 'transparent'
            }}
          >
            {link.label}
          </Link>
        ))}
      </div>
    </nav>
  )
}

