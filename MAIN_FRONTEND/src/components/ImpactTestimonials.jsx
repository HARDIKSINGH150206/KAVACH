import { motion } from 'framer-motion';
import { Quote } from 'lucide-react';

const testimonials = [
  {
    quote: "It was 2 AM and my child had a high fever. There was no doctor nearby. The app told me exactly what first-aid to give and booked an appointment at the PHC for the morning. It saved my child's life.",
    author: "Meena Devi",
    location: "Village in Rajasthan",
    image: "https://images.unsplash.com/photo-1544717302-de2939b7ef71?auto=format&fit=crop&q=80&w=200&h=200"
  },
  {
    quote: "As an ASHA worker, it was hard to diagnose complex symptoms in the field. This app acts like a senior doctor in my pocket, guiding me to make the right decisions for my patients.",
    author: "Sunita Kumari",
    location: "ASHA Worker, Bihar",
    image: "https://images.unsplash.com/photo-1620313658514-61c02abf9b99?auto=format&fit=crop&q=80&w=200&h=200"
  }
];

export default function ImpactTestimonials() {
  return (
    <section className="py-24 bg-amber-50 dark:bg-[#1a130c] relative overflow-hidden">
      {/* Warm background elements */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden opacity-50 dark:opacity-20 pointer-events-none">
        <div className="absolute top-[-10%] right-[-5%] w-[40rem] h-[40rem] bg-amber-400/20 rounded-full blur-[100px]" />
        <div className="absolute bottom-[-10%] left-[-5%] w-[30rem] h-[30rem] bg-rose-400/20 rounded-full blur-[100px]" />
      </div>

      <div className="container mx-auto px-6 relative z-10">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-amber-950 dark:text-amber-500 mb-4 font-heading">
            Voices of Trust
          </h2>
          <p className="text-amber-800/80 dark:text-amber-200/60 text-lg">
            Real stories from the heart of rural India where MediChain is making a difference every single day.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {testimonials.map((test, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.6, delay: index * 0.2 }}
              className="bg-white/80 dark:bg-black/40 backdrop-blur-md p-8 md:p-10 rounded-[2.5rem] shadow-xl shadow-amber-900/5 dark:shadow-black/50 border border-white/40 dark:border-white/5 relative"
            >
              <Quote className="absolute top-8 right-8 w-12 h-12 text-amber-500/20 dark:text-amber-500/10 rotate-180" />
              
              <p className="text-lg md:text-xl text-gray-800 dark:text-gray-200 leading-relaxed font-medium mb-8 relative z-10">
                "{test.quote}"
              </p>
              
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-full overflow-hidden border-2 border-amber-200 dark:border-amber-900">
                  <img src={test.image} alt={test.author} className="w-full h-full object-cover grayscale-[20%]" />
                </div>
                <div>
                  <h4 className="font-bold text-gray-900 dark:text-white">{test.author}</h4>
                  <p className="text-sm text-amber-600 dark:text-amber-500">{test.location}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
