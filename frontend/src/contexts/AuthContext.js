import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Create context
export const AuthContext = createContext(null);

// Context provider
export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Check if user is already logged in (token in localStorage)
  useEffect(() => {
    const checkLoggedIn = async () => {
      const token = localStorage.getItem('cryptoToken');
      
      if (token) {
        try {
          // Set auth header for all future requests
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          // Get current user info
          const response = await axios.get(`${API}/auth/me`);
          setCurrentUser(response.data);
        } catch (error) {
          console.error('Error fetching user data:', error);
          // If token is invalid/expired, remove it
          localStorage.removeItem('cryptoToken');
          delete axios.defaults.headers.common['Authorization'];
        }
      }
      
      setLoading(false);
    };
    
    checkLoggedIn();
  }, []);
  
  // Login function
  const login = async (email, password) => {
    setError(null);
    try {
      // FormData is required for the OAuth2 password flow
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);
      
      const response = await axios.post(`${API}/auth/login`, formData);
      
      // Store token in localStorage
      localStorage.setItem('cryptoToken', response.data.access_token);
      
      // Set auth header for all future requests
      axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
      
      // Get user data
      const userResponse = await axios.get(`${API}/auth/me`);
      setCurrentUser(userResponse.data);
      
      return true;
    } catch (error) {
      setError(error.response?.data?.detail || 'Login failed');
      console.error('Login error:', error);
      return false;
    }
  };
  
  // Register function
  const register = async (email, username, password) => {
    setError(null);
    try {
      await axios.post(`${API}/auth/register`, {
        email,
        username,
        password
      });
      
      // After successful registration, log the user in
      return await login(email, password);
    } catch (error) {
      setError(error.response?.data?.detail || 'Registration failed');
      console.error('Registration error:', error);
      return false;
    }
  };
  
  // Logout function
  const logout = () => {
    localStorage.removeItem('cryptoToken');
    delete axios.defaults.headers.common['Authorization'];
    setCurrentUser(null);
  };
  
  // Context value
  const value = {
    currentUser,
    loading,
    error,
    login,
    register,
    logout
  };
  
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook for using auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
