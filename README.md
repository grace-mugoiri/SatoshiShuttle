# RideShare Connect 🚗₿

A modern P2P carpooling platform with Bitcoin payment integration. Built with Flask (Python) backend and React frontend.

## 🌟 Features

- **User Authentication**: Secure registration and login system
- **Ride Management**: Create, search, and book rides
- **Bitcoin Payments**: Direct Bitcoin payments between users (Satoshis)
- **User Ratings**: Rate and review system for drivers and passengers  
- **Real-time Updates**: Live ride availability and booking updates
- **Responsive Design**: Mobile-friendly interface
- **Dashboard**: Comprehensive user dashboard for managing rides and bookings

## 🛠 Tech Stack

### Backend
- **Python Flask** - Web framework
- **SQLAlchemy** - Database ORM
- **Flask-JWT-Extended** - Authentication
- **Flask-CORS** - Cross-origin requests
- **PostgreSQL/SQLite** - Database

### Frontend
- **React 18** - UI framework
- **React Router** - Client-side routing
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **Axios** - HTTP client

### Bitcoin Integration
- **Bitcoin Core RPC** - Bitcoin node interaction
- **CoinGecko API** - Real-time Bitcoin pricing
- **Custom Bitcoin utilities** - Payment processing

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Bitcoin Core node (optional, for full Bitcoin integration)

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/rideshare-connect.git
cd rideshare-connect
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
python app.py
# Database tables will be created automatically
```

6. **Run the Flask app**
```bash
python app.py
# Server runs on http://localhost:5000
```

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend  # or create a new directory for React app
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure Tailwind CSS**
```bash
npx tailwindcss init -p
```

4. **Start the React app**
```bash
npm start
# App runs on http://localhost:3000
```

## 📁 Project Structure

```
satoshishuttle/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── utils/
│   └── bitcoin_utils.py  # Bitcoin integration utilities
├── frontend/
│   ├── src/
│   │   ├── App.js        # Main React component
│   │   ├── index.css     # Tailwind CSS
│   │   └── index.js      # React entry point
│   ├── package.json      # Node dependencies
│   └── tailwind.config.js # Tailwind configuration
└── README.md
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following:

```bash
SECRET_KEY=your-very-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///rideshare.db

# Bitcoin Configuration (optional)
BITCOIN_RPC_HOST=localhost
BITCOIN_RPC_PORT=8332
BITCOIN_RPC_USER=your-rpc-user
BITCOIN_RPC_PASSWORD=your-rpc-password

FLASK_ENV=development
```

### Database Configuration

For production, use PostgreSQL:
```bash
DATABASE_URL=postgresql://username:password@localhost/rideshare_db
```

## 💰 Bitcoin Integration

### Setup Bitcoin Core (Optional)

1. **Install Bitcoin Core**
   - Download from [bitcoin.org](https://bitcoin.org/en/download)

2. **Configure bitcoin.conf**
```conf
rpcuser=your-rpc-user
rpcpassword=your-rpc-password
rpcallowip=127.0.0.1
server=1
```

3. **Start Bitcoin Core**
```bash
bitcoind -daemon
```

### Bitcoin Features

- **Real-time pricing** from CoinGecko API
- **Automatic satoshi conversion**
- **Bitcoin address validation**
- **Transaction tracking**
- **Payment verification**

## 📱 API Endpoints

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login
- `GET /api/profile` - Get user profile

### Rides
- `GET /api/rides` - List available rides
- `POST /api/rides` - Create new ride
- `GET /api/my-rides` - Get user's offered rides

### Bookings
- `POST /api/bookings` - Book a ride
- `GET /api/my-bookings` - Get user's bookings

## 🎨 UI Components

- **Responsive Navigation** with mobile menu
- **Ride Cards** with Bitcoin pricing
- **Payment Method Selection** (Fiat/Bitcoin)
- **User Dashboard** with tabs
- **Authentication Forms** with validation
- **Status Badges** for ride/booking states

## 🔒 Security Features

- **JWT Authentication**
- **Password hashing** with Werkzeug
- **Input validation**
- **CORS configuration**
- **Secure Bitcoin address validation**

## 🚧 Future Enhancements

- [ ] **Lightning Network** integration for instant payments
- [ ] **Real-time chat** between users
- [ ] **GPS integration** for route tracking
- [ ] **Push notifications**
- [ ] **Multi-currency support**
- [ ] **Mobile app** (React Native)
- [ ] **Driver verification** system
- [ ] **Insurance integration**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Bitcoin Community** for the decentralized payment infrastructure
- **Flask & React Communities** for excellent documentation
- **CoinGecko** for Bitcoin price API
- **Tailwind CSS** for the amazing styling framework

## 📞 Support

For questions and support:
- Email: gracemugoiri@gmail.com
- Twitter: [@yourusername](hhttps://twitter.com/home)

---

**Built with ❤️ by Grace Mugoiri**

*Showcasing the power of Bitcoin for peer-to-peer payments in the sharing economy.*