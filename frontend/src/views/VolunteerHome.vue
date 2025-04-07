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

    <!-- Progress Bar -->
    <div class="progress-container">
      <div class="progress-steps">
        <div 
          v-for="(step, index) in steps" 
          :key="index"
          :class="['progress-step', { 'active': currentStep >= index, 'complete': currentStep > index }]"
        >
          <div class="step-icon">{{ index + 1 }}</div>
          <div class="step-label">{{ step }}</div>
          <div v-if="index < steps.length - 1" class="step-connector"></div>
        </div>
      </div>
    </div>

    <!-- Dynamic Content Based on Current Step -->
    <div class="step-content">
      <!-- 1st Stage: Product Listing -->
      <ProductListing 
        v-if="currentStep === 0" 
        :products="products"
        @product-selected="handleProductSelected"
      ></ProductListing>

      <!-- 2nd Stage: Delivery -->
      <Delivery 
        v-if="currentStep === 1" 
        :selectedProduct="selectedProduct"
        @delivery-confirmed="handleDeliveryConfirmed"
      ></Delivery>

      <!-- 3rd Stage: Drop Off -->
      <DropOff 
        v-if="currentStep === 2" 
        :selectedProduct="selectedProduct"
        @drop-off-confirmed="handleDropOffConfirmed"
      ></DropOff>

      <!-- Success Message after completion -->
      <div v-if="currentStep === 3" class="completion-message">
        <div class="success-icon">✓</div>
        <h2>Delivery Complete!</h2>
        <p>Thank you for your contribution to Food Bridge.</p>
        <button class="new-delivery-button" @click="resetProcess">Start New Delivery</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, inject, onMounted, onUnmounted, watch } from "vue";
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
const products = ref([]);
const selectedProduct = ref(null);
const currentStep = ref(0);

const steps = ["Select Product", "Confirm Delivery", "Drop Off"];

// Check for saved product and set appropriate step
const checkSavedProduct = () => {
  const savedProductString = localStorage.getItem('savedProduct');
  const deliveryStatus = localStorage.getItem('deliveryConfirmed');
  if (savedProductString) {
    try {
      const savedProduct = JSON.parse(savedProductString);
      if (savedProduct && savedProduct.productId) {
        selectedProduct.value = savedProduct;
        // Go directly to the drop-off step (step 2)
        if(deliveryStatus){
          currentStep.value = 2;
        }
        else{
          currentStep.value = 1;
        }
        console.log('Restored saved product, proceeding to drop-off step:', savedProduct);
      }
    } catch (error) {
      console.error('Error parsing saved product:', error);
      localStorage.removeItem('savedProduct');
    }
  }
};

// Check authentication on component mount
onMounted(async () => {
  checkAuth();
  // Check for saved product immediately after auth check
  checkSavedProduct();

  // localStorage.removeItem('savedProduct');
  // localStorage.removeItem('deliveryConfirmed');
  
  try {
    const response = await store.dispatch("apiRequest", {
      method: "get",
      endpoint: "http://localhost:5005/products",
    });
    products.value = response;
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

// Authentication management
const checkAuth = () => {
  const authListener = supabase.auth.onAuthStateChange((event, session) => {
    if (session?.user && session.user?.user_metadata?.role === "V") {
      user.value = session.user;
      console.log("User authenticated:", user.value);
      // Check for saved product again after successful authentication
      checkSavedProduct();
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

// Handle product selection from the ProductListing component
const handleProductSelected = (product) => {
  selectedProduct.value = product;
  localStorage.setItem('savedProduct', JSON.stringify(product));
  currentStep.value = 1;
};

// Handle delivery confirmation from the Delivery component
const handleDeliveryConfirmed = () => {
  localStorage.setItem('deliveryConfirmed', 'true');
  currentStep.value = 2;
};

// Handle drop-off confirmation from the DropOff component
const handleDropOffConfirmed = () => {
  // Clean up after successful completion
  localStorage.removeItem('savedProduct');
  localStorage.removeItem('deliveryConfirmed');
  currentStep.value = 3;
};

// Reset the process to start a new delivery
const resetProcess = () => {
  selectedProduct.value = null;
  localStorage.removeItem('savedProduct');
  currentStep.value = 0;
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

/* Navbar styles */
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

/* Progress Bar Styles */
.progress-container {
  padding: 2rem 1rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  position: relative;
  margin: 0 auto;
  max-width: 800px;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  z-index: 1;
  flex: 1;
}

.step-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909090;
  font-weight: 500;
  margin-bottom: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.step-label {
  font-size: 13px;
  color: #909090;
  text-align: center;
  transition: all 0.3s ease;
  font-weight: 400;
  letter-spacing: 0.2px;
}

.step-connector {
  position: absolute;
  top: 16px;
  right: calc(-50% + 16px);
  width: calc(100% - 32px);
  height: 1px;
  background-color: #f0f0f0;
  z-index: 0;
  transition: all 0.3s ease;
}

.progress-step.active .step-icon {
  background-color: #f43f5e;
  color: white;
  transform: scale(1.05);
  box-shadow: 0 2px 4px rgba(244, 63, 94, 0.2);
}

.progress-step.active .step-label {
  color: #222222;
  font-weight: 500;
}

.progress-step.complete .step-icon {
  background-color: #10b981;
  color: white;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

.progress-step.complete + .progress-step .step-connector,
.progress-step.complete .step-connector {
  background-color: #10b981;
  height: 2px;
}

/* Responsive styles */
@media (max-width: 768px) {
  .progress-steps {
    max-width: 600px;
  }
  
  .step-label {
    font-size: 12px;
  }
  
  .step-icon {
    width: 28px;
    height: 28px;
    font-size: 14px;
  }
  
  .step-connector {
    top: 14px;
  }
}

@media (max-width: 480px) {
  .step-label {
    display: none;
  }
  
  .step-icon {
    width: 24px;
    height: 24px;
    font-size: 12px;
    margin-bottom: 0;
  }
  
  .step-connector {
    top: 12px;
    right: calc(-50% + 12px);
    width: calc(100% - 24px);
  }
  
  .progress-container {
    padding: 1.5rem 0.5rem;
  }
}
</style>