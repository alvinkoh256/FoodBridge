<template>
  <div class="login-container">
    <div class="auth-card">
      <div class="form-section">
        <h1 class="title">Sign in to Your Account</h1>
        
        <div class="mb-6">
          <SelectButton @selection-changed="handleSelectionChange"/>
        </div>
        
        <div class="form-group">
          <label for="email" class="form-label">Email</label>
          <InputText id="email" v-model="email" class="form-input"/>
        </div>
        
        <div class="form-group">
          <label for="password" class="form-label">Password</label>
          <Password id="password" v-model="password" toggleMask :feedback="false" class="form-input"/>
        </div>
        
        <Button label="Login" class="submit-button" @click="signIn" severity="success"/>
        
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
        
        <div class="auth-link">
          Don't have an account? 
          <router-link to="/register">Register Here</router-link>
        </div>
      </div>
      
      <div class="brand-section">
        <img src="../assets/logo.jpg" alt="Logo" class="brand-image"/>
        <div class="brand-text">Begin today, <br>For tomorrow</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Button from 'primevue/button';
import SelectButton from '../components/SelectButton.vue';

// Inject the Supabase instance provided globally in main.js
const supabase = inject('supabase');
const email = ref('');
const password = ref('');
const errorMessage = ref('');
const role = ref('D');
const router = useRouter();
const store = useStore();

const handleSelectionChange = (selection) => {
  role.value = selection;
};

// Sign in method
const signIn = async () => {
  errorMessage.value = ''; // Reset error message

  // Step 1: Sign in user with email & password
  const { data, error } = await supabase.auth.signInWithPassword({
    email: email.value,
    password: password.value
  });

  if (error) {
    errorMessage.value = error.message;
    return;
  }

  // Step 2: Fetch the user's role from metadata
  const user = data.user;
  const userRole = user?.user_metadata?.role; // Get stored role

  if (!userRole) {
    errorMessage.value = 'User role not found.';
    await signOut();
    return;
  }

  if (userRole !== role.value) {
    errorMessage.value = `You are not registered as the chosen role`;
    await signOut(); // Logout user
    return;
  }

  if (userRole === 'D') {
    router.push('/home/donor');
  } 
  else if(userRole === 'F'){
    router.push('/home/bank');
  }
  else {
    router.push('/home');
  }
};

const signOut = async () => {
  store.dispatch('logout'); // Clear and logout user data
  router.push('/'); // Redirect to login page
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #ff7e5f, #feb47b, #ffd56b);
  background-size: 400% 400%;
  animation: gradient 15s ease infinite;
  padding: 1rem;
}

@keyframes gradient {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.auth-card {
  width: 100%;
  max-width: 1200px;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.form-section {
  padding: 2.5rem 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.title {
  font-size: 1.8rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 1.5rem;
  text-align: center;
}

.form-group {
  width: 100%;
  max-width: 400px;
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #333;
  text-align: left;
}

.submit-button {
  width: 100%;
  max-width: 400px;
  margin-top: 0.5rem;
  margin-bottom: 1rem;
  border-radius: 8px;
  height: 48px;
}

.error-message {
  color: #ef4444;
  font-weight: 600;
  margin: 1rem 0;
}

.auth-link {
  margin-top: 1.5rem;
  color: #333;
}

.auth-link a {
  color: #ff7e5f;
  font-weight: 600;
  text-decoration: none;
}

.auth-link a:hover {
  text-decoration: underline;
}

.brand-section {
  display: none;
  position: relative;
}

.brand-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.brand-text {
  position: absolute;
  top: 50%;
  left: 10%;
  transform: translateY(-50%);
  color: white;
  font-size: 2.5rem;
  font-weight: 700;
  line-height: 1.3;
  text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.5);
}

:deep .p-inputtext,
:deep .p-password {
  width: 100%;
  border: none;
  border-bottom: 2px solid #e5e7eb;
  background: transparent;
  transition: all 0.3s;
  padding: 0.75rem 0.5rem;
  color: #333;
}

:deep .p-inputtext:focus,
:deep .p-password:focus {
  border-bottom-color: #ff7e5f;
  box-shadow: none;
  outline: none;
}

:deep .p-password-input {
  width: 100%;
}

/* Responsive design */
@media (min-width: 768px) {
  .form-section {
    padding: 3rem;
  }
  
  .title {
    font-size: 2rem;
  }
}

@media (min-width: 1024px) {
  .auth-card {
    flex-direction: row;
    height: 85vh;
    max-height: 800px;
  }
  
  .form-section {
    width: 50%;
    justify-content: center;
  }
  
  .brand-section {
    display: block;
    width: 50%;
  }
}
</style>