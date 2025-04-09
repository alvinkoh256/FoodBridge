<template>
  <div class="hubs-container">
    <!-- Reserved Hubs Section -->
    <section class="hub-section">
      <h2 class="section-title">Hubs Reserved By You</h2>
      
      <div class="hub-grid">
        <div v-if="reservedHubs.length === 0" class="empty-state">
          No reserved hubs available
        </div>
        
        <div 
          v-for="hub in reservedHubs" 
          :key="hub.hubID" 
          class="hub-card reserved" 
          @click="openDialog(hub, true)"
        >
          <div class="hub-content">
            <span class="hub-name">{{ hub.hubName }}</span>
            <span class="hub-weight">{{ hub.totalWeight_kg }}kg</span>
          </div>
        </div>
      </div>
    </section>
    
    <!-- Unreserved Hubs Section -->
    <section class="hub-section">
      <h2 class="section-title">Hubs Available for Reservation</h2>
      
      <div class="hub-grid">
        <div v-if="filteredUnreservedHubs.length === 0" class="empty-state">
          No hubs available
        </div>
        
        <div 
          v-for="hub in filteredUnreservedHubs"
          :key="hub.hubID" 
          class="hub-card unreserved border-l-4 border-indigo-500" 
          @click="openDialog(hub, false)"
        >
          <div class="hub-content">
            <span class="hub-name">{{ hub.hubName }}</span>
            <span class="hub-weight">{{ hub.totalWeight_kg }}kg</span>
          </div>
        </div>
      </div>
    </section>
    
    <!-- Hub Details Dialog -->
    <Dialog 
      v-model:visible="visible" 
      modal 
      :header="dialogHeader" 
      :style="{ width: '90vw', maxWidth: '600px' }"
      :breakpoints="{ '768px': '95vw' }"
    >
      <DialogContentBank
        :hub="selectedHub"
        :isReserved="isReserved"
        :foodbankId="props.user.id"
        @close="visible = false"
        @update:isReserved="updateHubStatus"
      />
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, defineProps, watch, computed } from 'vue';
import { useStore } from 'vuex';
import DialogContentBank from '../components/DialogContentBank.vue';
import Dialog from 'primevue/dialog';

const store = useStore();
const visible = ref(false);
const dialogHeader = ref('');
const selectedHub = ref(null);
const isReserved = ref(false);
const reservedHubs = ref([]);
const unreservedHubs = ref([]);
const loading = ref(true);

const props = defineProps({
  user: Object
});

const filteredUnreservedHubs = computed(() => {
  return unreservedHubs.value.filter(hub => {
    const weight = parseFloat(hub.totalWeight_kg);
    return !isNaN(weight) && weight > 0;
  });
});

// Function to fetch all hubs data
const fetchHubsData = async () => {
  loading.value = true;

  try {
    // Fetch reserved inventories
    const resHubsResponse = await store.dispatch('apiRequest', {
      method: 'get',
      endpoint: `http://localhost:8000/hub/reservedInventories/${props.user.id}`
    });
    
    // Fetch unreserved hubs data
    const hubsResponse = await store.dispatch('apiRequest', {
      method: 'get',
      endpoint: `http://localhost:8000/hub/hubs-data`
    });

    console.log(hubsResponse);
    
    // Update the data
    reservedHubs.value = resHubsResponse || [];
    
    // Filter out reserved hubs from the unreserved list
    const reservedIds = reservedHubs.value.map(hub => hub.hubID);
    unreservedHubs.value = (hubsResponse || []).filter(
      hub => !reservedIds.includes(hub.hubID)
    );
  } catch (error) {
    console.error('Failed to fetch hubs data:', error);
  } finally {
    loading.value = false;
  }
};

// Watch for userId changes to refetch data
watch(() => props.user, () => {
  if (props.user) {
    fetchHubsData();
  }
}, { immediate: false });

onMounted(() => {
  if (props.user) {
    fetchHubsData();
  }
});

const openDialog = (hub, reservedStatus) => {
  selectedHub.value = hub;
  isReserved.value = reservedStatus;
  dialogHeader.value = `Drop-off at ${hub.hubName}`;
  visible.value = true;
};

const updateHubStatus = async (updatedStatus) => {
  // Update local state
  isReserved.value = updatedStatus;
  
  // Get the hub ID
  const hubId = selectedHub.value.hubID;
  
  if (updatedStatus) {
    const hubToMove = unreservedHubs.value.find(hub => (hub.hubID) === hubId);
    if (hubToMove) {
      reservedHubs.value.push(hubToMove);
      unreservedHubs.value = unreservedHubs.value.filter(hub => (hub.hubID) !== hubId);
    }
  } else {
    const hubToMove = reservedHubs.value.find(hub => (hub.hubID) === hubId);
    if (hubToMove) {
      unreservedHubs.value.push(hubToMove);
      reservedHubs.value = reservedHubs.value.filter(hub => (hub.hubID) !== hubId);
    }
  }
  
  // Close the dialog
  visible.value = false;
};
</script>

<style scoped>
.hubs-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.hub-section {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1.25rem;
  color: #333;
  text-align: left;
}

.hub-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.hub-card {
  padding: 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0,0,0,0.04);
}

.hub-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.08);
}

.hub-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.hub-name {
  font-weight: 500;
}

.hub-weight {
  font-size: 0.9rem;
}

.reserved {
  background-color: #e8f5e9;
  border-left: 4px solid #4CAF50;
  color: #2e7d32;
}

.unreserved {
  background-color: #f5f5f5;
  color: #424242;
}

.empty-state {
  grid-column: 1 / -1;
  padding: 1.5rem;
  background-color: #f9f9f9;
  border-radius: 6px;
  text-align: center;
  color: #757575;
  font-style: italic;
}

@media (max-width: 768px) {
  .hub-grid {
    grid-template-columns: 1fr;
  }
  
  .hub-section {
    padding: 1rem;
  }
}
</style>