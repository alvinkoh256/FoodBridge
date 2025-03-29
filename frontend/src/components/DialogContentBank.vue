<template>
  <div>
    <div class="drop-off-info">
      <p class="address"><strong>Address:</strong> {{ hub.address }}</p>
      <p class="weight"><strong>Weight:</strong> {{ hub.weight }} kg</p>
    </div>

    <div class="drop-off-info-panel">
      <h2 class="section-header">Items</h2>
      <div class="donation-items">
        <div v-for="(item, index) in hub.items" :key="index" class="donation-item">
          <span class="item-name">{{ item.name }}</span>
          <span class="item-quantity">x{{ item.quantity }}</span>
        </div>
      </div>

      <div class="donation-notes">
        <p>No additional notes.</p>
      </div>
    </div>
  </div>

  <div class="action-button-container gap-10">
    <Button 
      label="Reserve" 
      class="p-button-rounded w-full" 
      severity="warn" 
      :disabled="isReserved"
      @click="$emit('close')"
    />
    <Button 
      label="Unreserve" 
      class="p-button-rounded w-full" 
      severity="danger" 
      :disabled="!isReserved"
      @click="$emit('close')"
    />
  </div>
</template>

<script setup>
import { defineProps } from 'vue';
import Button from 'primevue/button';

const props = defineProps({
  hub: {
    type: Object,
    required: true
  },
  isReserved: {
    type: Boolean,
    required: true
  }
});
</script>

<style scoped>
/* Section Headers */
.section-header {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #2c3e50;
}

/* Drop-off Info */
.drop-off-info {
  text-align: center;
}

.address, .weight {
  font-size: 1rem;
  font-weight: 500;
  color: #444;
  margin-bottom: 0.5rem;
}

/* Donation Items */
.donation-items {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.donation-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 6px;
  font-size: 1rem;
}

.item-name {
  font-weight: 600;
  color: #333;
}

.item-quantity {
  font-weight: 500;
  color: #555;
}

/* Notes Section */
.donation-notes {
  margin-top: 1rem;
  padding: 1rem;
  border-top: 1px solid #ddd;
  font-size: 0.9rem;
  color: #666;
  background: #fcfcfc;
  border-radius: 6px;
}

/* Button Container */
.action-button-container {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
}
</style>
