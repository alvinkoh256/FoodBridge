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
        <ItemDropdown />
        <CreateItem />
        <Button label="Confirm Items" class="confirm-button" severity="success" />
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import CreateItem from "../components/CreateItem.vue";
  import ItemDropdown from "../components/ItemDropdown.vue";
  import Button from "primevue/button";
  import { useStore } from "vuex";
  import { useRouter } from "vue-router";
  
  // Use store and router
  const store = useStore();
  const router = useRouter();
  
  // Sign out function
  const signOut = async () => {
    store.dispatch("logout");
    router.push("/");
  };
  </script>
  
  <style scoped>
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
  