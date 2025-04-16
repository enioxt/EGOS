import React from 'react';

const Header = () => {
  return (
    <header className="bg-egos-blue text-white p-4 shadow-md">
      <div className="container mx-auto flex justify-between items-center">
        <h1 className="text-xl font-serif font-bold">EGOS Project</h1>
        {/* Placeholder for navigation */}
        <nav>
          <ul className="flex space-x-4">
            <li><a href="#" className="hover:text-egos-lavender">Home</a></li>
            <li><a href="#" className="hover:text-egos-lavender">About</a></li>
            {/* Add more links later */}
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header;
