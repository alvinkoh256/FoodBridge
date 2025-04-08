<template>
  <div>
    <div
      v-for="(item, index) in inputItems"
      :key="index"
      class="card flex flex-wrap md:flex-nowrap justify-center items-center gap-4 transition-all"
    >
      <div class="text-left w-full md:w-auto">
        <label for="item" class="text-gray-700 font-medium text-sm uppercase tracking-wider block mb-2">Item</label>
        <Dropdown
          v-model="item.selectedItem"
          :options="foodItems"
          optionLabel="itemName"
          placeholder="Select a Food Item"
          class="w-full dropdown-styled"
          @change="updateSelection"
          editable
        />
      </div>
      <div class="text-left w-full md:w-auto">
        <label for="quantity" class="text-gray-700 font-medium text-sm uppercase tracking-wider block mb-2">Qty</label>
        <InputNumber
          v-model="item.quantity"
          mode="decimal"
          showButtons
          :min="0"
          :max="100"
          class="w-full input-number-styled"
          @input="updateSelection"
        />
      </div>
      <Button
        icon="pi pi-trash"
        severity="danger"
        text
        @click="removeItem(index)"
        v-if="inputItems.length > 1"
        class="self-end mb-1 hover:bg-red-50 rounded-full p-2 transition-colors"
      />
    </div>
    <div class="flex justify-center mt-6 mb-2">
      <Button
        severity="danger"
        icon="pi pi-plus"
        variant="text"
        raised
        rounded
        @click="addItem"
        class="add-button transition-transform hover:scale-110"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useStore } from 'vuex';
import Dropdown from 'primevue/dropdown';
import InputNumber from 'primevue/inputnumber';
import Button from 'primevue/button';

const emit = defineEmits(['items-selected']);
const store = useStore();
const foodItems = ref([]);
const inputItems = ref([{
  selectedItem: null,
  quantity: 0
}]);

onMounted(async () => {
  try {
    const response = await store.dispatch('apiRequest', {
      method: 'get',
      endpoint: 'http://localhost:8000/hub/existing-items'
    });
    foodItems.value = response.items || [];
  } catch (error) {
    console.error('Failed to fetch items:', error);
  }
});

const addItem = () => {
  inputItems.value.push({
    id: Date.now(),
    selectedItem: null,
    quantity: 0
  });
  updateSelection();
};

const removeItem = (index) => {
  if (inputItems.value.length > 1) {
    inputItems.value.splice(index, 1);
    updateSelection();
  }
};

const updateSelection = () => {
  const validItems = inputItems.value.filter(item =>
    item.selectedItem && item.quantity > 0
  ).map(item => ({
    itemName: item.selectedItem.itemName,
    quantity: item.quantity
  }));
  
  emit('items-selected', validItems);
};

watch(inputItems, () => {
  updateSelection();
}, { deep: true });
</script>

<style scoped>
.card {
  margin-bottom: 1.5rem;
  padding: 1.5rem;
  border-radius: 0.75rem;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  background-color: white;
  transition: all 0.2s ease;
}

.card:hover {
  box-shadow: 0 10px 15px rgba(0,0,0,0.05);
  transform: translateY(-2px);
}

:deep(.p-dropdown) {
  border-radius: 0.5rem;
  transition: all 0.2s ease;
  width: 100%;
}

:deep(.p-dropdown:focus) {
  border-color: #6366f1;
  box-shadow: 0 0 0 1px #6366f1;
}

:deep(.p-dropdown-panel) {
  border-radius: 0.5rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

:deep(.p-dropdown-panel .p-dropdown-items .p-dropdown-item.p-highlight) {
  background-color: #EEF2FF;
  color: #4F46E5;
}

:deep(.p-inputtext) {
  border-radius: 0.5rem;
  transition: all 0.2s ease;
}

:deep(.p-inputnumber-buttons-stacked .p-button.p-inputnumber-button-up) {
  border-top-right-radius: 0.5rem;
}

:deep(.p-inputnumber-buttons-stacked .p-button.p-inputnumber-button-down) {
  border-bottom-right-radius: 0.5rem;
}

:deep(.p-button) {
  transition: background-color 0.2s ease, transform 0.2s ease;
}

:deep(.p-button-danger) {
  color: #ef4444;
}

:deep(.p-button-danger:hover) {
  color: #b91c1c;
}

.add-button:deep(.p-button) {
  background-color: #6366f1;
  width: 3rem;
  height: 3rem;
  border-radius: 9999px;
}

.add-button:deep(.p-button:hover) {
  background-color: #4f46e5;
}
</style>