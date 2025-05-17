import React from 'react';
import moment from 'moment';

const NewsCard = ({ article }) => {
  return (
    <a 
      href={article.url} 
      target="_blank" 
      rel="noopener noreferrer"
      className="block bg-slate-800 rounded-lg overflow-hidden shadow-lg hover:shadow-xl transition-shadow duration-300 hover:bg-slate-700"
    >
      <div className="h-40 overflow-hidden bg-slate-700">
        {article.thumbnail ? (
          <img 
            src={article.thumbnail} 
            alt={article.title} 
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.onerror = null;
              e.target.src = "https://via.placeholder.com/300x200/374151/94A3B8?text=Crypto+News";
            }}
          />
        ) : (
          <div className="w-full h-full bg-slate-700 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
            </svg>
          </div>
        )}
      </div>
      <div className="p-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm text-cyan-400">{article.source}</span>
          <span className="text-xs text-gray-400">{moment(article.published_at).fromNow()}</span>
        </div>
        <h3 className="text-lg font-semibold mb-2 line-clamp-2">{article.title}</h3>
        {article.summary && (
          <p className="text-gray-400 text-sm line-clamp-2">{article.summary}</p>
        )}
        {article.category && (
          <div className="mt-3">
            <span className="inline-block px-2 py-1 text-xs bg-slate-700 text-gray-300 rounded-md">
              {article.category}
            </span>
          </div>
        )}
      </div>
    </a>
  );
};

export default NewsCard;