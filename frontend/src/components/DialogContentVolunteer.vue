<template>
  <div class="drop-off-details-container">
    <div class="drop-off-image-container">
      <img src="../assets/logo.jpg" alt="Drop-off items" class="drop-off-image">
    </div>
    <div class="drop-off-info-panel">
      <h2 class="section-header">Details</h2>
      <div class="donation-items">
        <div v-for="(item, index) in dropOffData.items" :key="index" class="donation-item">
          <div class="item-name text-black">{{ item.name }}</div>
          <div class="item-quantity text-black">x{{ item.quantity }}</div>
        </div>
        
        <div class="donation-notes">
          I wanna die !!
        </div>
      </div>
    </div>
  </div>
  <div class="action-button-container">
    <Button label="Accept" class="p-button-rounded w-full" severity="success" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import Button from 'primevue/button';
const props = defineProps({
  visible: {
    type: Boolean,
    required: true
  },
  dropOffData: {
    type: Object,
    default: () => ({
      id: '',
      location: 'A CC',
      fullAddress: 'Actual address w/ Postal & det',
      imageUrl: '../assets/placeholder.jpg',
      items: [
        { name: 'Sardines', quantity: 20 },
        { name: 'Beans', quantity: 10 }
      ]
    })
  }
});
</script>

<style scoped>
.drop-off-details-container {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

@media (max-width: 768px) {
  .drop-off-details-container {
    flex-direction: column;
  }
}

.drop-off-image-container {
  flex: 1;
  min-width: 0;
}

.drop-off-image {
  width: 100%;
  height: auto;
  object-fit: cover;
  border-radius: 8px;
  max-height: 400px;
}

.drop-off-info-panel {
  flex: 1;
  background-color: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.section-header {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #333;
}

.donation-items {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.donation-item {
  display: flex;
  justify-content: space-between;
  font-size: 1rem;
}

.item-name {
  font-weight: 500;
}

.item-quantity {
  color: #555;
}

.donation-notes {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
  color: #666;
  font-size: 0.9rem;
  line-height: 1.5;
}

.action-button-container {
  display: flex;
  justify-content: center;
  margin: auto;
  width: 20%;
}
</style>