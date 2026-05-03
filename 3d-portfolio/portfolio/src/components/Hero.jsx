import { motion, useSpring } from 'framer-motion';
import { styles } from '../styles';
import { useScroll, useTransform } from 'framer-motion';
import { useRef } from 'react';
import { FaEnvelope, FaLinkedin } from 'react-icons/fa';
import DownloadButton from './DownloadBtn';
import Tilt from 'react-parallax-tilt';

const PresentationCard = () => {
  return (
    <div
      className="relative flex flex-col items-center justify-center p-6 group 
                  backdrop-blur-sm	
                  w-[350px]
                  border 
                  border-white/[0.18] 
                  rounded-3xl 
                  shadow-[0_0_100px_rgba(46,108,255,0.35)] 
                  hover:shadow-[140px_140px_240px_rgba(46,108,255,0.25),_-140px_-140px_240px_rgba(46,108,255,0.25)]
                  transition-all duration-500 ease-in-out"
    >
      <div className="w-40 h-40 rounded-full overflow-hidden">
        <img
          src="/src/assets/pfp.jpg"
          alt="Joaquin"
          className="w-full h-full object-cover"
        />
      </div>

      <p className="heroSubText z-10 mt-4 text-center">JOAQUIN</p>

      <p className="z-10 text-center mt-2">B.Sc. Robotics and Intelligent Systems</p>

      <div className="flex flex-col items-center mt-6 z-10">
        <div className="flex gap-4">
          <a
            href="mailto:ariasnavas.joaquin@gmail.com"
            className="hover:text-gray-300 text-2xl"
          >
            <FaEnvelope />
          </a>
          <a
            href="https://www.linkedin.com/in/joaquin"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-gray-300 text-2xl"
          >
            <FaLinkedin />
          </a>
        </div>
        <div className="mt-5 -bottom-10">
          <DownloadButton />
        </div>
      </div>
    </div>
  );
};

const Hero = () => {
  const ref = useRef(null);

  return (
    <>
      <section ref={ref} className="relative w-full mx-auto">
        <div
          className="sticky top-0 w-full h-screen flex flex-row items-center justify-center pt-20 text-secondary 
          bg-bg-image bg-cover bg-no-repeat bg-center"
        >
          <PresentationCard />

          <div className="ml-20">
            <h1 className={`${styles.heroHeadText} text-white`}>
              Hi, I'm <span className="text-[#0033AC]">JOAQUIN</span>
            </h1>
            <p className={`${styles.heroSubText} mt-2 text-white-100`}>
              I develop 3D visuals, user{' '}
              <br className="sm:block hidden" />
              interfaces and web applications
            </p>
          </div>
        </div>
      </section>
    </>
  );
};

export default Hero;