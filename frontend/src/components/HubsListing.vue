<template>
  <div class="hubs-listing-container">
    <h3 class="font-bold">Reserved Hubs</h3>
    <div class="flex flex-col mb-10 items-center">
      <div v-if="reservedHubs.length === 0" class="empty-state">
        No reserved hubs at the moment
      </div>
      <div 
        v-for="hub in reservedHubs" 
        :key="hub.hubId || hub.id" 
        class="hub reserved" 
        @click="openDialog(hub, true)"
      >
        {{ hub.hubName }} - {{ hub.totalWeight_kg }}kg
      </div>
    </div>
    
    <h3 class="font-bold">Unreserved Hubs</h3>
    <div class="flex flex-col mb-10 items-center">
      <div v-if="unreservedHubs.length === 0" class="empty-state">
        No unreserved hubs available
      </div>
      <div 
        v-for="hub in unreservedHubs" 
        :key="hub.hubId || hub.id" 
        class="hub unreserved" 
        @click="openDialog(hub, false)"
      >
        {{ hub.hubName }} - {{ hub.totalWeight_kg }}kg
      </div>
    </div>
    
    <!-- Drop-off Dialog -->
    <Dialog v-model:visible="visible" modal :header="dialogHeader" :style="{ width: '50rem' }">
      <DialogContentBank
        :hub="selectedHub"
        :isReserved="isReserved"
        :foodbankId="props.userId"
        @close="visible = false"
        @update:isReserved="updateHubStatus"
      />
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, defineProps, watch } from 'vue';
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
  userId: String
});

// Function to fetch all hubs data
const fetchHubsData = async () => {
  loading.value = true;
  
  try {
    // Fetch reserved inventories
    const resHubsResponse = await store.dispatch('apiRequest', {
      method: 'get',
      endpoint: `5010/public/hub/${props.userId}/reservedInventories`
    });
    
    // Fetch unreserved hubs data
    const hubsResponse = await store.dispatch('apiRequest', {
      method: 'get',
      endpoint: `5010/public/hub/hubsData`
    });
    
    // Update the data
    reservedHubs.value = resHubsResponse?.data || [];
    
    // Filter out reserved hubs from the unreserved list
    const reservedIds = reservedHubs.value.map(hub => hub.hubId || hub.id);
    unreservedHubs.value = (hubsResponse?.data || []).filter(
      hub => !reservedIds.includes(hub.hubId || hub.id)
    );
  } catch (error) {
    console.error('Failed to fetch hubs data:', error);
  } finally {
    loading.value = false;
  }
};

// Watch for userId changes to refetch data
watch(() => props.userId, () => {
  if (props.userId) {
    fetchHubsData();
  }
}, { immediate: false });

onMounted(() => {
  if (props.userId) {
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
  const hubId = selectedHub.value.hubId || selectedHub.value.id;
  
  if (updatedStatus) {
    const hubToMove = unreservedHubs.value.find(hub => (hub.hubId || hub.id) === hubId);
    if (hubToMove) {
      reservedHubs.value.push(hubToMove);
      unreservedHubs.value = unreservedHubs.value.filter(hub => (hub.hubId || hub.id) !== hubId);
    }
  } else {
    const hubToMove = reservedHubs.value.find(hub => (hub.hubId || hub.id) === hubId);
    if (hubToMove) {
      unreservedHubs.value.push(hubToMove);
      reservedHubs.value = reservedHubs.value.filter(hub => (hub.hubId || hub.id) !== hubId);
    }
  }
  
  // Close the dialog
  visible.value = false;

};
</script>

<style scoped>
.hubs-listing-container {
  padding: 20px;
  font-family: Arial, sans-serif;
}

h3 {
  text-align: center;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
}

.hub {
  padding: 10px;
  margin: 10px 0;
  width: 30%;
  border-radius: 8px;
  font-weight: bold;
  text-align: center;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.hub:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.reserved {
  background-color: #4CAF50;
  color: white;
}

.unreserved {
  background-color: #ddd;
  color: black;
}

.empty-state {
  padding: 15px;
  color: #666;
  text-align: center;
  font-style: italic;
}
</style>