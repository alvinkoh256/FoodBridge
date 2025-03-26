<template>
    <div class="toggle-container" :class="{ 'in': isIn }" @click="toggleSelection">
      <div class="toggle-slider"></div>
      <div class="toggle-options">
        <div class="toggle-option out" :class="{ 'active': !isIn }" data-option="out">Donor</div>
        <div class="toggle-option" :class="{ 'active': isIn }" data-option="in">Volunteer</div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: "SelectButton",
    data() {
      return {
        isIn: false
      };
    },
    methods: {
      toggleSelection() {
        this.isIn = !this.isIn;
        this.$emit('selection-changed', this.isIn ? 'volunteer' : 'donor');
      }
    }
  };
  </script>
  
  <style scoped>
  .toggle-container {
    position: relative;
    width: 100%;
    height: 60px;
    border-radius: 30px;
    background-color: #000;
    overflow: hidden;
    cursor: pointer;
    border: 2px solid #000;
  }
  
  .toggle-slider {
    position: absolute;
    width: 45%;  /* Reduced from 50% */
    height: 80%;  /* Reduced from 90% */
    border-radius: 30px;
    background-color: #fff;
    transition: transform 0.3s ease;
    top: 10%; 
    left: 2.5%;  /* Adds a small margin on the left for "OUT" position */
    right: 2.5%; 
    }
  
  .toggle-options {
    display: flex;
    width: 100%;
    height: 100%;
  }
  
  .toggle-option {
    width: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-weight: bold;
    z-index: 2;
    transition: color 0.3s ease;
  }
  
  .toggle-option.active {
    color: #f8b100;
  }
  
  .toggle-option.out.active {
    color: #ff3b30;
  }
  
  .out {
    color: #fff;
  }
  
  /* Initial state - OUT selected */
  .toggle-slider {
    transform: translateX(0);
  }
  
  /* When IN is selected */
  .toggle-container.in .toggle-slider {
    transform: translateX(110%);
  }
  </style>