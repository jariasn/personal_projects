import React, { useEffect, useState } from 'react';
import { BrowserRouter } from 'react-router-dom';
import ThemeContext from './components/ThemeContext'; // Create a new ThemeContext
import { About, Contact, Experience, Feedbacks, Hero, Navbar, Tech, Works } from './components';

const App = () => {
  const [theme, setTheme] = useState('dark'); // Initialize theme state

  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === 'dark' ? 'light' : 'dark'));
  };

  useEffect(() => {
    const root = window.document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      <BrowserRouter>
        {/* Add gradient and other effects */}
        <div
          className={`relative z-0 bg-primary text-secondary  
                      before:absolute before:inset-0 before:bg-grid-overlay before:opacity-10 
                      dark:before:opacity-20`}
        >
          <div className="relative">
            <Navbar />
            <Hero />
          </div>
          <About />
          <Experience />
          <Tech />
          <Works />
          <Feedbacks />
          <div className="relative z-0">
            <Contact />
          </div>
        </div>
      </BrowserRouter>
    </ThemeContext.Provider>
  );
};

export default App;