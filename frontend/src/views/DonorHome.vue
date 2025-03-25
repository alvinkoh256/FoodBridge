<template>
  <div class="donation-app">
    <Navbar v-model="activeTab" @logout="signOut"/>
    
    <!-- Content area -->
    <div class="content-area">
      <transition name="fade" mode="out-in">
        <component :is="currentTabComponent" 
                  :listings="postedListing" 
                  @listing-posted="handleListingPosted" 
                  :key="activeTab" />
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, inject, onMounted, computed } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import Navbar from '../components/Navbar.vue';
import CreateListing from '../components/CreateListing.vue';
import PostedListing from '../components/PostedListing.vue';

const supabase = inject('supabase');
const store = useStore();
const router = useRouter();
const user = ref(null);

// Tab navigation
const activeTab = ref('overview'); // Default to Current Listings view
const postedListing = ref([]);

// Compute the current component based on active tab
const currentTabComponent = computed(() => {
  return activeTab.value === 'overview' ? PostedListing : CreateListing;
});

// Check authentication on component mount
onMounted(async () => {
  await checkAuth();
});

// Authentication management
const checkAuth = async () => {
  // First check the current session
  const { data: { session }, error } = await supabase.auth.getSession();
  if (error) {
    console.error("Error checking session:", error);
    router.push("/");
    return;
  }
  
  if (session?.user && session.user?.user_metadata?.role === "donor") {
    user.value = session.user;
    console.log("User authenticated:", user.value);
  } else {
    user.value = null;
    router.push("/");
  }
  
  // Then set up the listener for future changes
  const { data: authListener } = supabase.auth.onAuthStateChange((event, session) => {
    if (session?.user && session.user?.user_metadata?.role === "donor") {
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
.donation-app {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #fff;
}

.content-area {
  background-color: white;
  padding: 20px;
  min-height: 400px;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>