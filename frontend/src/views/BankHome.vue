<template>
  <div class="app-container">
    <Navbar 
      v-model="activeTab" 
      @logout="signOut" 
      :tabNames="{ overview: 'Hubs Listing', listings: 'Reservations' }"
    />
    
    <main class="content">
      <transition name="fade" mode="out-in">
        <component 
          :is="currentTabComponent" 
          :listings="postedListing" 
          @listing-posted="handleListingPosted" 
          :userId="user?.id" 
          :key="activeTab" 
        />
      </transition>
    </main>
  </div>
</template>

<script setup>
import { ref, inject, onMounted, computed } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import Navbar from '../components/Navbar.vue';
import HubsListing from '../components/HubsListing.vue';
import Reservations from '../components/Reservations.vue';

const supabase = inject('supabase');
const store = useStore();
const router = useRouter();
const user = ref(null);
const activeTab = ref('overview');
const postedListing = ref([]);

// Compute the current component based on active tab
const currentTabComponent = computed(() => {
  return activeTab.value === 'overview' ? HubsListing : Reservations;
});

// Check authentication on component mount
onMounted(async () => {
  await checkAuth();
});

const checkAuth = async () => {
  // Check the current session
  const { data: { session }, error } = await supabase.auth.getSession();
  
  if (error) {
    console.error("Error checking session:", error);
    router.push("/");
    return;
  }
  
  if (session?.user && session.user?.user_metadata?.role === "F") {
    user.value = session.user;
    console.log("User authenticated:", user.value);
  } else {
    user.value = null;
    router.push("/");
  }
  
  // Set up the listener for future changes
  const { data: authListener } = supabase.auth.onAuthStateChange((event, session) => {
    if (session?.user && session.user?.user_metadata?.role === "F") {
      user.value = session.user;
      console.log("Auth state changed - user authenticated:", user.value);
    } else {
      user.value = null;
      router.push("/");
    }
  });
  
  // Return the unsubscribe function
  return () => {
    authListener?.unsubscribe();
  };
};

// Logout function
const signOut = async () => {
  await store.dispatch('logout');
  router.push('/');
};

// Handle new listing posted
const handleListingPosted = (newListing) => {
  postedListing.value.push(newListing);
  activeTab.value = 'overview'; // Switch to current listings tab after posting
};
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #fafafa;
}

.content {
  flex: 1;
  padding: 1.5rem;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .content {
    padding: 1rem 0.75rem;
  }
}
</style>