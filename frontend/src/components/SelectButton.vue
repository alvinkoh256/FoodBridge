<template>
  <div class="select-container">
    <div 
      class="select-slider" 
      :style="{ transform: `translateX(${sliderPosition}px)`, width: `${sliderWidth}px` }"
    ></div>
    <div class="select-options">
      <div 
        v-for="option in options" 
        :key="option.value"
        class="select-option" 
        :class="{ 'active': selectedOption === option.value }" 
        @click="selectOption(option.value)"
        ref="optionRefs"
      >
        {{ option.label }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "SelectButton",
  data() {
    return {
      selectedOption: "donor",
      options: [
        { value: "donor", label: "Donor" },
        { value: "volunteer", label: "Volunteer" },
        { value: "foodbank", label: "Bank" }
      ],
      sliderPosition: 0,
      sliderWidth: 0
    };
  },
  mounted() {
    this.calculateSliderPosition();
    window.addEventListener('resize', this.calculateSliderPosition);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.calculateSliderPosition);
  },
  methods: {
    selectOption(option) {
      this.selectedOption = option;
      this.$emit("selection-changed", option[0].toUpperCase());
      this.calculateSliderPosition();
    },
    calculateSliderPosition() {
      this.$nextTick(() => {
        if (!this.$refs.optionRefs) return;
        
        const activeIndex = this.options.findIndex(opt => opt.value === this.selectedOption);
        if (activeIndex === -1 || !this.$refs.optionRefs[activeIndex]) return;
        
        const activeElement = this.$refs.optionRefs[activeIndex];
        this.sliderWidth = activeElement.offsetWidth;
        this.sliderPosition = activeElement.offsetLeft;
      });
    }
  }
};
</script>

<style scoped>
.select-container {
  position: relative;
  width: 350px;
  height: 46px;
  border-radius: 23px;
  background-color: #f5f5f5;
  overflow: hidden;
  cursor: pointer;
  display: flex;
  transition: all 0.2s ease;
  border: 1px solid #e0e0e0;
}

.select-slider {
  position: absolute;
  height: 38px;
  border-radius: 19px;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  top: 4px;
}

.select-options {
  display: flex;
  width: 100%;
  height: 100%;
}

.select-option {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-weight: 500;
  font-size: 0.95rem;
  z-index: 2;
  transition: color 0.3s ease;
}

.select-option.active {
  color: #ff7e5f;
  font-weight: 600;
}

@media (max-width: 640px) {
  .select-container {
    height: 40px;
    border-radius: 20px;
  }
  
  .select-slider {
    height: 32px;
    border-radius: 16px;
    top: 4px;
  }
  
  .select-option {
    font-size: 0.85rem;
  }
}
</style>