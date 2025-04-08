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
import { ref, inject, onMounted, computed, watch } from 'vue';
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

// Check role and access on component mount
onMounted(async () => {
  // Wait for auth to be initialized
  await checkAuthAndAccess();
});

// Watch for role changes
watch(
  () => store.getters.userRole,
  (newRole) => {
    if (store.getters.isAuthInitialized) {
      checkRole(newRole);
    }
  }
);

const checkAuthAndAccess = async () => {
  if (!store.getters.isAuthInitialized) {
    await store.dispatch('initializeAuth');
  }
  
  // Update local user object
  user.value = store.state.user;
  
  // Check role
  checkRole(store.getters.userRole);
};

const checkRole = (role) => {
  // Only allow access if role is 'F' (Food Bank)
  if (role !== 'F') {
    console.log('Unauthorized role for BankHome:', role);
    router.push('/');
    return;
  }
  
  // Update local user reference
  user.value = store.state.user;
  console.log("User authenticated in BankHome:", user.value);
};

// Logout function
const signOut = async () => {
  await store.dispatch('logout');
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