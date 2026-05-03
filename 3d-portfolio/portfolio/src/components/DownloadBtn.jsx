import React from 'react';

const DownloadButton = () => {
  return (
    <div className="inline-block">
      <button className="
        flex
        items-center
        justify-start
        relative w-[45px] h-[45px]
        bg-white/10
        rounded-full
        overflow-hidden
        shadow-md
        transition-all
        duration-300
        ease-in-out
        group/btn
        hover:w-32
        hover:rounded-full
        hover:bg-green-600
      ">
        <div className="
          flex
          items-center
          justify-center
          w-full
          transition-all
          duration-300
          group-hover/btn:w-1/3
          group-hover/btn:pl-5
        ">
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            viewBox="0 0 24 24" 
            className="w-4 h-4 fill-white"
          >
            <path d="M12 2a1 1 0 0 1 1 1v12.585l3.293-3.292a1 1 0 0 1 1.414 1.414l-5 5a1 1 0 0 1-1.414 0l-5-5a1 1 0 0 1 1.414-1.414L11 15.585V3a1 1 0 0 1 1-1zm-7 18a1 1 0 0 1 1-1h12a1 1 0 0 1 0 2H6a1 1 0 0 1-1-1z"/>
          </svg>
        </div>
        <span className="
          absolute
          right-0
          transition-all
          duration-300
          opacity-0
          text-white
          text-lg
          font-semibold
          group-hover/btn:opacity-100
          group-hover/btn:pr-4
        ">
          CV
        </span>
      </button>
    </div>
  );
};

export default DownloadButton;