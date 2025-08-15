const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🚀 Setting up AI Stock Analysis Platform...\n');

// Check if .env.local exists
const envPath = path.join(__dirname, '.env.local');
if (!fs.existsSync(envPath)) {
  console.log('📝 Creating .env.local file...');
  const envExample = fs.readFileSync(path.join(__dirname, '.env.example'), 'utf8');
  fs.writeFileSync(envPath, envExample);
  console.log('✅ .env.local created! Please update with your credentials.\n');
} else {
  console.log('✅ .env.local already exists.\n');
}

// Install dependencies
console.log('📦 Installing dependencies...');
try {
  execSync('npm install', { stdio: 'inherit' });
  console.log('✅ Dependencies installed!\n');
} catch (error) {
  console.error('❌ Failed to install dependencies:', error.message);
  process.exit(1);
}

// Generate Prisma client
console.log('🗄️  Generating Prisma client...');
try {
  execSync('npx prisma generate', { stdio: 'inherit' });
  console.log('✅ Prisma client generated!\n');
} catch (error) {
  console.error('❌ Failed to generate Prisma client:', error.message);
  console.log('ℹ️  You may need to set up your database first.\n');
}

console.log('🎉 Setup complete!');
console.log('\n📋 Next steps:');
console.log('1. Update .env.local with your database URL and OAuth credentials');
console.log('2. Set up your PostgreSQL database');
console.log('3. Run: npx prisma db push');
console.log('4. Run: npm run dev');
console.log('\n🔗 Visit: http://localhost:3000');