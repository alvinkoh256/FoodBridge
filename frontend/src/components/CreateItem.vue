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
            v-model="item.itemName"
            type="text"
            placeholder="Item Name"
            class="w-full"
            @input="updateItems"
          />
        </div>
        <div class="text-left">
          <label for="weight" class="text-black font-bold pl-1">Weight (kg)</label>
          <InputNumber
            v-model="item.itemWeight_kg"
            inputId="minmax-buttons"
            mode="decimal"
            showButtons
            :min="0"
            :max="100"
            class="w-full"
            @input="updateItems"
          />
        </div>
        <div class="text-left">
          <label for="quantity" class="text-black font-bold pl-1">Qty</label>
          <InputNumber
            v-model="item.quantity"
            inputId="minmax-buttons"
            mode="decimal"
            showButtons
            :min="0"
            :max="100"
            class="w-full"
            @input="updateItems"
          />
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
          severity="danger"
          icon="pi pi-plus"
          variant="text"
          raised 
          rounded
          @click="addItem"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import InputNumber from 'primevue/inputnumber';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';

const emit = defineEmits(['new-items-added']);

const inputItems = ref([{
  itemName: '',
  quantity: 0,
  itemWeight_kg: 0
}]);

// Add a new item
const addItem = () => {
  inputItems.value.push({
    id: Date.now(),
    itemName: '',
    quantity: 0,
    itemWeight_kg: 0
  });
  updateItems();
};

// Remove an item by index
const removeItem = (index) => {
  if (inputItems.value.length > 1) {
    inputItems.value.splice(index, 1);
    updateItems();
  }
};

// Update items and emit the changes
const updateItems = () => {
  const validItems = inputItems.value.filter(item => 
    item.itemName && item.quantity > 0
  );
  
  emit('new-items-added', validItems);
};

// Watch for changes in the input items
watch(inputItems, () => {
  updateItems();
  console.log(inputItems.value);
}, { deep: true });
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