<template>
  <div class="donation-app">
    <Navbar v-model="activeTab" @logout="signOut"/>
    <!-- Content area -->
    <div class="content-area">
      <transition name="fade" mode="out-in">
        <component
          :is="currentTabComponent"
          :listings="postedListing"
          :user="user"
          :key="activeTab"
          @listing-posted="handleListingPosted"
        />
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, inject, onMounted, computed, watch } from 'vue';
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
const products = ref([]);

// Compute the current component based on active tab
const currentTabComponent = computed(() => {
  return activeTab.value === 'overview' ? PostedListing : CreateListing;
});

// Handler for when a listing is posted
const handleListingPosted = (response) => {
  // Switch to the overview tab to show posted listings
  activeTab.value = 'overview';
  fetchPostedListings();
};

// Function to fetch posted listings and filter by hub ID
const fetchPostedListings = async () => {
  if (!user.value?.id) return;
  
  try {
    const response = await store.dispatch('apiRequest', {
      method: 'get',
      endpoint: `http://localhost:8000/product/${user.value.id}`
    });

    if (response && Array.isArray(response)) {
      postedListing.value = response;
    }
  } catch (error) {
    console.error('Failed to fetch products:', error);
  }
};

// Check role and access on component mount
onMounted(async () => {
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
  
  // Fetch listings if we have a valid user
  if (user.value) {
    await fetchPostedListings();
  }
};

const checkRole = (role) => {
  // Only allow access if role is 'D' (Donor)
  if (role !== 'D') {
    console.log('Unauthorized role for DonorHome:', role);
    router.push('/');
    return;
  }
  
  // Update local user reference
  user.value = store.state.user;
  console.log("User authenticated in DonorHome:", user.value);
};

// Logout function
const signOut = async () => {
  await store.dispatch('logout');
};
</script>

<style scoped>
.donation-app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
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