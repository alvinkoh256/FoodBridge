<template>
  <div class="content">
    <div class="title">For You</div>
    <div class="divider"></div>
    <!-- Product List -->
    <div class="product-list">
      <div
        v-for="product in filteredProducts"
        :key="product.productId"
        :class="['drop-off-item border-l-4', {
          'border-indigo-500': product.productStatus !== 'on-going',
          'border-red-500 ongoing-status': product.productStatus === 'on-going',
          'cursor-pointer': product.productStatus !== 'on-going'
        }]"
        @click="product.productStatus !== 'on-going' && openDialog(product)"
      >
        <div class="profile-pic">
          <img :src="product.productPic" alt="Product Image">
        </div>
        <div class="drop-off-info">
          <div class="drop-off-location">
            Drop-off at {{ product.productCCDetails.hubName }}
          </div>
          <div class="drop-off-address">
            {{ product.productAddress }}
          </div>
        </div>
      </div>
    </div>

    <!-- Dialog -->
    <Dialog
      v-model:visible="visible"
      modal
      header="Drop-off Details"
      :breakpoints="{'960px': '95vw'}"
      :style="{ width: '75rem', maxWidth: '95vw' }"
    >
      <DialogContentVolunteer
        :product="selectedProduct"
        @accept="handleAccept"
      />
    </Dialog>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits, computed } from "vue";
import Dialog from "primevue/dialog";
import DialogContentVolunteer from "../components/DialogContentVolunteer.vue";

const props = defineProps({
  products: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['product-selected']);
const visible = ref(false);
const selectedProduct = ref(null);

// Filter out completed products
const filteredProducts = computed(() => {
  return props.products.filter(product => product.productStatus !== 'completed');
});

const openDialog = (product) => {
  // Only open dialog if product is not ongoing
  if (product.productStatus !== 'on-going') {
    selectedProduct.value = product;
    visible.value = true;
  }
};

const handleAccept = (updatedProduct) => {
  visible.value = false;
  emit('product-selected', updatedProduct);
};
</script>

<style scoped>
.content {
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 0 1rem;
  flex: 1;
}
.title {
  font-size: 2.5rem;
  font-weight: bold;
  color: black;
  margin-top: 1.5rem;
}
.divider {
  height: 1px;
  background-color: #ccc;
  margin: 1.25rem 0;
}
/* Product list styles */
.product-list {
  display: grid;
  gap: 0.75rem;
  margin-bottom: 2rem;
}
.drop-off-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  background-color: white;
  border-radius: 5px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.drop-off-item:hover:not(.ongoing-status) {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.ongoing-status {
  opacity: 0.7;
  cursor: default !important;
}
.profile-pic {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #ddd;
  margin-right: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
}
.profile-pic img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.drop-off-info {
  flex: 1;
}
.drop-off-location {
  font-weight: bold;
  color: black;
  margin-bottom: 0.25rem;
}
.drop-off-address {
  font-size: 12px;
  color: #666;
}
/* Responsive styles */
@media (max-width: 768px) {
  .title {
    font-size: 2rem;
  }
  .drop-off-item {
    padding: 0.75rem;
  }
}
@media (max-width: 480px) {
  .title {
    font-size: 1.75rem;
    text-align: center;
  }
  .drop-off-item {
    padding: 0.5rem;
  }
  .profile-pic {
    width: 32px;
    height: 32px;
  }
}
</style>