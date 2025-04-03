<template>
    <div >
      <div 
        v-for="(item, index) in inputItems" 
        :key="item.id" 
        class="card flex justify-content-center items-center space-x-4"
      >
        <div class="text-left">
          <label for="item" class="text-black font-bold pl-1">Item</label>
          <Dropdown 
            v-model="item.selectedItem" 
            id="item"
            :options="itemOptions" 
            optionLabel="name" 
            optionValue="code"
            placeholder="Select an Item" 
            class="w-full md:w-14rem"
          />
        </div>

        <div class="text-left">
          <label for="quantity" class="text-black font-bold pl-1">Qty</label>
          <InputNumber 
            v-model="value2"
            id="quantity"
            inputId="minmax-buttons" 
            mode="decimal" showButtons
            :min="0" :max="100" 
          fluid />
        </div>

        <Button 
          icon="pi pi-trash" 
          severity="danger" 
          text 
          @click="removeItem(index)"
          v-if="inputItems.length > 1"
        />
      </div>
      
      <div class="flex justify-center mt-4 mb-4">
        <Button 
          label="Add More" 
          severity="warn"
          icon="pi pi-plus" 
          @click="addItem"
        />
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  import { useStore } from 'vuex';
  import Dropdown from 'primevue/dropdown';
  import InputNumber from 'primevue/inputnumber';
  import Button from 'primevue/button';

  const store = useStore();
  const items = ref([]);
  
  const inputItems = ref([
    { 
      id: Date.now(), 
      selectedItem: null, 
      value: null 
    }
  ]);

  onMounted(async () => {
    try {
      const response = await store.dispatch('apiRequest', { 
        method: 'get', 
        endpoint: 'http://localhost:5010/public/hub/existingItems' 
      });
      items.value = response; 
      console.log(items.value);
    } catch (error) {
      console.error('Failed to fetch items:', error);
    }
  });
  
  const itemOptions = ref([
    { name: 'Clothing', code: 'CLT' },
    { name: 'Books', code: 'BKS' },
    { name: 'Electronics', code: 'ELEC' },
    { name: 'Furniture', code: 'FURN' },
    { name: 'Toys', code: 'TOYS' },
    { name: 'Kitchen Items', code: 'KTCH' },
    { name: 'Sports Equipment', code: 'SPRT' },
    { name: 'Stationery', code: 'STAT' }
  ]);
  
  // Method to add a new input item
  const addItem = () => {
    inputItems.value.push({
      id: Date.now(), // Unique identifier
      selectedItem: null,
      value: null
    });
  };
  
  // Method to remove an item
  const removeItem = (index) => {
    if (inputItems.value.length > 1) {
      inputItems.value.splice(index, 1);
    }
  };
  </script>
  
  <style scoped>

  </style>
  