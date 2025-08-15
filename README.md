# AI Stock Analysis Platform

A comprehensive AI-powered stock analysis and portfolio management platform built with Next.js, featuring real-time market data, intelligent recommendations, and advanced portfolio analytics.

## 🚀 Features

### **Core Functionality**
- **AI-Powered Stock Analysis**: Real-time stock analysis with buy/sell/hold recommendations
- **Portfolio Management**: Track multiple portfolios with performance analytics
- **Market Insights**: Sector analysis, market trends, and AI-generated insights
- **Watchlists**: Create and manage custom stock watchlists
- **Price Alerts**: Set intelligent price alerts with notifications
- **Reports & Analytics**: Generate comprehensive investment reports
- **Risk Assessment**: Portfolio risk analysis and diversification recommendations

### **Technical Features**
- **Authentication**: Secure Google OAuth integration
- **Real-time Data**: Live stock prices and market data
- **Responsive Design**: Mobile-first responsive UI
- **Dark Theme**: Modern dark theme with gradient backgrounds
- **Interactive Charts**: Advanced charting with technical indicators
- **Database Integration**: PostgreSQL with Prisma ORM

## 🛠️ Tech Stack

### **Frontend**
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **Recharts** - Interactive charts and data visualization
- **Lucide React** - Modern icon library
- **React Hot Toast** - Toast notifications

### **Backend**
- **Next.js API Routes** - Serverless API endpoints
- **NextAuth.js** - Authentication and session management
- **Prisma** - Database ORM and migrations
- **PostgreSQL** - Primary database

### **External APIs**
- **Yahoo Finance API** - Stock market data
- **Alpha Vantage** - Financial data and indicators
- **Google OAuth** - User authentication

## 📦 Installation

### Prerequisites
- Node.js 18+ 
- PostgreSQL database
- Google OAuth credentials

### 1. Clone the Repository
```bash
git clone <repository-url>
cd stock-analysis-platform
```

### 2. Install Dependencies
```bash
# Install frontend dependencies
cd frontend
npm install

# Install backend dependencies (if separate)
cd ../backend
npm install
```

### 3. Environment Setup
Create `.env.local` in the frontend directory:

```env
# Database
DATABASE_URL="postgresql://username:password@localhost:5432/stock_analysis"

# NextAuth
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your-nextauth-secret-key"

# Google OAuth
GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_CLIENT_SECRET="your-google-client-secret"

# API Keys
ALPHA_VANTAGE_API_KEY="your-alpha-vantage-key"
YAHOO_FINANCE_API_KEY="your-yahoo-finance-key"

# Notifications (Optional)
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USER="your-email@gmail.com"
SMTP_PASS="your-app-password"
```

### 4. Database Setup
```bash
cd frontend
npx prisma generate
npx prisma db push
```

### 5. Run the Application
```bash
# Development mode
npm run dev

# Production build
npm run build
npm start
```

The application will be available at `http://localhost:3000`

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── api/               # API routes
│   │   ├── dashboard/         # Dashboard page
│   │   ├── portfolio/         # Portfolio management
│   │   ├── insights/          # Market insights
│   │   ├── reports/           # Reports & analytics
│   │   ├── settings/          # User settings
│   │   └── analysis/[ticker]/ # Stock analysis
│   ├── components/            # Reusable components
│   │   ├── Navbar.tsx
│   │   ├── StockChart.tsx
│   │   ├── PortfolioChart.tsx
│   │   └── ...
│   ├── lib/                   # Utilities and configurations
│   │   ├── auth.ts           # NextAuth configuration
│   │   ├── prisma.ts         # Prisma client
│   │   └── utils.ts          # Helper functions
│   └── types/                 # TypeScript type definitions
├── prisma/
│   ├── schema.prisma         # Database schema
│   └── migrations/           # Database migrations
├── public/                   # Static assets
└── package.json
```

## 🔧 Configuration

### Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://localhost:3000/api/auth/callback/google` (development)
   - `https://yourdomain.com/api/auth/callback/google` (production)

### Database Configuration
The application uses PostgreSQL with Prisma ORM. The schema includes:
- User management and authentication
- Portfolio and position tracking
- Watchlists and price alerts
- Stock analysis data
- User preferences and settings

## 📊 API Endpoints

### Authentication
- `GET /api/auth/session` - Get current session
- `POST /api/auth/signin` - Sign in user
- `POST /api/auth/signout` - Sign out user

### Portfolio Management
- `GET /api/portfolio` - Get user portfolios
- `POST /api/portfolio` - Create new portfolio
- `PUT /api/portfolio/[id]` - Update portfolio
- `DELETE /api/portfolio/[id]` - Delete portfolio

### Stock Analysis
- `GET /api/stocks/[ticker]` - Get stock analysis
- `GET /api/stocks/search` - Search stocks
- `POST /api/stocks/analyze` - Analyze multiple stocks

### Watchlists
- `GET /api/watchlist` - Get user watchlists
- `POST /api/watchlist` - Create watchlist
- `PUT /api/watchlist/[id]` - Update watchlist
- `DELETE /api/watchlist/[id]` - Delete watchlist

## 🚀 Deployment

### Vercel (Recommended)
1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Docker
```bash
# Build Docker image
docker build -t stock-analysis-platform .

# Run container
docker run -p 3000:3000 stock-analysis-platform
```

### Manual Deployment
```bash
# Build for production
npm run build

# Start production server
npm start
```

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e
```

## 📈 Features in Detail

### Dashboard
- Real-time market overview
- Top gainers/losers
- Portfolio performance summary
- Recent analysis and alerts

### Portfolio Management
- Multiple portfolio support
- Position tracking with P&L
- Asset allocation charts
- Performance analytics
- Rebalancing recommendations

### Stock Analysis
- AI-powered buy/sell/hold signals
- Technical indicator analysis
- Fundamental data integration
- Price target predictions
- Risk assessment scores

### Market Insights
- Sector performance analysis
- Market trend identification
- Economic indicator tracking
- News sentiment analysis

### Reports & Analytics
- Portfolio performance reports
- Risk analysis reports
- Tax optimization reports
- Custom report generation

## 🔒 Security

- Secure authentication with NextAuth.js
- Environment variable protection
- API rate limiting
- Input validation and sanitization
- CSRF protection
- Secure session management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the FAQ section

## 🔮 Roadmap

- [ ] Mobile app development
- [ ] Advanced options trading analysis
- [ ] Social trading features
- [ ] Cryptocurrency integration
- [ ] Advanced backtesting
- [ ] Machine learning model improvements
- [ ] Real-time collaboration features

---

**Disclaimer**: This application is for educational and informational purposes only. It does not constitute financial advice. Always consult with qualified financial professionals before making investment decisions.

