<template>
    <div class="mt-6 p-6">
      <h3 class="text-xl font-bold mb-4 text-center">Can't find an item? Add it below!</h3>
      <div>
        <div 
            v-for="(item, index) in inputItems" 
            :key="item.id" 
            class="card flex justify-content-center items-center space-x-4"
        >
            <div class="text-left">
              <label for="item" class="text-black font-bold pl-1">Item</label>
              <InputText
                  v-model="value2"
                  type="text"
                  placeholder="Create Item"
              fluid />
            </div>

            <div class="text-left">
                <label for="weight" class="text-black font-bold pl-1">Weight</label>
                <InputNumber 
                v-model="value2"
                id="quantity"
                inputId="minmax-buttons" 
                mode="decimal" showButtons
                :min="0" :max="100" 
                fluid />
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
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  import InputNumber from 'primevue/inputnumber';
  import InputText from 'primevue/inputtext';
  import Button from 'primevue/button';
  
  // Emits to communicate with parent component
  const emit = defineEmits(['item-added']);
  
  // State for new item input
  const newItemName = ref('');
  const newItemDescription = ref('');
  
  // Track recently added items
  const inputItems = ref([
    { 
      id: Date.now(), 
      selectedItem: null, 
      value: null 
    }
  ]);
  
    // Method to add a new input item
    const addItem = () => {
        inputItems.value.push({
        id: Date.now(), 
        selectedItem: newItemName,
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