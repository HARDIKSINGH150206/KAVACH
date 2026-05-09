import { useEffect, useRef, useState } from 'react';
import { motion, useInView } from 'framer-motion';
import { Users, AlertTriangle, Clock } from 'lucide-react';

const stats = [
  {
    id: 1,
    value: 640,
    suffix: 'M+',
    label: 'Indians live without nearby doctor access',
    icon: Users,
    color: 'text-teal-500',
    bg: 'bg-teal-500/10'
  },
  {
    id: 2,
    value: 72,
    suffix: '%',
    label: 'Of deaths in rural areas are preventable',
    icon: AlertTriangle,
    color: 'text-amber-500',
    bg: 'bg-amber-500/10'
  },
  {
    id: 3,
    value: 4.2,
    suffix: ' hrs',
    label: 'Average wait time for basic consultation',
    icon: Clock,
    color: 'text-blue-500',
    bg: 'bg-blue-500/10',
    decimals: 1
  }
];

function Counter({ from, to, suffix, decimals = 0, duration = 2 }) {
  const [count, setCount] = useState(from);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  useEffect(() => {
    if (!isInView) return;

    let startTime;
    const updateCount = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const progress = timestamp - startTime;
      const progressPercentage = Math.min(progress / (duration * 1000), 1);
      
      // Easing function for smooth slowdown at the end
      const easeOutQuart = 1 - Math.pow(1 - progressPercentage, 4);
      
      const currentVal = from + (to - from) * easeOutQuart;
      setCount(currentVal);

      if (progressPercentage < 1) {
        requestAnimationFrame(updateCount);
      }
    };

    requestAnimationFrame(updateCount);
  }, [isInView, from, to, duration]);

  return (
    <span ref={ref}>
      {count.toFixed(decimals)}
      {suffix}
    </span>
  );
}

export default function ProblemStatsSection() {
  return (
    <section className="py-24 bg-white dark:bg-primary-dark">
      <div className="container mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            The Rural Healthcare Crisis
          </h2>
          <p className="text-gray-600 dark:text-gray-400 text-lg">
            Millions lack access to basic medical advice when they need it most. We are changing that.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.id}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.6, delay: index * 0.2 }}
              className="glass-card p-8 rounded-3xl relative overflow-hidden group hover:-translate-y-2 transition-transform duration-300"
            >
              <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 group-hover:scale-110 transition-all duration-500">
                <stat.icon className={`w-24 h-24 ${stat.color}`} />
              </div>
              
              <div className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-6 ${stat.bg}`}>
                <stat.icon className={`w-7 h-7 ${stat.color}`} />
              </div>
              
              <div className="text-5xl font-extrabold text-gray-900 dark:text-white mb-4 font-heading tracking-tight">
                <Counter from={0} to={stat.value} suffix={stat.suffix} decimals={stat.decimals} />
              </div>
              
              <p className="text-gray-600 dark:text-gray-300 font-medium leading-relaxed">
                {stat.label}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
