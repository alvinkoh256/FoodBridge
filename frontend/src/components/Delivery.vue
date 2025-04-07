<template>
    <div class="header">
      <div class="navbar">
      <div class="logo-section">
        <img src="../assets/Foodbridge.png" alt="Profile" class="logo-image">
      </div>
      <div class="tabs-section">
        <div class="nav-tab">Food Bridge</div>
      </div>
      <div class="logout-section">
        <button class="logout-button" @click="signOut">
          Log Out
        </button>
      </div>
    </div>
</div>
    <div class="flex flex-col items-center p-6 min-h-screen ">
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
  
      <Button 
        label="Confirm Delivery"
        @click="visible = true"
        class="mt-10"
        severity="warn"
      />
  
      <!-- Modal -->
      <Dialog v-model:visible="visible" modal header="Confirm Delivery" :style="{ width: '90%', maxWidth: '400px' }">
        <p class="text-center text-gray-600 text-sm">Are you sure the goods have been delivered?</p>
        <div class="flex justify-around mt-4">
          <Button label="No" class="w-25 p-button-rounded mt-5" @click="visible = false" severity="warn"/>
          <Button label="Yes" class="w-25 p-button-rounded mt-5" @click="confirmDelivery" severity="warn"/>
        </div>
      </Dialog>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, inject, computed } from 'vue';
  import { useStore } from 'vuex';
  import { useRouter } from 'vue-router';
  import Dialog from 'primevue/dialog';
  import Button from 'primevue/button';
  
  const router = useRouter();
  const store = useStore();
  const supabase = inject('supabase');
  
  const visible = ref(false);
  const imageUrl = ref(null);
  const fileInput = ref(null);
  const user = ref(null);

  const product = computed(() => JSON.parse(localStorage.getItem('savedProduct')));

  onMounted(async () => {
    await checkAuth();
  });

  const checkAuth = async () => {
    // First check the current session
    const { data: { session }, error } = await supabase.auth.getSession();
    if (error) {
      console.error("Error checking session:", error);
      router.push("/");
      return;
    }
    
    if (session?.user && session.user?.user_metadata?.role === "V") {
      user.value = session.user;
      console.log("User authenticated:", user.value);
    } else {
      user.value = null;
      router.push("/");
    }
    
    // Then set up the listener for future changes
    const { data: authListener } = supabase.auth.onAuthStateChange((event, session) => {
      if (session?.user && session.user?.user_metadata?.role === "V") {
        user.value = session.user;
        console.log("Auth state changed - user authenticated:", user.value);
      } else {
        user.value = null;
        router.push("/");
      }
    });
  
    // Return the unsubscribe function
    return () => {
      authListener?.unsubscribe();
    };
  };
  
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
        await store.dispatch('apiRequest', {
          method: 'delete',
          endpoint: 'http://localhost:5005/product',
          data: {
            productId: product.value.productId
          }
      });

      alert('Delivery Confirmed!');
      visible.value = false;
      router.push('/home/drop');
    } catch(error){
      console.error('Failed to update product status:', error);
    }
  };

  const signOut = async () =>{
  store.dispatch('logout');
  router.push('/')
};
  </script>
  
  <style>
  .header {
  width: 100%;
  background-color: #fff;
  border-bottom: 1px solid #f0f0f0;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  height: 60px;
  padding: 0 8px;
}

.logo-section {
  display: flex;
  align-items: center;
  min-width: 100px;
}

.logo-image {
  max-height: 100px; 
  width: auto;
}

.tabs-section {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex: 1;
}


.logout-button {
  padding: 8px 16px;
  background-color: transparent;
  color: black;
  border: 2px solid #f44336;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.logout-button:hover {
  background-color: #d32f2f;
  color: white;
}

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
}

.upload-container img {
  width: 100%;
  height: auto;
  object-fit: contain;
  border-radius: 6px;
}
</style>