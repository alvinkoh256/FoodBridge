<template>
  <div class="reservations-container">
    <div class="title">
      <h2>Your Reservations</h2>
      <p class="info">Press a hub to mark it as collected.</p>
    </div>

    <div class="reservations-list">
      <div 
        v-for="hub in reservedHubs" 
        :key="hub.hubId || hub.name" 
        class="reservation-card" 
        @click="openDialog(hub)"
        :class="{ 'collected': hub.isCollected }"
      >
        <div class="hub-info">
          <h3 class="hub-name">{{ hub.hubName }}</h3>
          <p class="status">
            Status: 
            <span :class="{ uncollected: !hub.isCollected, collectedText: hub.isCollected }">
              {{ hub.isCollected ? 'Collected' : 'Uncollected' }}
            </span>
          </p>
        </div>
      </div>
      
      <div v-if="reservedHubs.length === 0" class="no-reservations">
        You don't have any reservations yet.
      </div>
    </div>

    <div class="route-section">
      <p class="route-text">Ready to collect your reservations? Request the best route here!</p>
      <Button label="Show me the best route!" @click="showRoute" severity="warn"/>
    </div>

    <Dialog v-model:visible="visible" :style="{ width: '50rem' }" header="Confirm Collection">
      <div class="confirmation-dialog">
        <p class="confirmation-message">Are you sure you want to mark this hub as collected?</p>
        <div class="confirmation-buttons">
          <Button 
            label="Yes" 
            class="p-button-rounded" 
            severity="success" 
            @click="confirmCollection" 
            :loading="loading"
          />
          <Button 
            label="No" 
            class="p-button-rounded" 
            severity="danger" 
            @click="closeDialog"
          />
        </div>
      </div>
    </Dialog>

  </div>
</template>

<script setup>
import { ref, onMounted, defineProps } from 'vue';
import { useStore } from 'vuex';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';

const reservedHubs = ref([]);
const store = useStore();
const visible = ref(false);
const loading = ref(false);
const selectedHub = ref(null);

const props = defineProps({
  userId: String
});

const fetchReservedHubs = async () => {
  try {
    const reservedHubsResponse = await store.dispatch('apiRequest', { 
      method: 'get', 
      endpoint: `5010/public/hub/${props.userId}/reservedInventories` 
    });

    reservedHubs.value = reservedHubsResponse.data || [];
    
    // Initialize isCollected property if not present
    reservedHubs.value.forEach(hub => {
      if (hub.isCollected === undefined) {
        hub.isCollected = false;
      }
    });
  } catch (error) {
    console.error('Failed to fetch reserved hubs:', error);
  }
};

onMounted(() => {
  if (props.userId) {
    fetchReservedHubs();
  }
});

const openDialog = (hub) => {
  if (hub.isCollected) {
    return; // Don't open dialog if already collected
  }
  selectedHub.value = hub;
  visible.value = true;
};

const closeDialog = () => {
  visible.value = false;
  selectedHub.value = null;
};

const confirmCollection = async () => {
  if (!selectedHub.value) return;
  
  loading.value = true;
  
  try {
    const payload = {
      hubId: selectedHub.value.hubId || selectedHub.value.name,
      foodbankId: props.userId,
    };

    await store.dispatch('apiRequest', { 
      method: 'post', 
      endpoint: '5010/public/hub/collectionComplete', 
      data: payload 
    });

    // Update local state
    const hubIndex = reservedHubs.value.findIndex(
      hub => (hub.hubId || hub.name) === (selectedHub.value.hubId || selectedHub.value.name)
    );
    
    if (hubIndex !== -1) {
      reservedHubs.value[hubIndex].isCollected = true;
    }

    console.log(`Collection status for ${selectedHub.value.hubName} updated successfully.`);
  } catch (error) {
    console.error('Failed to update collection status:', error);
  } finally {
    loading.value = false;
    closeDialog();
  }
};

const showRoute = async () => {
    try {
      // Call the API to get the optimal route
      const response = await store.dispatch('apiRequest', {
        method: 'get',
        endpoint: `5016/getOptimalRoute/${props.userId}/getRoute`
      });
      
      window.open(response.data);

    } catch (error) {
      console.error('Failed to fetch optimal route:', error);
    }
  }
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
  margin-bottom: 30px;
}

.title h2 {
  font-size: 1.8rem;
  font-weight: bold;
  margin-bottom: 10px;
}

.info {
  font-size: 1rem;
  font-weight: normal;
  color: #666;
}

.reservations-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 30px;
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
  transition: all 0.3s ease-in-out;
  font-weight: bold;
  color: red;
}

.reservation-card:hover:not(.collected) {
  opacity: 0.9;
  background-color: #d4edda !important;
  font-weight: bold;
  color: green;
}

.collected {
  background-color: #d4edda;
  color: green;
  cursor: default;
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
  margin-top: 5px;
}

.uncollected {
  color: #dc3545;
  font-weight: bold;
}

.collectedText {
  color: #28a745;
  font-weight: bold;
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

.no-reservations {
  text-align: center;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  color: #6c757d;
  font-style: italic;
}

.confirmation-dialog {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px;
}

.confirmation-message {
  font-size: 1.1rem;
  margin-bottom: 20px;
  text-align: center;
}

.confirmation-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
}
</style>