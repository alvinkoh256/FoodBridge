<template>
  <div class="create-listing">
    <div class="listing-container">
      <div class="listing-form">
        <div class="form-section">
          <div class="image-upload-area">
            <img v-if="previewImage" :src="previewImage" class="preview-image" alt="Donation preview" />
            <div v-else class="upload-placeholder">
              <i class="upload-icon">Insert Photo</i>
              <input type="file" @change="handleImageUpload" class="file-input" accept="image/*" />
            </div>
          </div>
          
          <div class="form-fields">
              <div class="input-with-icon">
                <ItemDropdown @items-selected="updateSelectedItems" />
              </div>

              <div class="input-with-icon">
                <CreateItem @new-items-added="updateNewItems" :showWeight="false"/>
              </div>
            
            <div class="location-indicator">
              <div class="location-icon">📍</div>
              <AutoComplete ref="locationAutocomplete" @location-selected="updateLocation" />
            </div>
            
            <button class="post-button" @click="postListing">Post Listing</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps } from 'vue';
import { useStore } from 'vuex';
import AutoComplete from './AutoComplete.vue';
import ItemDropdown from './ItemDropdown.vue';
import CreateItem from './CreateItem.vue';

const props = defineProps({
  user: Object
});

const store = useStore();
const emit = defineEmits(['listing-posted']);

const location = ref('Current Location');
const previewImage = ref(null);
const selectedItems = ref([]);
const newCreatedItems = ref([]);
const selectedImage = ref(null);

// Image upload handling
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

// Update functions to receive data from child components
const updateSelectedItems = (items) => {
  selectedItems.value = items;
  console.log('Selected items updated:', items);
};

const updateNewItems = (items) => {
  newCreatedItems.value = items;
  console.log('New items updated:', items);
};

// Update location from AutoComplete component
const updateLocation = (selectedLocation) => {
  location.value = selectedLocation;
};

//For Debugging
// const logFormData = (formData) => {
//   for (let [key, value] of formData.entries()) {
//     console.log(key, value);
//   }
// };

// Form submission
const postListing = async () => {

  if (previewImage.value) {
    // Create the submission object with the required structure
    const allItems = [...selectedItems.value, ...newCreatedItems.value].map(item => ({
      itemName: item.itemName,
      quantity: item.quantity
    }));


    const formData = new FormData();
    formData.append('productPic', selectedImage.value); // the actual file
    formData.append('productAddress', location.value);
    formData.append('productCCDetails', JSON.stringify({
      hubId: props.user?.id, 
      hubName: props.user?.username, 
      hubAddress: props.user?.user_metadata?.address 
    }));
    formData.append('productItemList', JSON.stringify(allItems));
    
    // // Log the data for debugging
    // logFormData(formData);
    
    try {
      const response = await store.dispatch("apiRequest", {
        method: "post",
        endpoint: "http://localhost:5005/product",
        data: formData
      });

      // Reset form
      previewImage.value = null;
      selectedItems.value = [];
      newCreatedItems.value = [];

      emit('listing-posted', response);

    } catch (error) {
      console.error("Failed to fetch items:", error);
    }
  

  } else {
    alert('Please upload an image and select at least one item');
  }
};
</script>

<style scoped>
.create-listing {
  width: 100%;
}

.listing-container {
  display: flex;
  flex-direction: column;
}

.listing-form {
  width: 100%;
}

.form-section {
  display: flex;
  flex-direction: row;
  gap: 20px;
}

.image-upload-area {
  width: 300px;
  height: 300px;
  border: 3px solid #ff7e5f;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  position: relative;
  overflow: hidden;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.upload-icon {
  font-size: 1.5rem;
  color: #aaa;
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
}

.form-fields {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.input-with-icon {
  display: flex;
  justify-content: center;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.icon {
  padding: 10px;
  background-color: #f5f5f5;
  color: #666;
  font-weight: bold;
}

.form-control {
  flex: 1;
  padding: 10px 15px;
  border: none;
  outline: none;
  font-size: 16px;
}

.location-indicator {
  display: flex;
  align-items: center;
  margin-top: auto;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.location-icon {
  margin-right: 10px;
}

.post-button {
  margin-top: 20px;
  padding: 15px;
  background-color: #ff7e5f;
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 15px;
  font-weight: bold;
  cursor: pointer;
  width: 40%;
  margin: auto;
}

.post-button:hover {
  background-color: #333;
}
</style>