import { createStore } from 'vuex';
import { createClient } from '@supabase/supabase-js';
import axios from "axios";

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)

export default createStore({
  state: {
    user: null,
    role: null,
    apiBaseUrl: '', 
  },
  mutations: {
    setUser(state, user) {
      state.user = user;
      state.role = user?.user_metadata?.role || null;
    },
    clearUser(state) {
      state.user = null;
    },
  },
  getters: {
    isAuthenticated(state) {
      return state.user !== null;
    },
    userRole(state) {
      return state.role;
    },
  },
  actions: {
    setUser({ commit }, user) {
      commit('setUser', user);
    },
    async logout({ commit }) {
      await supabase.auth.signOut(); 
      commit('clearUser');
    },
    async apiRequest({ state }, { method, endpoint, data = null },) {
      try {
        const url = `${state.apiBaseUrl}${endpoint}`;
        const config = { method, url, data };

        const response = await axios(config);
        return response.data;
      } catch (error) {
        console.error(`API ${method.toUpperCase()} Error:`, error);
        throw error;
      }
    },
  },
});