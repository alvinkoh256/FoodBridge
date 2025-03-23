import { createStore } from 'vuex';

export default createStore({
  state: {
    userId: null,
    role: null
  },
  mutations: {
    setUser(state, user) {
      state.userId = user.id;
      state.role = user.user_metadata?.role || null;
    },
    clearUser(state) {
      state.userId = null;
      state.role = null;
    }
  },
  actions: {
    saveUser({ commit }, user) {
      commit('setUser', user);
    },
    logout({ commit }) {
      commit('clearUser');
    }
  }
});
