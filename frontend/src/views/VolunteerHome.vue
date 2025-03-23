<template>
    <div class="home-container">
        <div class="header">
            <div class="section-title">Postings for you</div>
        </div>

        <div class="divider"></div>

        <div class="drop-off-item">
            <div class="profile-pic">
                <img src="../assets/logo.jpg" alt="Profile">
            </div>
            <div class="drop-off-info">
                <div class="drop-off-location text-black">Drop-off at (A CC)</div>
                <div class="drop-off-date">14:30 12-Mar-2025</div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { inject, onMounted } from 'vue';
import { useStore } from 'vuex';

const supabase = inject('supabase');
const store = useStore();
</script>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 1rem;
  background-color: #fff;
  border-radius: 8px;
}

.header {
  background-color: #4a86e8;
  color: white;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 20px;
}

.section-title {
  font-size: 25px;
  font-weight: bold;
}

.divider {
  border-top: 1px solid #ccc;
  margin: 20px 0;
}

.drop-off-item {
  display: flex;
  align-items: center;
  padding: 15px;
  background-color: white;
  border-radius: 5px;
  margin-bottom: 10px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.profile-pic {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #ddd;
  margin-right: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

img{
  object-fit: cover; /* Ensures the image covers the circle without distortion */
}

.drop-off-info {
  flex-grow: 1;
}

.drop-off-location {
  font-weight: bold;
  margin-bottom: 5px;
}

.drop-off-date {
  font-size: 12px;
  color: #666;
}
</style>
