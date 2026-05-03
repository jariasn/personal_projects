import React, { useContext, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { styles } from "../styles";
import { navLinks } from "../constants";
import { logo, menu, close } from "../assets";

import ThemeContext from './ThemeContext';

const Navbar = () => {
  const [active, setActive] = useState("");
  const [toggle, setToggle] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const { theme, toggleTheme } = useContext(ThemeContext);

  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY;
      setScrolled(scrollTop > 100);
    };

    window.addEventListener("scroll", handleScroll);

    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <>
      {/* SVG Symbols */}
      <svg style={{ display: 'none' }} >
        <symbol id="light" viewBox="0 0 24 24">
          <g stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <line x1="12" y1="20" x2="12" y2="22" transform="rotate(0,12,12)" />
            <line x1="12" y1="20" x2="12" y2="22" transform="rotate(45,12,12)" />
            <line x1="12" y1="20" x2="12" y2="22" transform="rotate(90,12,12)" />
            <line x1="12" y1="20" x2="12" y2="22" transform="rotate(135,12,12)" />
            <line x1="12" y1="20" x2="12" y2="22" transform="rotate(180,12,12)" />
            <line x1="12" y1="20" x2="12" y2="22" transform="rotate(225,12,12)" />
            <line x1="12" y1="20" x2="12" y2="22" transform="rotate(270,12,12)" />
            <line x1="12" y1="20" x2="12" y2="22" transform="rotate(315,12,12)" />
          </g>
          <circle fill="currentColor" cx="12" cy="12" r="5" />
        </symbol>
        <symbol id="dark" viewBox="0 0 24 24">
          <path fill="currentColor" d="M15.1,14.9c-3-0.5-5.5-3-6-6C8.8,7.1,9.1,5.4,9.9,4c0.4-0.8-0.4-1.7-1.2-1.4C4.6,4,1.8,7.9,2,12.5c0.2,5.1,4.4,9.3,9.5,9.5c4.5,0.2,8.5-2.6,9.9-6.6c0.3-0.8-0.6-1.7-1.4-1.2C18.6,14.9,16.9,15.2,15.1,14.9z" />
        </symbol>
      </svg>

      <nav
        className={`${styles.paddingX} w-full flex items-center py-5 fixed top-0 z-20 ${
          scrolled ? "glass" : "bg-transparent"
        }`}
      >
        <div className='w-full flex justify-between items-center max-w-7xl mx-auto'>
          <Link
            to='/'
            className='flex items-center gap-2'
            onClick={() => {
              setActive("");
              window.scrollTo(0, 0);
            }}
          >
            <img src={logo} alt='logo' className='w-9 h-9 object-contain' />
            <p className='text-glass text-[18px] font-bold cursor-pointer flex'>
              Joaquin Arias&nbsp;
              {/* <span className='sm:block hidden'> | JavaScript Mastery</span> */}
            </p>
          </Link>

          {/* Desktop Navbar */}
          <ul className='list-none hidden sm:flex flex-row gap-10 items-center'>
            {navLinks.map((nav) => (
              <li
                key={nav.id}
                className={`${
                  active === nav.title ? "text-white" : "text-secondary"
                } hover:text-white text-[18px] font-medium cursor-pointer`}
                onClick={() => setActive(nav.title)}
              >
                <a href={`#${nav.id}`}>{nav.title}</a>
              </li>
            ))}
            <li>
              <label className="relative flex items-center w-16 h-8 rounded-full cursor-pointer transition-all duration-300 dark:bg-blue-900 bg-yellow-200">
                {/* Hidden Checkbox */}
                <input
                  type="checkbox"
                  className="peer hidden"
                  checked={theme === 'dark'}
                  onChange={toggleTheme}
                />
                {/* Moving Circle */}
                <span className="absolute w-6 h-6 bg-yellow-400 translate-x-1 dark:bg-blue-500 rounded-full transition-transform duration-300 peer-checked:translate-x-9 flex items-center justify-center drop-shadow-md">
                  {/* Sun Icon */}
                  <svg
                    className="w-4 h-4 text-white dark:opacity-0 transition-opacity duration-300 absolute"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <use href="#light" />
                  </svg>
                  {/* Moon Icon */}
                  <svg
                    className="w-4 h-4 text-white opacity-0 dark:opacity-100 transition-opacity duration-300 absolute"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <use href="#dark" />
                  </svg>
                </span>
              </label>
            </li>
          </ul>

          {/* Mobile Menu Toggle Button */}
          <div className='sm:hidden flex flex-1 justify-end items-center'>
            <img
              src={toggle ? close : menu}
              alt='menu'
              className='w-[28px] h-[28px] object-contain'
              onClick={() => setToggle(!toggle)}
            />

            {/* Mobile Menu */}
            <div
              className={`${
                !toggle ? "hidden" : "flex"
              } p-6 black-gradient absolute top-20 right-0 mx-4 my-2 min-w-[140px] z-10 rounded-xl`}
            >
              <ul className='list-none flex justify-end items-start flex-1 flex-col gap-4'>
                {navLinks.map((nav) => (
                  <li
                    key={nav.id}
                    className={`font-poppins font-medium cursor-pointer text-[16px] ${
                      active === nav.title ? "text-white" : "text-secondary"
                    }`}
                    onClick={() => {
                      setToggle(!toggle);
                      setActive(nav.title);
                    }}
                  >
                    <a href={`#${nav.id}`}>{nav.title}</a>
                  </li>
                ))}
                <li>
                  <label className="switch">
                    <input 
                      className="switch__input" 
                      type="checkbox" 
                      role="switch" 
                      name="dark" 
                      checked={theme === 'dark'}
                      onChange={toggleTheme}
                    />
                    <svg className="switch__icon" width="24px" height="24px" aria-hidden="true">
                      <use href="#light" />
                    </svg>
                    <svg className="switch__icon" width="24px" height="24px" aria-hidden="true">
                      <use href="#dark" />
                    </svg>
                    <span className="switch__inner"></span>
                    <span className="switch__inner-icons">
                      <svg className="switch__icon" width="24px" height="24px" aria-hidden="true">
                        <use href="#light" />
                      </svg>
                      <svg className="switch__icon" width="24px" height="24px" aria-hidden="true">
                        <use href="#dark" />
                      </svg>
                    </span>
                    <span className="switch__sr">Dark Mode</span>
                  </label>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </nav>
    </>
  );
};

export default Navbar;