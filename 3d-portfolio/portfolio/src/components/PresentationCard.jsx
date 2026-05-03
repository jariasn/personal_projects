import React from 'react';

const PresentationCard = () => {
  return (
    <div className="fixed top-1/4 left-10 w-[300px] bg-white rounded-lg shadow-lg p-5">
      <div className="flex flex-col items-center text-center">
        <div className="w-24 h-24 rounded-full bg-orange-500 overflow-hidden">
          {/* Replace with an actual image */}
          <img src="/path-to-image.jpg" alt="Profile" className="w-full h-full object-cover" />
        </div>
        <h2 className="text-xl font-bold mt-4">Mark Smith</h2>
        <p className="text-gray-600 mt-2">
          A Software Engineer who has developed countless innovative solutions.
        </p>
        <div className="flex space-x-3 mt-4">
          <a href="#" className="text-gray-500 hover:text-black">[Social 1]</a>
          <a href="#" className="text-gray-500 hover:text-black">[Social 2]</a>
          <a href="#" className="text-gray-500 hover:text-black">[Social 3]</a>
        </div>
      </div>
    </div>
  );
};

export default PresentationCard;