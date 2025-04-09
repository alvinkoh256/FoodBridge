<template>
  <div class="flex flex-col items-center p-6 min-h-screen">
    <h1 class="text-xl font-bold mb-10 text-left">Goods Delivery Confirmation</h1>

    <div 
      class="upload-container"
      @click="triggerFileInput"
    >
      <input type="file" @change="handleImageUpload" class="hidden" ref="fileInput" accept="image/*" />
      <img v-if="imageUrl" :src="imageUrl" alt="Uploaded Image" class="object-cover rounded-lg" />
      <div v-else class="text-gray-500 flex flex-col items-center">
        <i class="pi pi-camera text-3xl"></i>
        <span class="mt-1 text-sm">Tap to upload</span>
      </div>
    </div>

    <button 
      class="confirm-button"
      @click="visible = true"
      :disabled="!imageUrl"
    >
      Confirm Delivery
    </button>

    <!-- Modal -->
    <Dialog v-model:visible="visible" modal header="Confirm Delivery" :style="{ width: '90%', maxWidth: '400px' }">
      <p class="text-center text-gray-600 text-sm">Are you sure the goods have been delivered?</p>
      <div class="flex justify-around mt-4">
        <button class="cancel-btn" @click="visible = false">No</button>
        <button class="confirm-btn" @click="confirmDelivery">Yes</button>
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue';
import Dialog from 'primevue/dialog';
import { useStore } from "vuex";

const store = useStore();

const props = defineProps({
  selectedProduct: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['delivery-confirmed']);

const visible = ref(false);
const imageUrl = ref(null);
const fileInput = ref(null);

const triggerFileInput = () => {
  fileInput.value.click();
};

const handleImageUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    imageUrl.value = URL.createObjectURL(file);
  }
};

const confirmDelivery = async () => {
  try {
    store.dispatch('apiRequest', {
      method: 'post',
        endpoint: `http://localhost:8000/updateProduct`,      
        data: {
        productId: props.selectedProduct.productId,
        productStatus: "completed"
      }
    });

    visible.value = false;
    emit('delivery-confirmed');
  } catch(error) {
    console.error('Failed to update product status:', error);
  }
};
</script>

<style scoped>
.upload-container {
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  border-radius: 6px;
  overflow: hidden;
  background-color: white;
  box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
  width: 100%;
  height: 40em;
  max-width: 600px;
  margin: 0 auto;
}

.upload-container img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 6px;
}

.hidden {
  display: none;
}

.confirm-button {
  margin-top: 2rem;
  padding: 0.75rem 2rem;
  background-color: #f43f5e;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.confirm-button:hover {
  background-color: #e11d48;
}

.confirm-button:disabled {
  background-color: #cbd5e1;
  cursor: not-allowed;
}

.cancel-btn {
  padding: 0.5rem 1.5rem;
  background-color: transparent;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  color: #374151;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 1rem;
}

.cancel-btn:hover {
  background-color: #f3f4f6;
}

.confirm-btn {
  padding: 0.5rem 1.5rem;
  background-color: #f43f5e;
  border: none;
  border-radius: 4px;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 1rem;
}

.confirm-btn:hover {
  background-color: #e11d48;
}
</style>