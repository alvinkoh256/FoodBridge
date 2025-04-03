<template>
  <div>
    <div
      v-for="(item, index) in inputItems"
      :key="item.id"
      class="card flex justify-content-center items-center space-x-4"
    >
      <div class="text-left">
        <label for="item" class="text-black font-bold pl-1">Item</label>
        <Dropdown
          v-model="item.selectedItem"
          :id="`item-${index}`"
          :options="foodItems"
          optionLabel="itemName"
          optionValue="itemID"
          placeholder="Select a Food Item"
          class="w-full md:w-14rem"
        />
      </div>
      <div class="text-left">
        <label for="quantity" class="text-black font-bold pl-1">Qty</label>
        <InputNumber
          v-model="item.quantity"
          :id="`quantity-${index}`"
          inputId="minmax-buttons"
          mode="decimal"
          showButtons
          :min="0"
          :max="100"
        fluid/>
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
        severity="warning"
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
const foodItems = ref([]);
const inputItems = ref([
  {
    id: Date.now(),
    selectedItem: null,
    quantity: 0
  }
]);

onMounted(async () => {
  try {
    const response = await store.dispatch('apiRequest', {
      method: 'get',
      endpoint: 'http://localhost:5010/public/hub/existingItems'
    });
    
    foodItems.value = response.items || [];
    console.log('Food items loaded:', foodItems.value);
  } catch (error) {
    console.error('Failed to fetch items:', error);
  }
});

// Method to add a new input item
const addItem = () => {
  inputItems.value.push({
    id: Date.now(),
    selectedItem: null,
    quantity: 0
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
.card {
  margin-bottom: 1rem;
  padding: 1rem;
  border-radius: 0.5rem;
}

.flex {
  display: flex;
}

.justify-content-center {
  justify-content: center;
}

.items-center {
  align-items: center;
}

.space-x-4 > * + * {
  margin-left: 1rem;
}

.text-left {
  text-align: left;
}

.justify-center {
  justify-content: center;
}

.mt-4 {
  margin-top: 1rem;
}

.mb-4 {
  margin-bottom: 1rem;
}
</style>