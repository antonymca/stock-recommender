import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '../../../../lib/auth'
import { prisma } from '../../../../lib/prisma'

export async function GET() {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const portfolios = await prisma.portfolio.findMany({
      where: { userId: session.user.id },
      include: {
        positions: true
      }
    })

    return NextResponse.json(portfolios)
  } catch (error) {
    console.error('Error fetching portfolios:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { name } = await request.json()

    const portfolio = await prisma.portfolio.create({
      data: {
        name,
        userId: session.user.id
      }
    })

    return NextResponse.json(portfolio)
  } catch (error) {
    console.error('Error creating portfolio:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}