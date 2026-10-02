// backend/seeders/gestureSeeder.js
const mongoose = require('mongoose');
const Gesture = require('../models/gesture');
require('dotenv').config();

const gestures = [
  { letter: 'A', name: 'Letter A', description: 'Fist with thumb on side', meaning: 'Approval', difficulty: 'easy' },
  { letter: 'B', name: 'Letter B', description: 'All fingers extended, thumb across palm', meaning: 'Stop', difficulty: 'easy' },
  { letter: 'C', name: 'Letter C', description: 'Curved hand like the letter C', meaning: 'Okay', difficulty: 'medium' },
  { letter: 'D', name: 'Letter D', description: 'Index finger up, others in fist', meaning: 'Pointing', difficulty: 'easy' },
  { letter: 'E', name: 'Letter E', description: 'All fingers curled, thumb over fingers', meaning: 'No specific meaning', difficulty: 'hard' },
  { letter: 'F', name: 'Letter F', description: 'Index and thumb touching, other fingers up', meaning: 'Perfect/Excellent', difficulty: 'medium' },
  { letter: 'G', name: 'Letter G', description: 'Index finger pointing sideways', meaning: 'Direction', difficulty: 'easy' },
  { letter: 'H', name: 'Letter H', description: 'Index and middle fingers together', meaning: 'Peace', difficulty: 'easy' },
  { letter: 'I', name: 'Letter I', description: 'Pinky finger up', meaning: 'Small/Little', difficulty: 'easy' },
  { letter: 'L', name: 'Letter L', description: 'Thumb and index making L shape', meaning: 'Loser/Love', difficulty: 'easy' },
  { letter: 'V', name: 'Letter V', description: 'Index and middle finger separated', meaning: 'Victory/Peace', difficulty: 'easy' },
  { letter: 'Y', name: 'Letter Y', description: 'Thumb and pinky extended', meaning: 'Rock on/Hang loose', difficulty: 'easy' },
  { letter: 'THUMBS_UP', name: 'Thumbs Up', description: 'Thumb extended upward', meaning: 'Good/Approval', difficulty: 'easy' },
  { letter: 'THUMBS_DOWN', name: 'Thumbs Down', description: 'Thumb extended downward', meaning: 'Bad/Disapproval', difficulty: 'easy' },
  { letter: 'OK', name: 'OK Sign', description: 'Thumb and index making circle', meaning: 'Okay/Perfect', difficulty: 'easy' },
  { letter: 'PEACE', name: 'Peace Sign', description: 'Index and middle fingers up', meaning: 'Peace/Victory', difficulty: 'easy' },
  { letter: 'ROCK', name: 'Rock Sign', description: 'Index and pinky up, others down', meaning: 'Rock music', difficulty: 'medium' },
  { letter: 'LOVE', name: 'Love You', description: 'Pinky, index and thumb extended', meaning: 'I love you', difficulty: 'hard' }
];

async function seedGestures() {
  try {
    await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/gesture_db');
    console.log('🌱 Connected to MongoDB');

    // Clear existing gestures
    await Gesture.deleteMany({});
    console.log('🗑️ Cleared existing gestures');

    // Insert new gestures
    await Gesture.insertMany(gestures);
    console.log(`✅ Seeded ${gestures.length} gestures`);

    process.exit(0);
  } catch (error) {
    console.error('❌ Seeding error:', error);
    process.exit(1);
  }
}

seedGestures();