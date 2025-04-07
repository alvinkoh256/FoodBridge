<template>
  <div class="home-container">
    <!-- Navbar -->
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

    <!-- Progress Bar 3 Stages-->

    <!--1st stage Main Content -->
    <ProductListing></ProductListing>

    <!-- 2nd Stage Delivery -->
    <Delivery></Delivery>

    <!-- 3rd Stage Drop Off-->
    <DropOff></DropOff>


  </div>
</template>

<script setup>
import { ref, inject, onMounted, onUnmounted } from "vue";
import { useStore } from "vuex";
import { useRouter } from "vue-router";
import ProductListing from "../components/ProductListing.vue";
import Delivery from "../components/Delivery.vue";
import DropOff from "../components/DropOff.vue";

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

  socket.on("productListingRoom", (data) => {
    console.log("Received data from productListingRoom:", data);
    if (Array.isArray(data)) {
      data.forEach((newProduct) => {
        const index = products.value.findIndex(
          (p) => p.productId === newProduct.productId
        );
        if (index !== -1) {
          products.value[index] = newProduct;
        } else {
          products.value.push(newProduct);
        }
      });
    } else {
      console.warn("Expected array from productListingRoom, got:", data);
    }
  });
});

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
  socket.off("productListingRoom");
});
</script>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #fff;
}

/* Navbar styles - kept consistent with original */
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
  max-height: 70px;
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

.nav-tab {
  padding: 8px 16px;
  cursor: pointer;
  font-weight: bold;
  color: black;
  position: relative;
  transition: color 0.2s ease;
}

.logout-section {
  display: flex;
  align-items: center;
}

.logout-button {
  padding: 0.5rem 1rem;
  color: #f43f5e;
  background-color: transparent;
  border: 1px solid #f43f5e;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.logout-button:hover {
  background-color: #f43f5e;
  color: white;
}

/* Content styles - improved */
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

/* Product list styles - improved */
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
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.drop-off-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.ongoing-status {
  border-left: 4px solid #ff0000;
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
  
  .logo-image {
    max-height: 60px;
  }
}

@media (max-width: 480px) {
  .navbar {
    height: auto;
    padding: 0.5rem;
    flex-wrap: wrap;
  }
  
  .tabs-section {
    width: 100%;
    justify-content: center;
    margin-top: 0.5rem;
  }
  
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