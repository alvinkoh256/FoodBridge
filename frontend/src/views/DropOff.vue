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
      <ItemDropdown @items-selected="updateSelectedItems" />
      <CreateItem @new-items-added="updateNewItems" />
      <Button 
        label="Confirm Items" 
        class="confirm-button" 
        severity="success" 
        @click="confirmDropOff" 
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import CreateItem from "../components/CreateItem.vue";
import ItemDropdown from "../components/ItemDropdown.vue";
import Button from "primevue/button";
import { useStore } from "vuex";
import { useRouter } from "vue-router";

// Use store and router
const store = useStore();
const router = useRouter();

// Create refs to store selected items and new items
const selectedItems = ref([]);
const newCreatedItems = ref([]);

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
    const user = store.state.user || {};
    const volunteerID = user?.user_metadata?.uid || "123"; // fallback to "123" for testing
    const productID = "100"; // You might want to get this from somewhere else
    
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
    // You could add a success notification here
    
  } catch (error) {
    console.error('Failed to confirm drop-off:', error);
    // You could add an error notification here
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
</style>