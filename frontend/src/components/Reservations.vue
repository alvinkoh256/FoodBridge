<template>
    <div class="reservations-container">
        <div class="title">
            <h2 >Your Reservations</h2>
            <p class="info">Press a hub to mark it as collected.</p>
        </div>
  
      <div class="reservations-list">
        <div 
          v-for="hub in reservedHubs" 
          :key="hub.name" 
          class="reservation-card" 
          :class="{ collected: hub.isCollected }"
          @click="toggleCollected(hub)"
        >
          <div class="hub-info">
            <h3 class="hub-name">{{ hub.name }}</h3>
            <p class="status">
              Status: 
              <span :class="{ uncollected: !hub.isCollected, collectedText: hub.isCollected }">
                {{ hub.isCollected ? 'Collected' : 'Uncollected' }}
              </span>
            </p>
          </div>
        </div>
      </div>
  
      <div class="route-section">
        <p class="route-text">Ready to collect your reservations? Request the best route here!</p>
        <Button label="Show me the best route!" severity="warn"/>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, defineProps } from 'vue';
  import { useStore } from 'vuex';
  import Button from 'primevue/button';
  
  const reservedHubs = ref([
    { name: 'Kampong Chai Chee', isCollected: false },
    { name: 'Ah Hood Gardens RN', isCollected: false },
    { name: 'Tengah CC', isCollected: false },
  ]);

  const resHubs = ref([]);
  const store = useStore();
  
  const props = defineProps({
    userId: String
  });
  
  onMounted(async () => {
    try {
      const reservedHubsResponse = await store.dispatch('apiRequest', { 
        method: 'get', 
        endpoint: `/public/hub/${props.userId}/reservedInventories` 
      });

      resHubs.value = reservedHubsResponse;
    } catch (error) {
      console.error('Failed to fetch reserved hubs:', error);
    }
  });

  const toggleCollected = async (hub) => {
    hub.isCollected = !hub.isCollected;

    try {
      const payload = {
        hubId: hub.name,
        userId: props.userId,
      };

      await store.dispatch('apiRequest', { 
        method: 'post', 
        endpoint: '/public/hub/collectionComplete', 
        data: payload 
      });

      console.log(`Collection status for ${hub.name} updated successfully.`);
    } catch (error) {
      console.error('Failed to update collection status:', error);
      hub.isCollected = !hub.isCollected;
    }
  };
  </script>
  
  <style scoped>
  .reservations-container {
    max-width: 600px;
    margin: auto;
    padding: 20px;
    font-family: Arial, sans-serif;
  }
  
  .title {
    text-align: center;
    font-size: 1.8rem;
    font-weight: bold;
    margin-bottom: 30px;
  }

  .info{
    font-size: 1rem;
    font-weight: normal;
  }
  
  .reservations-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }
  
  .reservation-card {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #fbe3e3;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    transition: background-color 0.3s ease-in-out;
  }
  
  .reservation-card:hover {
    opacity: 0.9;
  }
  
  .collected {
    background-color: #d4edda !important; 
  }
  
  .hub-info {
    flex-grow: 1;
  }
  
  .hub-name {
    font-size: 1.2rem;
    font-weight: bold;
    margin: 0;
  }
  
  .status {
    font-size: 0.9rem;
    color: #555;
  }
  
  .uncollected {
    font-weight: bold;
    color: red;
  }
  
  .collectedText {
    font-weight: bold;
    color: green;
  }
  
  .route-section {
    text-align: center;
    margin-top: 30px;
  }
  
  .route-text {
    font-size: 1rem;
    font-weight: bold;
    margin-bottom: 15px;
  }
  
  .route-button {
    background-color: #4caf50;
    color: white;
    padding: 12px 20px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: bold;
  }
  
  .route-button:hover {
    background-color: #388e3c;
  }
  </style>
  