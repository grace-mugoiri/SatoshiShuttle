import React, { useState, useEffect } from 'react';
import { Car, Bitcoin, User, Calendar, MapPin, Star, Menu, X } from 'lucide-react';

// API Base URL - use environment variable or fallback to localhost for development
const API_BASE = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5001/api';

// Utility functions
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString();
};

const formatBitcoin = (satoshis) => {
  return (satoshis / 100000000).toFixed(8) + ' BTC';
};

// Auth Hook
const useAuth = () => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);

  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
      setToken(savedToken);
      // Verify token and get user info
      fetch(`${API_BASE}/profile`, {
        headers: { 'Authorization': `Bearer ${savedToken}` }
      })
        .then(res => res.json())
        .then(data => {
          if (data.id) {
            setUser(data);
          } else {
            logout();
          }
        })
        .catch(() => logout());
    }
  }, []);

  const login = async (username, password) => {
    try {
      const response = await fetch(`${API_BASE}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await response.json();

      if (data.access_token) {
        localStorage.setItem('token', data.access_token);
        setToken(data.access_token);
        setUser(data.user);
        return { success: true };
      } else {
        return { success: false, message: data.message };
      }
    } catch (error) {
      return { success: false, message: 'Login failed' };
    }
  };

  const register = async (userData) => {
    try {
      console.log('Registration attempt with data:', userData);
      console.log('API endpoint:', `${API_BASE}/register`);

      const response = await fetch(`${API_BASE}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
      });

      console.log('Response status:', response.status);
      const data = await response.json();
      console.log('Response data:', data);

      if (response.ok) {
        return { success: true, message: data.message };
      } else {
        return { success: false, message: data.message };
      }
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, message: 'Registration failed: ' + error.message };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  return { user, token, login, register, logout, isAuthenticated: !!user };
};

// Navigation Component
const Navbar = ({ auth, currentPage, setCurrentPage }) => {
  const [isOpen, setIsOpen] = useState(false);

  const navigate = (page) => {
    setCurrentPage(page);
    setIsOpen(false);
  };

  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          <button onClick={() => navigate('home')} className="flex items-center space-x-2 text-xl font-bold">
            <Car className="h-8 w-8" />
            <span>RideShare Connect</span>
          </button>

          <div className="hidden md:flex items-center space-x-6">
            <button onClick={() => navigate('rides')} className="hover:text-blue-200">Find Rides</button>
            {auth.isAuthenticated ? (
              <>
                <button onClick={() => navigate('dashboard')} className="hover:text-blue-200">Dashboard</button>
                <button onClick={() => navigate('create-ride')} className="hover:text-blue-200">Offer Ride</button>
                <button onClick={auth.logout} className="bg-blue-700 px-4 py-2 rounded hover:bg-blue-800">
                  Logout
                </button>
              </>
            ) : (
              <>
                <button onClick={() => navigate('login')} className="hover:text-blue-200">Login</button>
                <button onClick={() => navigate('register')} className="bg-blue-700 px-4 py-2 rounded hover:bg-blue-800">
                  Sign Up
                </button>
              </>
            )}
          </div>

          <button
            className="md:hidden"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>

        {isOpen && (
          <div className="md:hidden py-4 border-t border-blue-700">
            <div className="flex flex-col space-y-2">
              <button onClick={() => navigate('rides')} className="hover:text-blue-200 py-2 text-left">Find Rides</button>
              {auth.isAuthenticated ? (
                <>
                  <button onClick={() => navigate('dashboard')} className="hover:text-blue-200 py-2 text-left">Dashboard</button>
                  <button onClick={() => navigate('create-ride')} className="hover:text-blue-200 py-2 text-left">Offer Ride</button>
                  <button onClick={auth.logout} className="bg-blue-700 px-4 py-2 rounded hover:bg-blue-800 text-left">
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <button onClick={() => navigate('login')} className="hover:text-blue-200 py-2 text-left">Login</button>
                  <button onClick={() => navigate('register')} className="hover:text-blue-200 py-2 text-left">Sign Up</button>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

// Home Component
const Home = ({ setCurrentPage }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Share Rides, Pay with Bitcoin
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            The future of carpooling is here. Connect with fellow travelers and pay securely with Bitcoin.
            No banks, no fees, just peer-to-peer transportation.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => setCurrentPage('rides')}
              className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Find a Ride
            </button>
            <button
              onClick={() => setCurrentPage('create-ride')}
              className="bg-orange-500 text-white px-8 py-3 rounded-lg font-semibold hover:bg-orange-600 transition-colors"
            >
              Offer a Ride
            </button>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white p-6 rounded-lg shadow-md text-center">
            <Bitcoin className="h-12 w-12 text-orange-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">Bitcoin Payments</h3>
            <p className="text-gray-600">Pay directly with Bitcoin. Fast, secure, and decentralized payments.</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md text-center">
            <Car className="h-12 w-12 text-blue-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">Easy Carpooling</h3>
            <p className="text-gray-600">Find rides or offer seats in your car. Connect with your community.</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md text-center">
            <Star className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">Trusted Community</h3>
            <p className="text-gray-600">Rate and review your ride partners. Build trust in the community.</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-8">
          <h2 className="text-3xl font-bold text-center mb-8">Why Bitcoin for Ridesharing?</h2>
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-xl font-semibold mb-4">Instant Payments</h3>
              <p className="text-gray-600 mb-4">
                No waiting for bank transfers or payment processing. Bitcoin transactions are confirmed in minutes.
              </p>
              <h3 className="text-xl font-semibold mb-4">Global Accessibility</h3>
              <p className="text-gray-600">
                Anyone with a Bitcoin wallet can participate, regardless of their banking status or location.
              </p>
            </div>
            <div>
              <h3 className="text-xl font-semibold mb-4">Lower Fees</h3>
              <p className="text-gray-600 mb-4">
                Eliminate payment processor fees. Bitcoin transactions cost just a few cents.
              </p>
              <h3 className="text-xl font-semibold mb-4">Privacy & Security</h3>
              <p className="text-gray-600">
                Your payment information stays private. No need to share credit card details.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Login Component
const Login = ({ auth, setCurrentPage }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await auth.login(username, password);
    if (result.success) {
      setCurrentPage('dashboard');
    } else {
      setError(result.message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm space-y-4">
            <input
              type="text"
              required
              className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <input
              type="password"
              required
              className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {error && (
            <div className="text-red-600 text-sm text-center">{error}</div>
          )}

          <button
            type="submit"
            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none"
          >
            Sign in
          </button>

          <div className="text-center">
            <button
              type="button"
              onClick={() => setCurrentPage('register')}
              className="text-indigo-600 hover:text-indigo-500"
            >
              Don't have an account? Sign up
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Register Component
const Register = ({ auth, setCurrentPage }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    phone: '',
    bitcoin_address: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await auth.register(formData);
    if (result.success) {
      setSuccess(result.message);
      setError('');
      setTimeout(() => setCurrentPage('login'), 2000);
    } else {
      setError(result.message);
      setSuccess('');
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
      <div className="max-w-md w-full space-y-8">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Create your account
        </h2>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <input
              type="text"
              name="username"
              required
              className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Username"
              value={formData.username}
              onChange={handleChange}
            />
            <input
              type="email"
              name="email"
              required
              className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Email address"
              value={formData.email}
              onChange={handleChange}
            />
            <input
              type="password"
              name="password"
              required
              className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Password"
              value={formData.password}
              onChange={handleChange}
            />
            <input
              type="tel"
              name="phone"
              className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Phone number (optional)"
              value={formData.phone}
              onChange={handleChange}
            />
            <input
              type="text"
              name="bitcoin_address"
              className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Bitcoin address (optional)"
              value={formData.bitcoin_address}
              onChange={handleChange}
            />
            <p className="text-sm text-gray-500">
              💡 Add your Bitcoin address to receive payments when offering rides
            </p>
          </div>

          {error && (
            <div className="text-red-600 text-sm text-center">{error}</div>
          )}
          {success && (
            <div className="text-green-600 text-sm text-center">{success}</div>
          )}

          <button
            type="submit"
            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
          >
            Sign up
          </button>

          <div className="text-center">
            <button
              type="button"
              onClick={() => setCurrentPage('login')}
              className="text-indigo-600 hover:text-indigo-500"
            >
              Already have an account? Sign in
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Rides List Component
const RidesList = ({ auth, setCurrentPage }) => {
  const [rides, setRides] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRides();
  }, []);

  const fetchRides = async () => {
    try {
      const response = await fetch(`${API_BASE}/rides`);
      const data = await response.json();
      setRides(data);
    } catch (error) {
      console.error('Error fetching rides:', error);
    } finally {
      setLoading(false);
    }
  };

  const [showBitcoinPayment, setShowBitcoinPayment] = useState(false);
  const [paymentDetails, setPaymentDetails] = useState(null);

  const handleBookRide = async (rideId, paymentMethod) => {
    if (!auth.isAuthenticated) {
      alert('Please login to book a ride');
      setCurrentPage('login');
      return;
    }

    const seats = parseInt(prompt('How many seats would you like to book?', '1'));
    if (!seats || seats < 1) return;

    try {
      const response = await fetch(`${API_BASE}/bookings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${auth.token}`
        },
        body: JSON.stringify({
          ride_id: rideId,
          seats_booked: seats,
          payment_method: paymentMethod
        })
      });

      const data = await response.json();
      if (response.ok) {
        if (paymentMethod === 'bitcoin') {
          // Show Bitcoin payment modal
          const testnetAddress = prompt('Enter your Bitcoin TESTNET address to receive payment:', 'tb1q...');
          if (testnetAddress) {
            await createBitcoinPayment(data.booking_id, testnetAddress, data.total_amount);
          }
        } else {
          alert(`Booking successful! Total: $${data.total_amount}`);
          fetchRides();
        }
      } else {
        alert(data.message);
      }
    } catch (error) {
      alert('Booking failed');
    }
  };

  const createBitcoinPayment = async (bookingId, testnetAddress, totalAmount) => {
    try {
      const response = await fetch(`${API_BASE}/bitcoin/create-payment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${auth.token}`
        },
        body: JSON.stringify({
          booking_id: bookingId,
          testnet_address: testnetAddress
        })
      });

      const data = await response.json();
      if (response.ok) {
        setPaymentDetails(data);
        setShowBitcoinPayment(true);
      } else {
        alert('Failed to create payment');
      }
    } catch (error) {
      alert('Payment creation failed');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">Loading rides...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Available Rides</h1>

        {rides.length === 0 ? (
          <div className="text-center py-12">
            <Car className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl text-gray-500 mb-4">No rides available</h3>
            <button
              onClick={() => setCurrentPage('create-ride')}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
            >
              Offer the first ride
            </button>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {rides.map(ride => (
              <div key={ride.id} className="bg-white rounded-lg shadow-md p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="font-semibold text-lg">{ride.origin} → {ride.destination}</h3>
                    <div className="flex items-center text-gray-600 mt-2">
                      <User className="h-4 w-4 mr-1" />
                      <span>{ride.driver}</span>
                      <div className="flex items-center ml-4">
                        <Star className="h-4 w-4 text-yellow-400 mr-1" />
                        <span>{ride.driver_rating.toFixed(1)}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center text-gray-600">
                    <Calendar className="h-4 w-4 mr-2" />
                    <span>{formatDate(ride.departure_time)}</span>
                  </div>
                  <div className="flex items-center text-gray-600">
                    <User className="h-4 w-4 mr-2" />
                    <span>{ride.available_seats} seats available</span>
                  </div>
                </div>

                {ride.description && (
                  <div className="mb-4">
                    <p className="text-gray-600 text-sm">{ride.description}</p>
                  </div>
                )}

                <div className="flex justify-between items-center mb-4">
                  <div>
                    <div className="text-lg font-semibold">${ride.price_fiat}</div>
                    <div className="text-sm text-orange-600 flex items-center">
                      <Bitcoin className="h-4 w-4 mr-1" />
                      {formatBitcoin(ride.price_bitcoin)}
                    </div>
                  </div>
                </div>

                <div className="flex space-x-2">
                  <button
                    onClick={() => handleBookRide(ride.id, 'fiat')}
                    className="flex-1 bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition-colors"
                  >
                    Book ($)
                  </button>
                  <button
                    onClick={() => handleBookRide(ride.id, 'bitcoin')}
                    className="flex-1 bg-orange-500 text-white py-2 px-4 rounded hover:bg-orange-600 transition-colors flex items-center justify-center"
                  >
                    <Bitcoin className="h-4 w-4 mr-1" />
                    Book
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Bitcoin Payment Modal */}
        {showBitcoinPayment && paymentDetails && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-md w-full p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold">Bitcoin Payment</h3>
                <button onClick={() => setShowBitcoinPayment(false)} className="text-gray-500 hover:text-gray-700">
                  <X className="h-6 w-6" />
                </button>
              </div>

              <div className="text-center mb-4">
                <p className="text-gray-600 mb-2">Send Bitcoin Testnet to:</p>
                <div className="bg-gray-100 p-3 rounded break-all text-sm font-mono mb-4">
                  {paymentDetails.payment_address}
                </div>

                <div className="mb-4">
                  <p className="text-2xl font-bold text-orange-600">
                    {paymentDetails.amount_btc.toFixed(8)} BTC
                  </p>
                  <p className="text-sm text-gray-500">
                    ({paymentDetails.amount_satoshis} satoshis)
                  </p>
                </div>

                {/* QR Code */}
                <div className="bg-white p-4 border-2 border-gray-200 rounded inline-block mb-4">
                  <img
                    src={`data:image/png;base64,${paymentDetails.qr_code}`}
                    alt="Payment QR Code"
                    className="w-48 h-48"
                  />
                </div>

                <div className="bg-blue-50 p-3 rounded mb-4">
                  <p className="text-sm text-blue-800">
                    <strong>Get Testnet Bitcoin:</strong><br/>
                    Visit a testnet faucet to get free test coins
                  </p>
                  <a
                    href="https://testnet-faucet.mempool.co/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline text-sm"
                  >
                    Mempool Testnet Faucet →
                  </a>
                </div>

                <button
                  onClick={() => setShowBitcoinPayment(false)}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Create Ride Component
const CreateRide = ({ auth, setCurrentPage }) => {
  const [formData, setFormData] = useState({
    origin: '',
    destination: '',
    departure_time: '',
    available_seats: 1,
    price_fiat: '',
    price_bitcoin: '',
    description: ''
  });
  const [btcPrice, setBtcPrice] = useState(45000);

  useEffect(() => {
    fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd')
      .then(res => res.json())
      .then(data => setBtcPrice(data.bitcoin.usd))
      .catch(() => setBtcPrice(45000));
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => {
      const updated = { ...prev, [name]: value };

      if (name === 'price_fiat' && value) {
        const btcAmount = parseFloat(value) / btcPrice;
        updated.price_bitcoin = Math.round(btcAmount * 100000000);
      }

      return updated;
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!auth.isAuthenticated) {
      alert('Please login to create a ride');
      setCurrentPage('login');
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/rides`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${auth.token}`
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();
      if (response.ok) {
        alert('Ride created successfully!');
        setFormData({
          origin: '',
          destination: '',
          departure_time: '',
          available_seats: 1,
          price_fiat: '',
          price_bitcoin: '',
          description: ''
        });
        setCurrentPage('dashboard');
      } else {
        alert(data.message);
      }
    } catch (error) {
      alert('Failed to create ride');
    }
  };

  if (!auth.isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-xl mb-4">Please login to create a ride</p>
          <button
            onClick={() => setCurrentPage('login')}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-2xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Offer a Ride</h1>

        <div className="bg-white rounded-lg shadow-md p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">From</label>
                <input
                  type="text"
                  name="origin"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Starting location"
                  value={formData.origin}
                  onChange={handleChange}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">To</label>
                <input
                  type="text"
                  name="destination"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Destination"
                  value={formData.destination}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Departure Time</label>
                <input
                  type="datetime-local"
                  name="departure_time"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={formData.departure_time}
                  onChange={handleChange}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Available Seats</label>
                <select
                  name="available_seats"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={formData.available_seats}
                  onChange={handleChange}
                >
                  {[1, 2, 3, 4, 5, 6].map(num => (
                    <option key={num} value={num}>{num}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Price per Seat (USD)</label>
                <input
                  type="number"
                  name="price_fiat"
                  step="0.01"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.00"
                  value={formData.price_fiat}
                  onChange={handleChange}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Price in Bitcoin (Satoshis)</label>
                <input
                  type="number"
                  name="price_bitcoin"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Auto-calculated"
                  value={formData.price_bitcoin}
                  onChange={handleChange}
                />
                {formData.price_bitcoin && (
                  <p className="text-sm text-gray-500 mt-1">
                    ≈ {formatBitcoin(formData.price_bitcoin)}
                  </p>
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Additional Information</label>
              <textarea
                name="description"
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Any additional details about your ride..."
                value={formData.description}
                onChange={handleChange}
              />
            </div>

            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 transition-colors font-semibold"
            >
              Create Ride
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

// Dashboard Component
const Dashboard = ({ auth, setCurrentPage }) => {
  const [myRides, setMyRides] = useState([]);
  const [myBookings, setMyBookings] = useState([]);
  const [activeTab, setActiveTab] = useState('rides');

  useEffect(() => {
    if (auth.isAuthenticated) {
      fetchMyRides();
      fetchMyBookings();
    }
  }, [auth.isAuthenticated]);

  const fetchMyRides = async () => {
    try {
      const response = await fetch(`${API_BASE}/my-rides`, {
        headers: { 'Authorization': `Bearer ${auth.token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setMyRides(Array.isArray(data) ? data : []);
      } else {
        setMyRides([]);
      }
    } catch (error) {
      console.error('Error fetching rides:', error);
      setMyRides([]);
    }
  };

  const fetchMyBookings = async () => {
    try {
      const response = await fetch(`${API_BASE}/my-bookings`, {
        headers: { 'Authorization': `Bearer ${auth.token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setMyBookings(Array.isArray(data) ? data : []);
      } else {
        setMyBookings([]);
      }
    } catch (error) {
      console.error('Error fetching bookings:', error);
      setMyBookings([]);
    }
  };

  if (!auth.isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-xl mb-4">Please login to view your dashboard</p>
          <button
            onClick={() => setCurrentPage('login')}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Dashboard</h1>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-4">
              <div className="bg-blue-100 p-3 rounded-full">
                <User className="h-8 w-8 text-blue-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">{auth.user.username}</h2>
                <p className="text-gray-600">{auth.user.email}</p>
                <div className="flex items-center mt-2">
                  <Star className="h-4 w-4 text-yellow-400 mr-1" />
                  <span className="text-sm">{auth.user.rating.toFixed(1)} rating</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('rides')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${activeTab === 'rides'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
              >
                My Rides ({myRides.length})
              </button>
              <button
                onClick={() => setActiveTab('bookings')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${activeTab === 'bookings'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
              >
                My Bookings ({myBookings.length})
              </button>
            </nav>
          </div>
        </div>

        {activeTab === 'rides' && (
          <div className="space-y-6">
            {myRides.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-lg">
                <Car className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl text-gray-500 mb-4">No rides offered yet</h3>
                <button
                  onClick={() => setCurrentPage('create-ride')}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
                >
                  Offer a ride
                </button>
              </div>
            ) : (
              myRides.map(ride => (
                <div key={ride.id} className="bg-white rounded-lg shadow p-6">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-lg font-semibold">{ride.origin} → {ride.destination}</h3>
                      <p className="text-gray-600">{formatDate(ride.departure_time)}</p>
                      <p className="text-sm text-gray-500 mt-2">
                        {ride.available_seats} seats • ${ride.price_fiat}
                      </p>
                      <p className="text-sm text-gray-500">
                        {formatBitcoin(ride.price_bitcoin)}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${ride.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                        {ride.status}
                      </span>
                      <p className="text-sm text-gray-500 mt-2">{ride.bookings_count} bookings</p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'bookings' && (
          <div className="space-y-6">
            {myBookings.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-lg">
                <MapPin className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl text-gray-500 mb-4">No bookings yet</h3>
                <button
                  onClick={() => setCurrentPage('rides')}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
                >
                  Find a ride
                </button>
              </div>
            ) : (
              myBookings.map(booking => (
                <div key={booking.id} className="bg-white rounded-lg shadow p-6">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-lg font-semibold">
                        {booking.ride.origin} → {booking.ride.destination}
                      </h3>
                      <p className="text-gray-600">Driver: {booking.ride.driver}</p>
                      <p className="text-gray-600">{formatDate(booking.ride.departure_time)}</p>
                      <p className="text-sm text-gray-500 mt-2">
                        {booking.seats_booked} seat{booking.seats_booked > 1 ? 's' : ''}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center mb-2">
                        {booking.payment_method === 'bitcoin' ? (
                          <Bitcoin className="h-4 w-4 text-orange-500 mr-1" />
                        ) : (
                          <span className="text-green-600 mr-1">$</span>
                        )}
                        <span className="font-semibold">
                          {booking.payment_method === 'bitcoin'
                            ? formatBitcoin(booking.total_amount_bitcoin)
                            : ' + booking.total_amount_fiat'
                          }
                        </span>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${booking.payment_status === 'confirmed'
                        ? 'bg-green-100 text-green-800'
                        : booking.payment_status === 'pending'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                        }`}>
                        {booking.payment_status}
                      </span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// Main App Component
const App = () => {
  const auth = useAuth();
  const [currentPage, setCurrentPage] = useState('home');

  useEffect(() => {
    if (auth.isAuthenticated && currentPage === 'login') {
      setCurrentPage('dashboard');
    }
  }, [auth.isAuthenticated]);

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <Home setCurrentPage={setCurrentPage} />;
      case 'login':
        return <Login auth={auth} setCurrentPage={setCurrentPage} />;
      case 'register':
        return <Register auth={auth} setCurrentPage={setCurrentPage} />;
      case 'rides':
        return <RidesList auth={auth} setCurrentPage={setCurrentPage} />;
      case 'create-ride':
        return <CreateRide auth={auth} setCurrentPage={setCurrentPage} />;
      case 'dashboard':
        return <Dashboard auth={auth} setCurrentPage={setCurrentPage} />;
      default:
        return <Home setCurrentPage={setCurrentPage} />;
    }
  };

  return (
    <div className="App">
      <Navbar auth={auth} currentPage={currentPage} setCurrentPage={setCurrentPage} />
      {renderPage()}
    </div>
  );
};

export default App;