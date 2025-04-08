import { createStore } from 'vuex';
import { createClient } from '@supabase/supabase-js';
import axios from "axios";
import router from '../router'; // Make sure to import router

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)

export default createStore({
  state: {
    user: null,
    role: null,
    authInitialized: false
  },
  mutations: {
    setUser(state, user) {
      state.user = user;
      state.role = user?.user_metadata?.role || null;
    },
    clearUser(state) {
      state.user = null;
      state.role = null;
    },
    setAuthInitialized(state, value) {
      state.authInitialized = value;
    }
  },
  getters: {
    isAuthenticated(state) {
      return state.user !== null;
    },
    userRole(state) {
      return state.role;
    },
    isAuthInitialized(state) {
      return state.authInitialized;
    }
  },
  actions: {
    setUser({ commit }, user) {
      commit('setUser', user);
    },
    async logout({ commit }) {
      await supabase.auth.signOut(); 
      commit('clearUser');
      router.push('/');
    },
    async apiRequest({ state }, { method, endpoint, data = null }) {
      try {
        const url = `${endpoint}`;
        const config = { method, url, data };

        const response = await axios(config);
        return response.data;
      } catch (error) {
        console.error(`API ${method.toUpperCase()} Error:`, error);
        throw error;
      }
    },
    async initializeAuth({ commit, dispatch }) {
      try {
        // Check current session
        const { data: { session }, error } = await supabase.auth.getSession();
        
        if (error) {
          console.error("Error checking session:", error);
          commit('setAuthInitialized', true);
          return;
        }
        
        if (session?.user) {
          dispatch('setUser', session.user);
        }
        
        // Set up listener for future auth changes
        const { data: authListener } = supabase.auth.onAuthStateChange((event, session) => {
          if (session?.user) {
            dispatch('setUser', session.user);
          } else {
            commit('clearUser');
            router.push('/');
          }
        });
        
        commit('setAuthInitialized', true);
        return () => {
          authListener?.unsubscribe();
        };
      } catch (error) {
        console.error("Auth initialization error:", error);
        commit('setAuthInitialized', true);
      }
    },
    async redirectBasedOnRole({ state }) {
      // Redirect based on user role
      if (state.user) {
        const role = state.role;
        
        switch (role) {
          case 'F': // Food Bank
            router.push('/home/bank');
            break;
          case 'D': // Donor
            router.push('/home/donor');
            break;
          case 'V': // Volunteer
            router.push('/home');
            break;
          default:
            // If role is undefined or not recognized
            router.push('/');
            break;
        }
      } else {
        router.push('/');
      }
    }
  },
});