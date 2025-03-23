<template>
  <div class="home-container">

    <div class="header">
      <div class="section-title">Postings for you</div>
    </div>
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

    <button @click="signOut">Log Out</button>
    <Dialog v-model:visible="visible" modal header="Drop-off at (A CC)" :style="{ width: '75rem' }">
      <DialogContent/>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, inject, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import DialogContent from '../components/DialogContent.vue';
import Dialog from 'primevue/dialog';

const supabase = inject('supabase');
const store = useStore();
const router = useRouter();
const user = ref(null);
const visible = ref(false);

const { data } = supabase.auth.onAuthStateChange((event, session) => {
  if (session?.user && session.user?.user_metadata?.role == "volunteer") {
    // User is logged in
    user.value = session.user; 
    console.log("User authenticated:", user.value);
  } 
  else {
    user.value = null;
    router.push("/"); 
  }
});

const signOut = async () =>{
  store.dispatch('logout');
  router.push('/')
};

const openDialog = () => {
  visible.value = true;
};

const closeDialog = () => {
  visible.value = false;
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

.header {
  background-color: #4a86e8;
  color: white;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 20px;
}

.section-title {
  font-size: 25px;
  font-weight: bold;
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
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
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

img{
  object-fit: cover; /* Ensures the image covers the circle without distortion */
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
</style>
