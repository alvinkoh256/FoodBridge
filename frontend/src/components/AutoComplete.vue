<template>
  <div class="autocomplete-container">
    <input
      ref="autocompleteInput"
      id="autocomplete"
      type="text"
      class="autocomplete-input text-black"
      placeholder="Enter an address"
      @input="getSuggestions"
    />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';

export default {
  name: 'Autocomplete',
  setup() {
    const address = ref('');
    const autocompleteInput = ref(null);

    return {
      address,
      autocompleteInput
    };
  },
  data() {
    return {
      apiKey: import.meta.env.VITE_GOOGLE_PLACES_API_KEY
    };
  },
  mounted() {
    this.initGooglePlace();
  },
  methods: {
    initGooglePlace() {
      return new Promise((resolve, reject) => {
        if (window.google && window.google.maps) {
          this.initAutoComplete();
          resolve();
          return;
        }

        const script = document.createElement('script');
        script.src = `https://maps.googleapis.com/maps/api/js?key=${this.apiKey}&libraries=places`;
        script.async = true;
        script.defer = true;
        
        script.onload = () => {
          this.initAutoComplete();
          resolve();
        };
        
        script.onerror = () => {
          reject(new Error('Google Maps API failed to load.'));
        };
        
        document.head.appendChild(script);
      });
    },
    initAutoComplete() {
      if (!this.$refs.autocompleteInput) return;

      const autocomplete = new google.maps.places.Autocomplete(this.$refs.autocompleteInput, {
        types: ['geocode'],
        componentRestrictions: { country: 'sg' }
      });

      autocomplete.addListener('place_changed', () => {
        const place = autocomplete.getPlace();
        if (place && place.formatted_address) {
          this.address = place.formatted_address;
          this.$emit('location-selected', place.formatted_address);
        }
      });
    }
  }
};
</script>

<style scoped>
.autocomplete-container {
  position: relative;
  width: 100%;
}
.autocomplete-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.suggestions-list {
  position: absolute;
  width: 100%;
  max-height: 200px;
  overflow-y: auto;
  background: white;
  border: 1px solid #ccc;
  border-top: none;
  z-index: 10;
}
.suggestion-item {
  padding: 8px 12px;
  cursor: pointer;
}
.suggestion-item:hover {
  background-color: #f0f0f0;
}
</style>