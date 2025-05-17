import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from './AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Create context
export const PortfolioContext = createContext(null);

// Context provider
export const PortfolioProvider = ({ children }) => {
  const { currentUser } = useAuth();
  const [portfolios, setPortfolios] = useState([]);
  const [currentPortfolio, setCurrentPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Fetch portfolios when user changes
  useEffect(() => {
    const fetchPortfolios = async () => {
      if (!currentUser) {
        setPortfolios([]);
        setCurrentPortfolio(null);
        setLoading(false);
        return;
      }
      
      try {
        setLoading(true);
        const response = await axios.get(`${API}/portfolio`);
        setPortfolios(response.data);
        
        // Set current portfolio to the first one if available
        if (response.data.length > 0 && !currentPortfolio) {
          setCurrentPortfolio(response.data[0]);
        }
        
        setError(null);
      } catch (error) {
        console.error('Error fetching portfolios:', error);
        setError('Failed to fetch portfolios');
      } finally {
        setLoading(false);
      }
    };
    
    fetchPortfolios();
  }, [currentUser]);
  
  // Fetch a specific portfolio
  const fetchPortfolio = async (portfolioId) => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/portfolio/${portfolioId}`);
      setCurrentPortfolio(response.data);
      setError(null);
      return response.data;
    } catch (error) {
      console.error('Error fetching portfolio:', error);
      setError('Failed to fetch portfolio');
      return null;
    } finally {
      setLoading(false);
    }
  };
  
  // Create a new portfolio
  const createPortfolio = async (portfolioData) => {
    try {
      setLoading(true);
      const response = await axios.post(`${API}/portfolio`, portfolioData);
      
      // Add new portfolio to the list
      setPortfolios([...portfolios, response.data]);
      
      // Set as current portfolio
      setCurrentPortfolio(response.data);
      
      setError(null);
      return response.data;
    } catch (error) {
      console.error('Error creating portfolio:', error);
      setError('Failed to create portfolio');
      return null;
    } finally {
      setLoading(false);
    }
  };
  
  // Delete a portfolio
  const deletePortfolio = async (portfolioId) => {
    try {
      setLoading(true);
      await axios.delete(`${API}/portfolio/${portfolioId}`);
      
      // Remove from list
      const updatedPortfolios = portfolios.filter(p => p.id !== portfolioId);
      setPortfolios(updatedPortfolios);
      
      // If the current portfolio was deleted, set a new one or null
      if (currentPortfolio?.id === portfolioId) {
        setCurrentPortfolio(updatedPortfolios.length > 0 ? updatedPortfolios[0] : null);
      }
      
      setError(null);
      return true;
    } catch (error) {
      console.error('Error deleting portfolio:', error);
      setError('Failed to delete portfolio');
      return false;
    } finally {
      setLoading(false);
    }
  };
  
  // Context value
  const value = {
    portfolios,
    currentPortfolio,
    loading,
    error,
    fetchPortfolio,
    createPortfolio,
    deletePortfolio,
    setCurrentPortfolio
  };
  
  return <PortfolioContext.Provider value={value}>{children}</PortfolioContext.Provider>;
};

// Custom hook for using portfolio context
export const usePortfolio = () => {
  const context = useContext(PortfolioContext);
  if (!context) {
    throw new Error('usePortfolio must be used within a PortfolioProvider');
  }
  return context;
};
