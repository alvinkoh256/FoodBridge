<template>
  <div class="container">
    <h2 class="title">What have you delivered?</h2>
    <ItemDropdown @items-selected="updateSelectedItems" />
    <CreateItem @new-items-added="updateNewItems" />
    <button 
      class="confirm-button" 
      @click="confirmDropOff"
      :disabled="!canConfirm"
    >
      Confirm Items
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject, defineProps, defineEmits } from 'vue';
import CreateItem from "../components/CreateItem.vue";
import ItemDropdown from "../components/ItemDropdown.vue";
import { useStore } from "vuex";
import { useRouter } from "vue-router";

// Define props and emits
const props = defineProps({
  selectedProduct: Object
});

const emit = defineEmits(['drop-off-confirmed']);

// Use store and router
const store = useStore();
const router = useRouter();
const supabase = inject('supabase');

// Create refs to store selected items and new items
const selectedItems = ref([]);
const newCreatedItems = ref([]);
const user = ref(null);
const loading = ref(false);

// Check if user can confirm drop-off
const canConfirm = computed(() => 
  (selectedItems.value.length > 0 || newCreatedItems.value.length > 0) && !loading.value
);

// Access selected product from props or localStorage as fallback
const product = computed(() => {
  if (props.selectedProduct) {
    return props.selectedProduct;
  }
  return JSON.parse(localStorage.getItem('savedProduct'));
});

onMounted(async () => {
  await checkAuth();
});

const checkAuth = async () => {
  const { data: { session }, error } = await supabase.auth.getSession();
  
  if (error || !session?.user || session.user?.user_metadata?.role !== "V") {
    router.push("/");
    return;
  }
  
  user.value = session.user;
  
  // Set up auth state listener
  const { data: authListener } = supabase.auth.onAuthStateChange((event, session) => {
    if (session?.user && session.user?.user_metadata?.role === "V") {
      user.value = session.user;
    } else {
      router.push("/");
    }
  });
  
  return () => authListener?.unsubscribe();
};

// Update functions to receive data from child components
const updateSelectedItems = (items) => {
  selectedItems.value = items;
};

const updateNewItems = (items) => {
  newCreatedItems.value = items;
};

// Function to confirm drop-off
const confirmDropOff = async () => {
  if (!canConfirm.value) return;
  
  try {
    loading.value = true;
    
    const volunteerID = user.value?.id;
    const productID = product.value?.productId;
    
    if (!volunteerID || !productID) {
      throw new Error("Missing required information");
    }
    
    const payload = {
      volunteerID,
      productID,
      items: selectedItems.value || [],
      newItems: newCreatedItems.value || []
    };
    
    await store.dispatch('apiRequest', {
      method: 'post',
      endpoint: 'http://localhost:8000/confirm-drop-off',
      data: payload
    });
    
    // Clear saved data
    localStorage.removeItem('savedProduct');
    localStorage.removeItem('deliveryConfirmed');
    
    // Emit event to parent
    emit('drop-off-confirmed');
  } catch (error) {
    console.error('Failed to confirm drop-off:', error);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  width: 100%;
  margin: 0 auto;
}

.title {
  align-self: flex-start;
  font-weight: 600;
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.confirm-button {
  width: 100%;
  max-width: 300px;
  border-radius: 8px;
  padding: 0.75rem;
  font-size: 1rem;
  background-color: #f59e0b;
  color: white;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: 1rem;
}

.confirm-button:hover:not(:disabled) {
  background-color: #d97706;
}

.confirm-button:disabled {
  background-color: #e5e7eb;
  color: #9ca3af;
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .container {
    padding: 0.75rem;
  }
  
  .title {
    font-size: 1.25rem;
  }
  
  .confirm-button {
    max-width: 100%;
  }
}
</style>