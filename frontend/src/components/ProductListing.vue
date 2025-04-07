<template>
    <div class="content">
      <div class="title">For You</div>
      <div class="divider"></div>

      <!-- Product List -->
      <div class="product-list">
        <div 
          v-for="product in products" 
          :key="product.productId"
          :class="['drop-off-item border-l-4 border-indigo-500', {'ongoing-status': product.productStatus === 'on-going'}]"
          @click="openDialog(product)"
        >
          <div class="profile-pic">
            <img :src="product.productPic" alt="Product Image">
          </div>
          <div class="drop-off-info">
            <div class="drop-off-location">
              Drop-off at {{ product.productCCDetails.hubName }}
            </div>
            <div class="drop-off-address">
              {{ product.productAddress }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Dialog -->
    <Dialog 
      v-model:visible="visible" 
      modal 
      header="Drop-off Details" 
      :breakpoints="{'960px': '95vw'}" 
      :style="{ width: '75rem', maxWidth: '95vw' }"
    >
      <DialogContentVolunteer :product="selectedProduct"/>
    </Dialog>
</template>

<script setup>
    import { ref, inject, onMounted, onUnmounted } from "vue";
    import { useStore } from "vuex";
    import { useRouter } from "vue-router";
    import DialogContentVolunteer from "../components/DialogContentVolunteer.vue";
    import Dialog from "primevue/dialog";
</script>