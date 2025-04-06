<template>
  <div class="donation-container">
    <!-- Image Section -->
    <div class="donation-image">
      <img :src="product?.productPic || '../assets/logo.jpg'" alt="Donation items" class="rounded-img">
    </div>
    
    <!-- Details Section -->
    <div class="donation-details">
      <h2 class="details-title">Details</h2>
      
      <div class="item-list">
        <div v-for="(item, index) in product?.productItemList || []" :key="index" class="item">
          <span class="item-name">{{ item.itemName }}</span>
          <span class="item-quantity">x{{ item.quantity }}</span>
        </div>
      </div>
      
      <div class="location-info">
        <p><span class="text-bold">Drop-off Location:</span> {{ product?.productCCDetails?.hubName }}</p>
        <p><span class="text-bold">Address:</span> {{ product?.productAddress }}</p>
      </div>
    </div>
  </div>
  
  <!-- Action Button -->
  <div class="button-wrapper">
    <Button 
      label="Accept" 
      class="p-button-rounded" 
      severity="success" 
      @click="acceptDropOff" 
      :disabled="isButtonDisabled"
      :loading="loading"
    />
  </div>
</template>

<script setup>
import { defineProps, computed, ref } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from "vue-router";
import Button from 'primevue/button';

const props = defineProps({
  product: {
    type: Object,
    default: () => ({})
  }
});

const store = useStore();
const router = useRouter();
const loading = ref(false);

// Determine if the button should be disabled
const isButtonDisabled = computed(() => props.product?.productStatus === 'on-going');

const acceptDropOff = async () => {
  if (!props.product?.productId) {
    console.error('Product ID is missing');
    return;
  }

  loading.value = true;
  
  try {
    await store.dispatch('apiRequest', {
      method: 'put',
      endpoint: 'http://localhost:5005/product',
      data: {
        productId: props.product.productId,
        productStatus: 'on-going'
      }
    });
    
    // Update product status
    const updatedProduct = { ...props.product, productStatus: 'on-going' };
    localStorage.setItem('savedProduct', JSON.stringify(updatedProduct));
    router.push('/home/delivery');
  } catch (error) {
    console.error('Failed to update product status:', error);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.donation-container {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.donation-image {
  flex: 1;
}

.rounded-img {
  width: 100%;
  height: auto;
  border-radius: 8px;
  object-fit: cover;
  max-height: 350px;
}

.donation-details {
  flex: 1;
  background-color: white;
  border-radius: 8px;
  padding: 1.25rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.04);
}

.details-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #333;
}

.item-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.item {
  display: flex;
  justify-content: space-between;
  font-size: 1rem;
  padding: 0.25rem 0;
}

.item-name {
  font-weight: 500;
  color: #333;
}

.item-quantity {
  color: #555;
}

.location-info {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #f0f0f0;
  font-size: 0.9rem;
  line-height: 1.6;
  color: #555;
}

.text-bold {
  font-weight: 600;
}

.button-wrapper {
  display: flex;
  justify-content: center;
  width: auto;
  max-width: 180px;
  margin: 0 auto;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .donation-container {
    flex-direction: column;
  }
  
  .donation-image, .donation-details {
    width: 100%;
  }
  
  .rounded-img {
    max-height: 250px;
  }
  
  .button-wrapper {
    width: 100%;
    max-width: 100%;
  }
}
</style>