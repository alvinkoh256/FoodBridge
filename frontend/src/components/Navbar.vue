<template>
  <nav class="navbar">
    <div class="navbar-content">
      <div class="navbar-logo">
        <img src="../assets/Foodbridge.png" alt="Foodbridge Logo">
      </div>
      
      <div class="navbar-menu" :class="{ 'is-active': isMobileMenuOpen }">
        <div 
          class="navbar-item" 
          :class="{ 'active': modelValue === 'overview' }"
          @click="updateTab('overview')"
        >
          {{ tabNames.overview }}
        </div>
        <div 
          class="navbar-item" 
          :class="{ 'active': modelValue === 'listings' }"
          @click="updateTab('listings')"
        >
          {{ tabNames.listings }}
        </div>
      </div>
      
      <div class="navbar-actions">
        <button class="btn-logout" @click="handleLogout">
          Log Out
        </button>
        <button class="btn-menu" @click="toggleMobileMenu">
          <span></span>
          <span></span>
          <span></span>
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { defineProps, defineEmits, ref } from 'vue';

const props = defineProps({
  modelValue: {
    type: String,
    required: true
  },
  tabNames: {
    type: Object,
    required: false,
    default: () => ({
      overview: 'Current Listings',
      listings: 'Create Listing'
    })
  }
});

const emit = defineEmits(['update:modelValue', 'logout']);
const isMobileMenuOpen = ref(false);

const updateTab = (tab) => {
  emit('update:modelValue', tab);
  isMobileMenuOpen.value = false;
};

const handleLogout = () => {
  emit('logout');
};

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
};
</script>

<style scoped>
.navbar {
  width: 100%;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  height: 64px;
}

.navbar-logo {
  display: flex;
  align-items: center;
}

.navbar-logo img {
  max-height: 70px;
  width: auto;
}

.navbar-menu {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.navbar-item {
  color: #6b7280;
  font-weight: 500;
  cursor: pointer;
  position: relative;
  padding: 0.5rem 0;
  transition: color 0.2s ease;
}

.navbar-item:hover {
  color: #111827;
}

.navbar-item.active {
  color: #111827;
  font-weight: 600;
}

.navbar-item.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #111827;
  border-radius: 1px;
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-logout {
  padding: 0.5rem 1rem;
  color: #f43f5e;
  background-color: transparent;
  border: 1px solid #f43f5e;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-logout:hover {
  background-color: #f43f5e;
  color: white;
}

.btn-menu {
  display: none;
  flex-direction: column;
  justify-content: space-between;
  height: 20px;
  width: 24px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
}

.btn-menu span {
  height: 2px;
  width: 100%;
  background-color: #111827;
  border-radius: 1px;
  transition: all 0.3s ease;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .navbar-menu {
    position: absolute;
    top: 64px;
    left: 0;
    width: 100%;
    flex-direction: column;
    background-color: white;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    padding: 1rem 0;
    gap: 1rem;
    transform: translateY(-100%);
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
    z-index: 50;
  }

  .navbar-menu.is-active {
    transform: translateY(0);
    opacity: 1;
    visibility: visible;
  }

  .btn-menu {
    display: flex;
  }

  .btn-menu span:nth-child(1) {
    transform: rotate(0) translateY(0);
  }

  .btn-menu span:nth-child(2) {
    opacity: 1;
  }

  .btn-menu span:nth-child(3) {
    transform: rotate(0) translateY(0);
  }

  .is-active + .navbar-actions .btn-menu span:nth-child(1) {
    transform: rotate(45deg) translateY(6px);
  }

  .is-active + .navbar-actions .btn-menu span:nth-child(2) {
    opacity: 0;
  }

  .is-active + .navbar-actions .btn-menu span:nth-child(3) {
    transform: rotate(-45deg) translateY(-6px);
  }
}
</style>