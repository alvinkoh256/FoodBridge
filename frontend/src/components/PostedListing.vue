<template>
    <div class="posted-listings">
      <div class="listings-container">
        <div v-if="listings.length === 0" class="no-listings">
          <p>No listings posted yet.</p>
        </div>
        <div v-else class="listings-grid">
          <div v-for="(listing, index) in listings" :key="index" class="listing-card">
            <img :src="listing.image" class="listing-image" alt="Donation item" />
            <div class="listing-details">
              <h3>{{ listing.description }}</h3>
              <p>Quantity: {{ listing.quantity }}</p>
              <p class="location">📍 {{ listing.location }}</p>
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
    margin-bottom: 10px;
  }
  
  .location {
    color: #666;
    margin-top: 10px;
  }
  
  .no-listings {
    text-align: center;
    padding: 50px 0;
    color: #666;
  }
  </style>