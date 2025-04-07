<template>
  <div class="create-listing w-full bg-gray-50 p-6 rounded-lg">
    <Toast position="bottom-center" />
    <div class="listing-container">
      <div class="listing-form">
        <div class="form-section flex flex-col md:flex-row gap-6">
          <div class="image-upload-area mx-auto md:mx-0 transition-all hover:shadow-lg">
            <img v-if="previewImage" :src="previewImage" class="preview-image" alt="Donation preview" />
            <div v-else class="upload-placeholder">
              <i class="upload-icon pi pi-camera text-3xl text-gray-400"></i>
              <p class="text-gray-500 mt-2 text-sm uppercase tracking-wider">Upload Photo</p>
              <input type="file" @change="handleImageUpload" class="file-input" accept="image/*" />
            </div>
          </div>
          
          <div class="form-fields flex-1 flex flex-col">
            <div class="mb-5 bg-white p-5 rounded-lg shadow-sm border-t-4 border-indigo-500">
              <h3 class="text-gray-700 font-medium text-sm uppercase tracking-wider mb-4">Select Existing Items</h3>
              <ItemDropdown @items-selected="updateSelectedItems" />

              <CreateItem @new-items-added="updateNewItems" :showWeight="false"/>
            
              <div class="flex-1">
                <label class="text-gray-700 font-medium text-sm text-left uppercase tracking-wider block mb-2">Location</label>
                <AutoComplete ref="locationAutocomplete" @location-selected="updateLocation" />
              </div>
            </div>
            
            <button 
              class="post-button transition-all flex items-center justify-center" 
              @click="postListing"
              :disabled="isLoading"
            >
              <i v-if="isLoading" class="pi pi-spin pi-spinner mr-2"></i>
              {{ isLoading ? 'Posting...' : 'Post Listing' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps } from 'vue';
import { useStore } from 'vuex';
import { useToast } from 'primevue/usetoast';
import Dropdown from 'primevue/dropdown';
import Toast from 'primevue/toast';
import AutoComplete from './AutoComplete.vue';
import ItemDropdown from './ItemDropdown.vue';
import CreateItem from './CreateItem.vue';

const props = defineProps({
  user: Object
});

const store = useStore();
const toast = useToast();
const emit = defineEmits(['listing-posted']);

const location = ref('Current Location');
const previewImage = ref(null);
const selectedItems = ref([]);
const newCreatedItems = ref([]);
const selectedImage = ref(null);
const isLoading = ref(false);

const handleImageUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    selectedImage.value = file;

    const reader = new FileReader();
    reader.onload = (e) => {
      previewImage.value = e.target.result;
    };
    reader.readAsDataURL(file);
  }
};

const updateSelectedItems = (items) => {
  selectedItems.value = items;
};

const updateNewItems = (items) => {
  newCreatedItems.value = items;
};

const updateLocation = (selectedLocation) => {
  location.value = selectedLocation;
};

const showErrorToast = (message) => {
  toast.add({
    severity: 'error',
    summary: 'Error',
    detail: message,
    life: 5000,
    position: 'bottom-center'
  });
};

const showSuccessToast = (message) => {
  toast.add({
    severity: 'success',
    summary: 'Success',
    detail: message,
    life: 5000,
    position: 'bottom-center'
  });
};

const postListing = async () => {
  if (!previewImage.value) {
    showErrorToast('Please upload an image');
    return;
  }
  
  if (selectedItems.value.length === 0 && newCreatedItems.value.length === 0) {
    showErrorToast('Please select at least one item');
    return;
  }

  isLoading.value = true;

  const allItems = [...selectedItems.value, ...newCreatedItems.value].map(item => ({
    itemName: item.itemName,
    quantity: item.quantity
  }));
  
  const formData = new FormData();
  formData.append('image', selectedImage.value); 
  formData.append('productAddress', location.value);

  const itemsJson = JSON.stringify(allItems).replace(/\\\//g, '/');
  formData.append('productItemList', itemsJson);

  formData.append('productUserId', props.user.id);

  try {
    const response = await store.dispatch("apiRequest", {
      method: "post",
      endpoint: "http://localhost:5001/findVolunteers",
      data: formData
    });

    previewImage.value = null;
    selectedItems.value = [];
    newCreatedItems.value = [];
    
    showSuccessToast('Listing posted successfully!');
    emit('listing-posted', response);
  } catch (error) {
    console.error("Failed to find volunteer:", error);
    
    // Extract error message from response or use a default message
    const errorMessage = error.response?.data?.message || 'Failed to post listing. Please try again.';
    showErrorToast(errorMessage);
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.create-listing {
  transition: all 0.3s ease;
}

.image-upload-area {
  width: 300px;
  height: 300px;
  border: 2px dashed #6366f1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.75rem;
  position: relative;
  overflow: hidden;
  margin-bottom: 1rem;
  background-color: white;
  transition: all 0.2s ease;
}

.image-upload-area:hover {
  border-color: #4f46e5;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  cursor: pointer;
  transition: all 0.2s ease;
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 0.5rem;
}

.post-button {
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: white;
  border: none;
  border-radius: 50px;
  font-size: 1rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  cursor: pointer;
  width: 100%;
  max-width: 250px;
  margin: 0 auto;
  display: block;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(99, 102, 241, 0.25);
  height: 3.5rem;
}

.post-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 10px rgba(99, 102, 241, 0.3);
}

.post-button:active:not(:disabled) {
  transform: translateY(1px);
}

.post-button:disabled {
  background: linear-gradient(135deg, #a5a6f6 0%, #9795ee 100%);
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .form-section {
    padding: 0 0.5rem;
  }
  
  .image-upload-area {
    width: 100%;
    max-width: 300px;
  }
}
</style>