<template>
  <div class="hubs-listing-container">
    <h3 class="font-bold">Reserved Hubs</h3>
    <div class="flex flex-col mb-10 items-center">
      <div v-for="hub in reservedHubs" :key="hub.name" class="hub reserved" @click="openDialog(hub, true)">
        {{ hub.name }} - {{ hub.weight }}kg
      </div>
    </div>

    <h3 class="font-bold">Unreserved Hubs</h3>
    <div class="flex flex-col mb-10 items-center">
      <div v-for="hub in unreservedHubs" :key="hub.name" class="hub unreserved" @click="openDialog(hub, false)">
        {{ hub.name }} - {{ hub.weight }}kg
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
const reshubs = ref([]);
const hubs = ref([]);

const props = defineProps({
  userId: String
});

const reservedHubs = ref([
  { 
    name: 'Kampong Chai Chee', 
    weight: 110.335,
    address: '123 Victoria Street',
    items: [
      { name: 'Sardines', quantity: 20 },
      { name: 'Beans', quantity: 10 }
    ]
  },
  { name: 'Ah Hood Gardens RN', weight: 65.235 },
  { name: 'Tengah CC', weight: 7.275 },
]);

onMounted(async () => {
  try {
    // Fetch reserved inventories
    const resHubsResponse = await store.dispatch('apiRequest', { 
      method: 'get', 
      endpoint: `/public/hub/${props.userId}/reservedInventories`
    });

    // Fetch hubs data
    const hubsResponse = await store.dispatch('apiRequest', { 
      method: 'get', 
      endpoint: `/public/hub/hubsData`
    });

    reshubs.value = resHubsResponse;
    hubs.value = hubsResponse;

  } catch (error) {
    console.error('Failed to fetch items:', error);
  }
});

const unreservedHubs = ref([
  { name: 'Everspring RN', weight: 54.875 },
  { name: "Chong Pang Zone '8' RC", weight: 22.72 },
]);

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
