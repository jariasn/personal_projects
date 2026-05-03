import React from 'react'
import Tilt from 'react-parallax-tilt'
import { motion } from 'framer-motion'
import { styles } from '../styles'
import { services } from '../constants'
import {fadeIn, textVariant} from '../utils/motion'
import { SectionWrapper } from '../hoc'

const ServiceCard = ({ index, title, icon }) => {
  return (
    <Tilt className='xs:w-[250px] w-full'>
      <motion.div variants={fadeIn("right", "spring", 0.5*index, 0.75)} className='w-full p-[1px] rounded-[20px] '>
        <div options={{max: 45, scale: 1, speed:150}} className='rounded-[20px] py-5 px-12 min-h-[280px] flex justify-evenly items-center flex-col' style={{ background: 'rgba(172, 172, 172, 0.2)', backdropFilter: 'blur(3px)', boxShadow: '0 4px 10px rgba(0, 0, 0, 0.2)'}}>
          <img src={icon} alt={title} className='w-20 h-20 object-contain'/>
          <h3 className='section-color text-[20px] font-bold text-center font-typewritter'>{title}</h3>
        </div>
      </motion.div>
    </Tilt>
  )
}

const About = () => {
  return (
    <>
      <motion.div variants={textVariant()}>
        <p className={styles.sectionSubText}>Introduction</p>
        <h2 className={styles.sectionHeadText}>Overview.</h2>
      </motion.div>
      <motion.p variants={fadeIn("", "", 0.1, 1)} className='mt-4 text-[20px] max-w-3x1 leading-[30px] font-typewritter'>
        I'm a software engineer with a passion for robotics and artificial intelligence. I have a strong background in robotics, machine learning, and computer vision. I have experience working with various programming languages and frameworks, including Python, C++, and TensorFlow. I'm currently working as a software engineer at a tech company, where I develop software for autonomous vehicles. I'm always looking for new challenges and opportunities to learn and grow as a developer.
      </motion.p>

      <div className='grid-lines-container mt-20 flex flex-wrap gap-10 justify-center items-center'>
        {services.map((service, index) => (
          <ServiceCard key={service.title} index={index} {...service} />
        ))}
      </div>
    </>
  )
}

export default SectionWrapper(About, 'about')