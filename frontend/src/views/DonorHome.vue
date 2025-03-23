<template>
    <div class="donation-app">
      
        <Navbar v-model="activeTab"/>
      <!-- Content area -->
      <div class="content-area">
        <!-- Create Listing Tab Content -->
        <div v-if="activeTab === 'create'" class="create-listing">
          <div class="listing-container">
            <div class="listing-form">
              <div class="form-section">
                <div class="image-upload-area">
                  <img v-if="previewImage" :src="previewImage" class="preview-image" alt="Donation preview" />
                  <div v-else class="upload-placeholder">
                    <i class="upload-icon">📷</i>
                    <p>Upload Photo</p>
                    <input type="file" @change="handleImageUpload" class="file-input" accept="image/*" />
                  </div>
                </div>
                
                <div class="form-fields">
                  <div class="form-group">
                    <div class="input-with-icon">
                      <i class="icon">+</i>
                      <input type="text" placeholder="Input Description of Goods" class="form-control" v-model="description" />
                    </div>
                  </div>
                  
                  <div class="form-group">
                    <div class="input-with-icon">
                      <i class="icon">+</i>
                      <input type="number" placeholder="Quantity" class="form-control" v-model="quantity" />
                    </div>
                  </div>
                  
                  <div class="location-indicator">
                    <div class="location-icon">📍</div>
                    <span class="location-text">Current Location</span>
                  </div>
                  
                  <button class="post-button" @click="postListing">Post Listing</button>
                </div>
              </div>
            </div>
          </div>
        </div>
  
        <!-- Posted Listings Tab Content -->
        <div v-if="activeTab === 'posted'" class="posted-listings">
          <div class="listings-container">
            <div v-if="postedListings.length === 0" class="no-listings">
              <p>No listings posted yet.</p>
            </div>
            <div v-else class="listings-grid">
              <div v-for="(listing, index) in postedListings" :key="index" class="listing-card">
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
      </div>
      <button @click="signOut" class="logout-button">Log Out</button>
    </div>
  </template>
  
  <script setup>
  import { ref, inject, onMounted } from 'vue';
  import { useStore } from 'vuex';
  import { useRouter } from 'vue-router';
  import Navbar from '../components/Navbar.vue';
  
  // Setup authentication and state management
  const supabase = inject('supabase');
  const store = useStore();
  const router = useRouter();
  const user = ref(null);
  
  // Component state
  const activeTab = ref('create');
  const description = ref('');
  const quantity = ref('');
  const location = ref('Current Location');
  const previewImage = ref(null);
  const postedListings = ref([]);
  
  // Check authentication on component mount
  onMounted(() => {
    checkAuth();
  });
  
  // Authentication management
  const checkAuth = () => {
    const authListener = supabase.auth.onAuthStateChange((event, session) => {
      if (session?.user && session.user?.user_metadata?.role === "donor") {
        user.value = session.user;
        console.log("User authenticated:", user.value);
      } else {
        user.value = null;
        router.push("/");
      }
    });
  
    // Return cleanup function
    return () => {
      if (authListener && authListener.data) {
        authListener.data.unsubscribe();
      }
    };
  };
  
  // Logout function
  const signOut = async () => {
    await store.dispatch('logout');
    router.push('/');
  };
  
  // Image upload handling
  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        previewImage.value = e.target.result;
      };
      reader.readAsDataURL(file);
    }
  };
  
  // Form submission
  const postListing = () => {
    if (description.value && quantity.value && previewImage.value) {
      postedListings.value.push({
        description: description.value,
        quantity: quantity.value,
        location: location.value,
        image: previewImage.value
      });
      
      // Reset form
      description.value = '';
      quantity.value = '';
      previewImage.value = null;
      
      // Switch to posted listings tab
      activeTab.value = 'posted';
    } else {
      alert('Please fill all fields and upload an image');
    }
  };
  </script>
  
  <style scoped>
  .donation-app {
    display: flex;
    flex-direction: column;
    height: 100%;
    padding: 1rem;
    background-color: #fff;
    border-radius: 8px;
  }
  
  .content-area {
    background-color: white;
    padding: 20px;
    min-height: 400px;
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
    border: 1px dashed #ccc;
    display: flex;
    align-items: center;
    justify-content: center;
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
    font-size: 3rem;
    margin-bottom: 10px;
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
    align-items: center;
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
    background-color: #4a4a4a;
    color: white;
    border: none;
    border-radius: 25px;
    font-size: 18px;
    font-weight: bold;
    cursor: pointer;
    width: 100%;
  }
  
  .post-button:hover {
    background-color: #333;
  }
  
  .logout-button {
    margin-top: 15px;
    padding: 10px 15px;
    background-color: #f44336;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    align-self: flex-end;
  }
  
  .logout-button:hover {
    background-color: #d32f2f;
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