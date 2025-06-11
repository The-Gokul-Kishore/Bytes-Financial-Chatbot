import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

interface User {
  username: string;
  email: string;
  user_id: number;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  signup: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Use the proxy URL instead of direct backend URL
const API_URL = '/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  // Update axios headers whenever token changes
  useEffect(() => {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete api.defaults.headers.common['Authorization'];
    }
  }, [token]);

  // Verify token on mount and when token changes
  useEffect(() => {
    const verifyToken = async () => {
      if (!token) {
        setIsAuthenticated(false);
        setUser(null);
        return;
      }

      try {
        console.log('Verifying token:', token);
        const response = await api.get('/verify-token');
        console.log('Token verification response:', response.data);
        
        if (response.data.valid) {
          setIsAuthenticated(true);
          setUser({
            username: response.data.username,
            email: '', 
            user_id: 0, 
          });
        } else {
          console.log('Token invalid, logging out');
          logout();
        }
      } catch (error) {
        console.error('Token verification error:', error);
        if (axios.isAxiosError(error)) {
          console.error('Axios error details:', {
            status: error.response?.status,
            data: error.response?.data,
            headers: error.response?.headers
          });
        }
        logout();
      }
    };

    verifyToken();
  }, [token]);

  const login = async (username: string, password: string) => {
    try {
      console.log('Attempting login for username:', username);
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await api.post('/token', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      
      console.log('Login response:', response.data);
      const { access_token } = response.data;
      if (!access_token) {
        throw new Error('No access token received');
      }

      localStorage.setItem('token', access_token);
      setToken(access_token);
    } catch (error) {
      console.error('Login error:', error);
      if (axios.isAxiosError(error)) {
        console.error('Axios error details:', {
          status: error.response?.status,
          data: error.response?.data,
          headers: error.response?.headers
        });
      }
      throw new Error('Invalid credentials');
    }
  };

  const signup = async (username: string, email: string, password: string) => {
    try {
      console.log('Attempting signup for username:', username);
      const response = await api.post('/create-user', {
          "email":email,
        "username":username,
        "password":password
      });
      console.log('Signup response:', response.data);

      // After successful signup, log the user in
      await login(username, password);
    } catch (error) {
      console.error('Signup error:', error);
      if (axios.isAxiosError(error)) {
        console.error('Axios error details:', {
          status: error.response?.status,
          data: error.response?.data,
          headers: error.response?.headers
        });
      }
      throw new Error('Failed to create account');
    }
  };

  const logout = () => {
    console.log('Logging out');
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
  };

  const value = {
    user,
    token,
    isAuthenticated,
    login,
    signup,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};