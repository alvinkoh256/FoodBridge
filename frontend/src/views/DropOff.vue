<template>
  <div class="header">
    <div class="navbar">
      <div class="logo-section">
        <img src="../assets/Foodbridge.png" alt="Profile" class="logo-image" />
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
    <div class="container">
      <div class="title">What have you delivered ?</div>
      <ItemDropdown @items-selected="updateSelectedItems" />
      <CreateItem @new-items-added="updateNewItems" />
      <Button 
        label="Confirm Items" 
        class="confirm-button" 
        severity="warn" 
        @click="confirmDropOff" 
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, inject } from 'vue';
import CreateItem from "../components/CreateItem.vue";
import ItemDropdown from "../components/ItemDropdown.vue";
import Button from "primevue/button";
import { useStore } from "vuex";
import { useRouter } from "vue-router";

// Use store and router
const store = useStore();
const router = useRouter();
const supabase = inject('supabase');

// Create refs to store selected items and new items
const selectedItems = ref([]);
const newCreatedItems = ref([]);
const user = ref(null);

//Retrieve selected product
const product = computed(() => JSON.parse(localStorage.getItem('savedProduct')));

onMounted(async () => {
  await checkAuth();
});

const checkAuth = async () => {
  // First check the current session
  const { data: { session }, error } = await supabase.auth.getSession();
  if (error) {
    console.error("Error checking session:", error);
    router.push("/");
    return;
  }
  
  if (session?.user && session.user?.user_metadata?.role === "V") {
    user.value = session.user;
    console.log("User authenticated:", user.value);
  } else {
    user.value = null;
    router.push("/");
  }
  
  // Then set up the listener for future changes
  const { data: authListener } = supabase.auth.onAuthStateChange((event, session) => {
    if (session?.user && session.user?.user_metadata?.role === "V") {
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

// Update functions to receive data from child components
const updateSelectedItems = (items) => {
  selectedItems.value = items;
  console.log('Selected items updated:', items);
};

const updateNewItems = (items) => {
  newCreatedItems.value = items;
  console.log('New items updated:', items);
};

// Sign out function
const signOut = async () => {
  store.dispatch("logout");
  router.push("/");
};

// Function to confirm drop-off
const confirmDropOff = async () => {
  try {
    // Get user information from store or use fallback
    const volunteerID = user.value.id
    const productID = product.productId;
    
    // Format the payload according to the expected API structure
    const payload = {
      volunteerID,
      productID,
      items: selectedItems.value || [],
      newItems: newCreatedItems.value || [] // Note: Changed from 'newitems' to 'newItems'
    };
    
    console.log("Sending payload:", payload);
    
    const response = await store.dispatch('apiRequest', {
      method: 'post',
      endpoint: 'http://localhost:5009/confirmDelivery/drop-off',
      data: payload
    });
    
    console.log('Drop-off confirmed:', response);
    
  } catch (error) {
    console.error('Failed to confirm drop-off:', error);
  }
};
</script>

<style scoped>
.header {
  width: 100%;
  height: 100%;
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
  margin-bottom: 10px;
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
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  width: 100%;
  border-radius: 6px;
  margin: auto;
}
.confirm-button {
  width: 100%;
  max-width: 300px;
  border-radius: 12px;
  padding: 10px;
  font-size: 1rem;
}

.title {
  text-align: left;
  padding-top: 10px;
  font-weight: bold;
  font-size: 30px;
  color: black;
}
</style>