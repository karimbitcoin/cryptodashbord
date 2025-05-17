import React, { useState, useEffect } from 'react';
import axios from 'axios';
import NewsCard from './NewsCard';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const NewsFeed = ({ limit = 6, category = null }) => {
  const [news, setNews] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeCategory, setActiveCategory] = useState(category);

  const categories = [
    { id: null, name: 'All' },
    { id: 'Bitcoin', name: 'Bitcoin' },
    { id: 'Ethereum', name: 'Ethereum' },
    { id: 'DeFi', name: 'DeFi' },
    { id: 'NFT', name: 'NFTs' },
    { id: 'Regulation', name: 'Regulation' }
  ];

  useEffect(() => {
    const fetchNews = async () => {
      try {
        setIsLoading(true);
        let url = `${API}/news?limit=${limit}`;
        
        if (activeCategory) {
          url += `&category=${activeCategory}`;
        }
        
        if (searchTerm) {
          url += `&search=${searchTerm}`;
        }
        
        const response = await axios.get(url);
        setNews(response.data);
        setError(null);
      } catch (error) {
        console.error('Error fetching news:', error);
        setError('Failed to load news articles');
      } finally {
        setIsLoading(false);
      }
    };

    fetchNews();
  }, [limit, activeCategory, searchTerm]);

  const handleCategoryChange = (categoryId) => {
    setActiveCategory(categoryId);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    // Search is triggered by the effect
  };

  return (
    <div className="w-full">
      <div className="mb-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4">
          <h2 className="text-xl font-medium mb-2 sm:mb-0">Latest News</h2>
          
          <form onSubmit={handleSearch} className="w-full sm:w-auto">
            <div className="relative">
              <input
                type="text"
                placeholder="Search news..."
                className="w-full bg-slate-700 text-white rounded-md px-4 py-2 pr-10 focus:outline-none focus:ring-2 focus:ring-cyan-500"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              <button type="submit" className="absolute right-2 top-2 text-gray-400">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
            </div>
          </form>
        </div>
        
        <div className="flex space-x-2 overflow-x-auto pb-2 mb-4">
          {categories.map((cat) => (
            <button
              key={cat.id || 'all'}
              className={`px-3 py-1 rounded-md whitespace-nowrap ${
                activeCategory === cat.id
                  ? 'bg-cyan-600 text-white'
                  : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
              }`}
              onClick={() => handleCategoryChange(cat.id)}
            >
              {cat.name}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(limit)].map((_, index) => (
            <div key={index} className="bg-slate-800 rounded-lg shadow-lg overflow-hidden animate-pulse">
              <div className="h-40 bg-slate-700"></div>
              <div className="p-4">
                <div className="flex justify-between mb-2">
                  <div className="h-4 bg-slate-700 rounded w-20"></div>
                  <div className="h-4 bg-slate-700 rounded w-16"></div>
                </div>
                <div className="h-5 bg-slate-700 rounded w-full mb-2"></div>
                <div className="h-5 bg-slate-700 rounded w-2/3 mb-4"></div>
                <div className="h-4 bg-slate-700 rounded w-full mb-2"></div>
                <div className="h-4 bg-slate-700 rounded w-4/5"></div>
              </div>
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="bg-red-500 bg-opacity-20 border border-red-500 rounded-md p-4 text-red-500">
          {error}
        </div>
      ) : news.length === 0 ? (
        <div className="bg-slate-800 rounded-lg shadow-lg p-6 text-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
          <p className="text-lg text-gray-400">No news articles found</p>
          {(activeCategory || searchTerm) && (
            <button
              onClick={() => {
                setActiveCategory(null);
                setSearchTerm('');
              }}
              className="mt-4 bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-md"
            >
              Clear filters
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {news.map((article, index) => (
            <NewsCard key={index} article={article} />
          ))}
        </div>
      )}
    </div>
  );
};

export default NewsFeed;