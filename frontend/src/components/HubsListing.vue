<template>
  <div class="hubs-listing-container">
    <h3 class="font-bold">Reserved Hubs</h3>
    <div class="flex flex-col mb-10 items-center">
      <div v-for="hub in reservedHubs" :key="hub.hubName" class="hub reserved" @click="openDialog(hub, true)">
        {{ hub.hubName }} - {{ hub.totalWeight_kg }}kg
      </div>
    </div>

    <h3 class="font-bold">Unreserved Hubs</h3>
    <div class="flex flex-col mb-10 items-center">
      <div v-for="hub in unreservedHubs" :key="hub.hubName" class="hub unreserved" @click="openDialog(hub, false)">
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
import { ref, onMounted, defineProps } from 'vue';
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

const props = defineProps({
  userId: String
});

onMounted(async () => {
  try {
    // Fetch reserved inventories
    const resHubsResponse = await store.dispatch('apiRequest', { 
      method: 'get', 
      endpoint: `5010/public/hub/${props.userId}/reservedInventories`
    });

    // Fetch hubs data
    const hubsResponse = await store.dispatch('apiRequest', { 
      method: 'get', 
      endpoint: `5010/public/hub/hubsData`
    });

    reservedHubs.value = resHubsResponse?.data || [];
    unreservedHubs.value = hubsResponse?.data || [];

  } catch (error) {
    console.error('Failed to fetch items:', error);
  }
});

const openDialog = (hub, reservedStatus) => {
  selectedHub.value = hub;
  isReserved.value = reservedStatus;
  dialogHeader.value = `Drop-off at ${hub.name}`;
  visible.value = true;
};

const updateHubStatus = (updatedStatus) => {
  isReserved.value = updatedStatus;

  if (updatedStatus) {
    reservedHubs.value.push(selectedHub.value);
    unreservedHubs.value = unreservedHubs.value.filter(hub => hub.name !== selectedHub.value.name);
  } else {
    unreservedHubs.value.push(selectedHub.value);
    reservedHubs.value = reservedHubs.value.filter(hub => hub.name !== selectedHub.value.name);
  }
  
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
}

.hub {
  padding: 10px;
  margin: 10px 0;
  width: 30%;
  border-radius: 8px;
  font-weight: bold;
  text-align: center;
  cursor: pointer;
}

.reserved {
  background-color: #4CAF50;
  color: white;
}

.unreserved {
  background-color: #ddd;
  color: black;
}
</style>
