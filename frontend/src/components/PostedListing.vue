<template>
  <div class="posted-listings">
    <div class="listings-container">
      <div v-if="!listings || listings.length === 0" class="no-listings">
        <p>No listings posted yet.</p>
      </div>
      <div v-else class="listings-grid">
        <div v-for="(product, index) in listings" :key="product.productId" class="listing-card">
          <div class="status-indicator" :class="{ 'status-ongoing': product.productStatus === 'on-going' }">
            {{ product.productStatus === 'on-going' ? 'In Progress' : 'Open' }}
          </div>
          <img :src="product.productPic" class="listing-image" alt="Donation item" />
          <div class="listing-details">
            <h3>Donation Listing</h3>
            <div v-if="product.productItemList && product.productItemList.length > 0">
              <div v-for="(item, itemIndex) in product.productItemList" :key="itemIndex" class="item-detail">
                <p><strong>{{ item.itemName }}</strong>: {{ item.quantity }}</p>
              </div>
            </div>
            <p class="location">📍 {{ product.productAddress }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue';

const props = defineProps({
  listings: {
    type: Array,
    default: () => []
  }
});
</script>

<style scoped>
.posted-listings {
  width: 100%;
}

.listings-container {
  width: 100%;
}

.listings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.listing-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  position: relative;
}

.listing-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.status-indicator {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  color: white;
  background-color: #4CAF50;
  z-index: 1;
}

.status-ongoing {
  background-color: #FF5252;
}

.listing-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.listing-details {
  padding: 15px;
}

.listing-details h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #ff7e5f;
}

.item-detail {
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px dashed #eee;
}

.item-detail:last-child {
  border-bottom: none;
}

.location {
  color: #666;
  margin-top: 10px;
  display: flex;
  align-items: center;
}

.no-listings {
  text-align: center;
  padding: 50px 0;
  color: #666;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin-top: 20px;
}
</style>