<template>
  <div class="navbar-container">
    <div class="navbar">
      <div class="logo-section">
        <img src="../assets/Foodbridge.png" alt="Profile" class="logo-image">
      </div>
      <div class="tabs-section">
        <div
          class="nav-tab"
          :class="{ 'active': modelValue === 'overview' }"
          @click="updateTab('overview')"
        >
          Current Listings
        </div>
        <div
          class="nav-tab"
          :class="{ 'active': modelValue === 'listings' }"
          @click="updateTab('listings')"
        >
          Create Listing
        </div>
      </div>
      <div class="logout-section">
        <button class="logout-button" @click="handleLogout">
          Log Out
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  modelValue: {
    type: String,
    required: true
  }
});

const emit = defineEmits(['update:modelValue', 'logout']);

const updateTab = (tab) => {
  emit('update:modelValue', tab);
};

const handleLogout = () => {
  emit('logout');
};
</script>

<style scoped>
.navbar-container {
  width: 100%;
  background-color: #fff;
  border-bottom: 1px solid #f0f0f0;
  padding: 0 1rem;
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

.nav-tab {
  padding: 8px 16px;
  cursor: pointer;
  font-weight: 500;
  color: #888;
  position: relative;
  transition: color 0.2s ease;
}

.nav-tab:hover {
  color: #333;
}

.nav-tab.active {
  color: #333;
  font-weight: 600;
}

.nav-tab.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #333;
}

.logout-section {
  display: flex;
  justify-content: flex-end;
  min-width: 100px;
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
</style>