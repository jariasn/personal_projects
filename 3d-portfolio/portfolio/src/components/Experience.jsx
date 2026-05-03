import { VerticalTimeline, VerticalTimelineElement }  from 'react-vertical-timeline-component';
import { motion } from 'framer-motion'
import 'react-vertical-timeline-component/style.min.css';
import { styles } from '../styles'
import { SectionWrapper } from '../hoc'
import { experiences } from '../constants'
import { textVariant } from '../utils/motion'

const ExperienceCard = ({ experience }) => (
  <VerticalTimelineElement 
    contentStyle={{ background: 'rgba(172, 172, 172, 0.2)', backdropFilter: 'blur(3px)', boxShadow: '0 4px 10px rgba(0, 0, 0, 0.2)', color: '#000'}} 
    contentArrowStyle={{ borderRight: '9px solid rgba(172, 172, 172, 0.3)' }} 
    date={<span className="font-serif">{experience.date} </span>}
    iconStyle={{ background: experience.iconBg }} 
    icon={
      <div className='flex justify-center items-center w-full h-full'>
        <img src={experience.icon} alt={experience.company_name} className='w-[60%] h-[60%] object-contain'/>
      </div>
    }
  >
    <div>
      <h3 className='text-black text-[24px] font-serif'>
        {experience.title}
      </h3>
      <p className='text-secondary text-[16px] font-semibold font-serif' style={{ margin: 0 }}>
        {experience.company_name}
      </p>
    </div>
    <ul className='mt-5 list-disc ml-5 space-y-2'>
      {experience.points.map((point, index) => (
        <li key={`experience-point-${index}`} className='text-black-100 text-[14px] pl-1 tracking-wider font-serif'>
          {point}
        </li>
      ))}

    </ul>
  </VerticalTimelineElement>
)
const Experience = () => {
  return (
    <>
      <motion.div variants={textVariant()}>
        <p className={styles.sectionSubText}>What i have done</p>
        <h2 className={styles.sectionHeadText}>Work Experience.</h2>
      </motion.div>
      <div className='mt-20 flex flex-col'>
        <VerticalTimeline lineColor="#856755">
          {experiences.map((experience, index) => (
            <ExperienceCard key={index} experience={experience} />
        ))}
        </VerticalTimeline>

      </div>
    </>
  )
}

export default SectionWrapper(Experience, "work")