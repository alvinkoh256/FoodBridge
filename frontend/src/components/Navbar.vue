<template>
    <div class="navbar">
      <div
        class="nav-tab"
        :class="{ 'active': modelValue === 'create' }"
        @click="updateTab('create')"
      >
        Create Listing
      </div>
      <div
        class="nav-tab"
        :class="{ 'active': modelValue === 'posted' }"
        @click="updateTab('posted')"
      >
        Posted Listings
      </div>
    </div>
  </template>
  
  <script setup>
  import { defineProps, defineEmits } from 'vue';
  
  const props = defineProps({
    modelValue: {
      type: String,
      required: true
    }
  });
  
  const emit = defineEmits(['update:modelValue']);
  
  const updateTab = (tab) => {
    emit('update:modelValue', tab);
  };
  </script>
  
<style scoped>
  .navbar {
    display: flex;
    background-color: #f5f5f5;
    border-bottom: 1px solid #ddd;
    border-radius: 15px 15px 0px 0px;
  }
  
  .nav-tab {
    padding: 15px 25px;
    cursor: pointer;
    font-weight: bold;
    text-align: center;
    color: black;
    border-radius: 15px 15px 0px 0px;
    flex: 1;
    transition: all 0.5s ease-out;
  }
  
  .nav-tab.active {
    background-color: black;
    border-bottom: 3px solid #000;
    color: #f5f5f5;
  }
  
</style>