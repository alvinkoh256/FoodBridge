<template>
  <div class="home-container">
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
    <div class="title">For You</div>
    <div class="divider"></div>
    <div 
      v-for="(product, index) in products" 
      :key="product.productId" 
      :class="['drop-off-item', {'ongoing-status': product.productStatus === 'on-going'}]" 
      @click="openDialog(product)"
    >
      <div class="profile-pic">
        <img :src="product.productPic" alt="Product Image">
      </div>
      <div class="drop-off-info">
        <div class="drop-off-location text-black">
          Drop-off at {{ product.productCCDetails.hubName }}
        </div>
        <div class="drop-off-address">
          {{ product.productAddress }}
        </div>
      </div>
    </div>

    <Dialog v-model:visible="visible" modal header="Drop-off Details" :style="{ width: '75rem' }">
      <DialogContentVolunteer :product="selectedProduct"/>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, inject, onMounted, onUnmounted } from "vue";
import { useStore } from "vuex";
import { useRouter } from "vue-router";
import DialogContentVolunteer from "../components/DialogContentVolunteer.vue";
import Dialog from "primevue/dialog";

const supabase = inject("supabase");
const store = useStore();
const router = useRouter();
const socket = inject("socket"); 

const user = ref(null);
const visible = ref(false);
const products = ref([]);
const selectedProduct = ref(null);


// Check authentication on component mount
onMounted(async () => {
  checkAuth();

  try {
    const response = await store.dispatch("apiRequest", {
      method: "get",
      endpoint: "http://localhost:5005/products",
    });

    products.value = response;
    //filterProducts(response);
  } catch (error) {
    console.error("Failed to fetch items:", error);
  }

  // Listen for product updates from socket
  // socket.on("productUpdated", (updatedProduct) => {
  //   console.log("New product update received:", updatedProduct);

  //   // Only show products that include the user's ID
  //   if (user.value?.id && updatedProduct.productUserList?.includes(user.value.id)) {
  //     // Check if the product already exists in the list
  //     const index = products.value.findIndex(
  //       (p) => p.productId === updatedProduct.productId
  //     );

  //     if (index !== -1) {
  //       // Update existing product
  //       products.value[index] = updatedProduct;
  //     } else {
  //       // Add new product
  //       products.value.push(updatedProduct);
  //     }
  //   }
  // });
});

// Authentication management
const checkAuth = () => {
  const authListener = supabase.auth.onAuthStateChange((event, session) => {
    if (session?.user && session.user?.user_metadata?.role === "V") {
      user.value = session.user;
      console.log("User authenticated:", user.value);
    } else {
      user.value = null;
      router.push("/");
    }
  });

  return () => {
    if (authListener?.data) {
      authListener.data.unsubscribe();
    }
  };
};

// Function to filter products by user ID
const filterProducts = (productList) => {
  if (user.value?.id) {
    products.value = productList.filter(
      (product) => product.productUserList?.includes(user.value.id)
    );
  } else {
    products.value = [];
  }
};

const signOut = async () => {
  await store.dispatch("logout");
  router.push("/");
};

const openDialog = (product) => {
  selectedProduct.value = product;
  visible.value = true;
};

// Cleanup socket listeners when component unmounts
onUnmounted(() => {
  socket.off("productUpdated");
});

</script>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 1rem;
  background-color: #fff;
  border-radius: 8px;
}

.nav-tab {
  padding: 8px 16px;
  cursor: pointer;
  font-weight: bold;
  color: black;
  position: relative;
  transition: color 0.2s ease;
}

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

.divider {
  border-top: 1px solid #ccc;
  margin: 20px 0;
}

.drop-off-item {
  display: flex;
  align-items: center;
  padding: 15px;
  background-color: white;
  border-radius: 5px;
  margin-bottom: 10px;
  border: 3px solid #f44336;
  cursor: pointer; 
}

.ongoing-status {
  background-color: #ffecec;
  border: 3px solid #ff0000;
}

.profile-pic {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #ddd;
  margin-right: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
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

img {
  object-fit: cover; 
  width: 100%;
  height: 100%;
}

.drop-off-info {
  flex-grow: 1;
}

.drop-off-location {
  font-weight: bold;
  margin-bottom: 5px;
}

.drop-off-address {
  font-size: 12px;
  color: #666;
}

.title {
  text-align: left;
  padding-top: 10px;
  font-weight: bold;
  font-size: 40px;
  color: black;
}
</style>