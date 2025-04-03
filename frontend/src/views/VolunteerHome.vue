<template>
  <div class="home-container">

    <div class="header">
      <div class="navbar">
      <div class="logo-section">
        <img src="../assets/Foodbridge.png" alt="Profile" class="logo-image">
      </div>
      <div class="tabs-section">
        <div class="nav-tab">Food Bridge</div>
      </div>
      <div class="logout-section">
        <button class="logout-button" @click="signOut">
          Log Out
        </button>
      </div>
    </div>
    </div>
    <div class="title">For You</div>
    <div class="divider"></div>
    <div class="drop-off-item" @click="openDialog">
      <div class="profile-pic">
        <img src="../assets/logo.jpg" alt="Profile">
      </div>
      <div class="drop-off-info">
        <div class="drop-off-location text-black">Drop-off at (A CC)</div>
        <div class="drop-off-date">14:30 12-Mar-2025</div>
      </div>
    </div>

    <Dialog v-model:visible=visible modal header="Drop-off at (A CC)" :style="{ width: '75rem' }">
      <DialogContentVolunteer/>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, inject, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import DialogContentVolunteer from '../components/DialogContentVolunteer.vue';
import Dialog from 'primevue/dialog';

const supabase = inject('supabase');
const store = useStore();
const router = useRouter();
const user = ref(null);
const visible = ref(false);

// Check authentication on component mount
onMounted(() => {
  checkAuth();
});

// Authentication management
const checkAuth = () => {
  const authListener = supabase.auth.onAuthStateChange((event, session) => {
    if (session?.user && session.user?.user_metadata?.role === "V") {
      user.value = session.user;
      console.log("User authenticated:", user.value);
    } else {
      user.value = null;
      router.push("/");
    }
  });

  // Return cleanup function
  return () => {
    if (authListener && authListener.data) {
      authListener.data.unsubscribe();
    }
  };
};

const signOut = async () =>{
  store.dispatch('logout');
  router.push('/')
};

const openDialog = () => {
  visible.value = true;
};


</script>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 1rem;
  background-color: #fff;
  border-radius: 8px;
}

.nav-tab {
  padding: 8px 16px;
  cursor: pointer;
  font-weight: bold;
  color: black;
  position: relative;
  transition: color 0.2s ease;
}

.header {
  width: 100%;
  background-color: #fff;
  border-bottom: 1px solid #f0f0f0;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  height: 60px;
  padding: 0 8px;
}

.logo-section {
  display: flex;
  align-items: center;
  min-width: 100px;
}

.logo-image {
  max-height: 100px; 
  width: auto;
}

.tabs-section {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex: 1;
}

.divider {
  border-top: 1px solid #ccc;
  margin: 20px 0;
}

.drop-off-item {
  display: flex;
  align-items: center;
  padding: 15px;
  background-color: white;
  border-radius: 5px;
  margin-bottom: 10px;
  border: 3px solid #f44336;
}

.profile-pic {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #ddd;
  margin-right: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.logout-button {
  padding: 8px 16px;
  background-color: transparent;
  color: black;
  border: 2px solid #f44336;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.logout-button:hover {
  background-color: #d32f2f;
  color: white;
}

img{
  object-fit: cover; 
}

.drop-off-info {
  flex-grow: 1;
}

.drop-off-location {
  font-weight: bold;
  margin-bottom: 5px;
}

.drop-off-date {
  font-size: 12px;
  color: #666;
}

.title{
  text-align: left;
  padding-top: 10px;
  font-weight: bold;
  font-size: 40px;
  color: black;
}
</style>
