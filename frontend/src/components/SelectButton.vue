<template>
  <div class="toggle-container">
    <div class="toggle-slider" :style="{ transform: `translateX(${sliderPosition}%)` }"></div>
    <div class="toggle-options">
      <div class="toggle-option" :class="{ 'active': selectedOption === 'donor' }" @click="selectOption('donor')">Donor</div>
      <div class="toggle-option" :class="{ 'active': selectedOption === 'volunteer' }" @click="selectOption('volunteer')">Volunteer</div>
      <div class="toggle-option" :class="{ 'active': selectedOption === 'bank' }" @click="selectOption('bank')">Bank</div>
    </div>
  </div>
</template>

<script>
export default {
  name: "SelectButton",
  data() {
    return {
      selectedOption: "donor",
      positions: {
        donor: 0,
        volunteer: 100,
        bank: 200
      }
    };
  },
  computed: {
    sliderPosition() {
      return this.positions[this.selectedOption];
    }
  },
  methods: {
    selectOption(option) {
      this.selectedOption = option;
      this.$emit("selection-changed", option[0].toUpperCase());
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
  display: flex;
  border: 2px solid #000;
}

.toggle-slider {
  position: absolute;
  width: 33%;
  height: 80%;
  border-radius: 30px;
  background-color: #fff;
  transition: transform 0.3s ease;
  top: 10%;
  left: 0.5%;
}

.toggle-options {
  display: flex;
  width: 100%;
  height: 100%;
}

.toggle-option {
  flex: 1;
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
</style>
