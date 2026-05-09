import { MessageCircle } from 'lucide-react';
import { motion } from 'framer-motion';

export default function WhatsAppCTA() {
  return (
    <motion.button
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ delay: 1, type: "spring", stiffness: 200 }}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
      className="fixed bottom-6 right-6 z-50 bg-[#25D366] text-white p-4 rounded-full shadow-2xl shadow-[#25D366]/40 flex items-center justify-center group"
    >
      <MessageCircle className="w-7 h-7" />
      
      {/* Tooltip on hover */}
      <div className="absolute right-full mr-4 bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 px-4 py-2 rounded-xl text-sm font-bold shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap border border-gray-100 dark:border-gray-800">
        Chat on WhatsApp
      </div>
    </motion.button>
  );
}
