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
        @close="visible = false"
      />
    </Dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import DialogContentBank from '../components/DialogContentBank.vue';
import Dialog from 'primevue/dialog';

const visible = ref(false);
const dialogHeader = ref('');
const selectedHub = ref(null);
const isReserved = ref(false);

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
