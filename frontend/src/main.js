import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
);

createApp(App)
    .use(router)
    .provide('supabase', supabase)
    .mount('#app')
