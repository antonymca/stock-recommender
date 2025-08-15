'use client'

import { useSession, signIn, signOut } from 'next-auth/react'
import Link from 'next/link'
import { useState } from 'react'
import { Menu, X, User, LogOut } from 'lucide-react'

export default function Navbar() {
  const { data: session, status } = useSession()
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex-shrink-0 flex items-center">
              <span className="text-xl font-bold text-gray-800">StockAnalysis</span>
            </Link>
          </div>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-8">
            <Link href="/dashboard" className="text-gray-700 hover:text-blue-600">
              Dashboard
            </Link>
            <Link href="/portfolio" className="text-gray-700 hover:text-blue-600">
              Portfolio
            </Link>
            <Link href="/insights" className="text-gray-700 hover:text-blue-600">
              Insights
            </Link>
            
            {status === 'loading' ? (
              <div className="animate-pulse bg-gray-200 h-8 w-20 rounded"></div>
            ) : session ? (
              <div className="flex items-center space-x-4">
                <span className="text-gray-700">Hi, {session.user?.name}</span>
                <button
                  onClick={() => signOut()}
                  className="flex items-center space-x-1 text-gray-700 hover:text-red-600"
                >
                  <LogOut size={16} />
                  <span>Sign Out</span>
                </button>
              </div>
            ) : (
              <button
                onClick={() => signIn()}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                Sign In
              </button>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-gray-700 hover:text-blue-600"
            >
              {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
              <Link href="/dashboard" className="block px-3 py-2 text-gray-700 hover:text-blue-600">
                Dashboard
              </Link>
              <Link href="/portfolio" className="block px-3 py-2 text-gray-700 hover:text-blue-600">
                Portfolio
              </Link>
              <Link href="/insights" className="block px-3 py-2 text-gray-700 hover:text-blue-600">
                Insights
              </Link>
              
              {session ? (
                <div className="px-3 py-2">
                  <p className="text-gray-700 mb-2">Hi, {session.user?.name}</p>
                  <button
                    onClick={() => signOut()}
                    className="text-red-600 hover:text-red-700"
                  >
                    Sign Out
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => signIn()}
                  className="block w-full text-left px-3 py-2 text-blue-600 hover:text-blue-700"
                >
                  Sign In
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
