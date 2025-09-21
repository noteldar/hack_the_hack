'use client'

import { useState, useEffect } from 'react'
import { ThemeProvider } from 'next-themes'
import { Toaster } from '@/components/ui/sonner'
import { Header } from './header'
import { Sidebar } from './sidebar'

interface MainLayoutProps {
  children: React.ReactNode
}

export function MainLayout({ children }: MainLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return null
  }

  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <div className="min-h-screen gradient-bg">
        <div className="flex h-screen overflow-hidden">
          {/* Sidebar */}
          <div className="hidden lg:flex lg:flex-shrink-0">
            <div className="flex flex-col w-80">
              <Sidebar isOpen={true} setIsOpen={setSidebarOpen} />
            </div>
          </div>

          {/* Mobile sidebar */}
          <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />

          {/* Main content */}
          <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
            <Header onMenuClick={() => setSidebarOpen(true)} />

            {/* Page content */}
            <main className="flex-1 relative overflow-y-auto focus:outline-none">
              <div className="py-6">
                <div className="px-6 max-w-7xl mx-auto">
                  {children}
                </div>
              </div>
            </main>
          </div>
        </div>

        <Toaster />
      </div>
    </ThemeProvider>
  )
}