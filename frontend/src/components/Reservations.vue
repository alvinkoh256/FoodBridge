<template>
  <div class="reservations-view">
    <div class="header">
      <h2 class="main-title">Your Reservations</h2>
      <p class="subtitle">Press a hub to mark it as collected</p>
    </div>

    <!-- Reservations List -->
    <div class="cards-container">
      <div 
        v-for="hub in reservedHubs" 
        :key="hub.hubId || hub.name" 
        class="reservation" 
        @click="openDialog(hub)"
        :class="{ 'is-collected': hub.isCollected }"
      >
        <div class="reservation-content">
          <h3 class="reservation-title">{{ hub.hubName }}</h3>
          <div class="status-badge" :class="hub.isCollected ? 'status-collected' : 'status-pending'">
            {{ hub.isCollected ? 'Collected' : 'Uncollected' }}
          </div>
        </div>
      </div>
      
      <div v-if="reservedHubs.length === 0" class="no-data">
        <p>You don't have any reservations yet.</p>
      </div>
    </div>

    <!-- Route Request Section -->
    <div class="route-container">
      <p class="route-caption">Ready to collect your reservations?</p>
      <Button 
        label="Show me the best route" 
        
        @click="showRoute" 
        severity="warning" 
        class="route-button"
      />
    </div>

    <!-- Collection Confirmation Dialog -->
    <Dialog 
      v-model:visible="visible" 
      :style="{ width: '90vw', maxWidth: '500px' }"
      :breakpoints="{ '768px': '95vw' }"
      header="Confirm Collection"
    >
      <div class="dialog-content">
        <p class="dialog-message">Are you sure you want to mark this hub as collected?</p>
        <div class="dialog-actions">
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
import { ref, onMounted, defineProps, computed } from 'vue';
import { useStore } from 'vuex';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';

const reservedHubs = ref([]);
const store = useStore();
const visible = ref(false);
const loading = ref(false);
const selectedHub = ref(null);

const disableButton = computed(() => {
  if (reservedHubs.value.length > 0) return true;

  // Check if there is at least one uncollected hub
  const hasUncollectedHub = reservedHubs.value.some(hub => !hub.isCollected);

  return !hasUncollectedHub;
});

const props = defineProps({
  userId: String
});

const fetchReservedHubs = async () => {
  try {
    const reservedHubsResponse = await store.dispatch('apiRequest', { 
      method: 'get', 
      endpoint: `http://localhost:8000/hub/reservedInventories/${props.userId}` 
    });
    reservedHubs.value = reservedHubsResponse || [];
    
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
      hubID: selectedHub.value.hubID,
      foodbankID: props.userId,
    };

    await store.dispatch('apiRequest', { 
      method: 'post', 
      endpoint: 'http://localhost:8000/hub/collection-complete', 
      data: payload 
    });

    // Update local state
    const hubIndex = reservedHubs.value.findIndex(
      hub => (hub.hubID || hub.name) === (selectedHub.value.hubID || selectedHub.value.name)
    );
    
    if (hubIndex !== -1) {
      reservedHubs.value[hubIndex].isCollected = true;
    }
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
      endpoint: `http://localhost:8000/get-optimal-route/${props.userId}`
    });
    
    // Open route link on new tab
    console.log(response);
    window.open(response.googleMapsLink);
  } catch (error) {
    console.error('Failed to fetch optimal route:', error);
  }
};
</script>

<style scoped>
.reservations-view {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.header {
  text-align: center;
  margin-bottom: 0.5rem;
}

.main-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #333;
}

.subtitle {
  font-size: 0.9rem;
  color: #666;
}

.cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.reservation {
  background-color: white;
  border-radius: 8px;
  padding: 1.25rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  transition: all 0.2s ease;
  cursor: pointer;
  border-left: 4px solid #ff5252;
}

.reservation:hover:not(.is-collected) {
  transform: translateY(-2px);
  box-shadow: 0 3px 6px rgba(0,0,0,0.12);
}

.is-collected {
  border-left-color: #4caf50;
  cursor: default;
}

.reservation-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.reservation-title {
  font-size: 1.1rem;
  font-weight: 500;
  margin: 0;
  color: #333;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-pending {
  background-color: #ffebee;
  color: #c62828;
}

.status-collected {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.no-data {
  grid-column: 1 / -1;
  padding: 2rem;
  text-align: center;
  background-color: #f9f9f9;
  border-radius: 8px;
  color: #757575;
}

.route-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

.route-caption {
  font-weight: 500;
  color: #333;
}

.route-button {
  min-width: 200px;
}

.dialog-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem 0;
}

.dialog-message {
  margin-bottom: 1.5rem;
  font-size: 1rem;
}

.dialog-actions {
  display: flex;
  gap: 1rem;
}

@media (max-width: 768px) {
  .cards-container {
    grid-template-columns: 1fr;
  }
  
  .route-container {
    padding: 1rem;
  }
  
  .dialog-actions {
    flex-direction: column;
    gap: 0.75rem;
    width: 100%;
  }
  
  .dialog-actions button {
    width: 100%;
  }
}
</style>