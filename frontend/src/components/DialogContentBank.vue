<template>
  <div>
    <div class="drop-off-info">
      <p class="address"><strong>Address:</strong> {{ hub.hubAddress }}</p>
      <p class="weight"><strong>Weight:</strong> {{ hub.totalWeight_kg }} kg</p>
    </div>
    <div class="drop-off-info-panel">
      <h2 class="section-header">Items</h2>
      <div class="donation-items">
        <div v-for="(item, index) in hub.reservedItems || hub.items || []" :key="index" class="donation-item">
          <span class="item-name">{{ item.itemName }}</span>
          <span class="item-quantity">x{{ item.quantity }}</span>
        </div>
        <div v-if="(!hub.reservedItems || hub.reservedItems.length === 0) && (!hub.items || hub.items.length === 0)" class="no-items">
          No specific items information available.
        </div>
      </div>
      <div class="donation-notes">
        <p>{{ hub.notes || 'No additional notes.' }}</p>
      </div>
    </div>
    <div class="action-button-container gap-10">
      <Button
        label="Reserve"
        class="p-button-rounded w-full"
        severity="warning"
        :disabled="isReserved || loading"
        :loading="loading && action === 'reserve'"
        @click="handleReserve"
      />
      <Button
        label="Unreserve"
        class="p-button-rounded w-full"
        severity="danger"
        :disabled="!isReserved || loading"
        :loading="loading && action === 'unreserve'"
        @click="handleUnreserve"
      />
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref } from 'vue';
import { useStore } from 'vuex';
import Button from 'primevue/button';

const props = defineProps({
  hub: {
    type: Object,
    required: true
  },
  isReserved: {
    type: Boolean,
    required: true
  },
  foodbankId: String
});

const store = useStore();
const emit = defineEmits(["close", "update:isReserved"]);
const loading = ref(false);
const action = ref('');

const handleReserve = async () => {
  if (loading.value) return;

  action.value = 'reserve';
  loading.value = true;

  try {
    await store.dispatch("apiRequest", {
      method: "POST",
      endpoint: "http://localhost:5015/reserveHub/reserve",
      data: {
        hubID: props.hub.hubID,
        foodbankID: props.foodbankId,
      }
    });
    
    emit("update:isReserved", true);
    emit("close");
  } catch (error) {
    console.error("Reserve failed:", error);
  } finally {
    loading.value = false;
  }
};

const handleUnreserve = async () => {
  if (loading.value) return;
  
  action.value = 'unreserve';
  loading.value = true;

  try {
    await store.dispatch("apiRequest", {
      method: "POST",
      endpoint: "http://localhost:5015/reserveHub/unreserve",
      data: {
        hubID: props.hub.hubID,
        foodbankID: props.foodbankId,
      }
    });
    
    emit("update:isReserved", false);
    emit("close");
  } catch (error) {
    console.error("Unreserve failed:", error);
    // Add error notification here if needed
  } finally {
    loading.value = false;
  }
};
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
  margin-bottom: 1.5rem;
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
  margin-bottom: 1.5rem;
}

.donation-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 6px;
  font-size: 1rem;
}

.no-items {
  text-align: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 6px;
  font-style: italic;
  color: #666;
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
  margin-top: 1.5rem;
}

.gap-10 {
  gap: 10px;
}
</style>