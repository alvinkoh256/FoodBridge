<template>
  <div class="p-4 md:p-6 rounded-lg">
    <h3 class="text-xl font-bold mb-6 text-center text-gray-800 block">Can't find an item? Add it below!</h3>
    <div>
      <div
        v-for="(item, index) in inputItems"
        :key="index"
        class="card flex flex-wrap md:flex-nowrap justify-center items-center gap-4 transition-all"
      >
        <div class="text-left w-full md:w-auto">
          <label for="item" class="text-gray-700 font-medium text-sm uppercase tracking-wider block mb-2">Item</label>
          <InputText
            v-model="item.itemName"
            type="text"
            placeholder="Item Name"
            class="w-full focus:border-indigo-500 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
            @input="updateItems"
          />
        </div>
        <div class="text-left w-full md:w-auto" v-if="showWeight">
          <label for="weight" class="text-gray-700 font-medium text-sm uppercase tracking-wider block mb-2">Weight (kg)</label>
          <InputNumber
            v-model="item.itemWeight_kg"
            mode="decimal"
            showButtons
            :min="0"
            :max="100"
            class="w-full input-number-styled"
            @input="updateItems"
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
            @input="updateItems"
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
  </div>
</template>

<script setup>
import { ref, watch, defineProps } from 'vue';
import InputNumber from 'primevue/inputnumber';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';

const emit = defineEmits(['new-items-added']);

const props = defineProps({
  showWeight: {
    type: Boolean,
    default: true
  }
});

const inputItems = ref([{
  itemName: '',
  quantity: 0,
  itemWeight_kg: 0
}]);

const addItem = () => {
  inputItems.value.push({
    id: Date.now(),
    itemName: '',
    quantity: 0,
    itemWeight_kg: 0
  });
  updateItems();
};

const removeItem = (index) => {
  if (inputItems.value.length > 1) {
    inputItems.value.splice(index, 1);
    updateItems();
  }
};

const updateItems = () => {
  const validItems = inputItems.value.filter(item => 
    item.itemName && item.quantity > 0
  );
  
  emit('new-items-added', validItems);
};

watch(inputItems, () => {
  updateItems();
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

:deep(.p-inputtext:focus) {
  border-color: #6366f1;
  box-shadow: 0 0 0 1px #6366f1;
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