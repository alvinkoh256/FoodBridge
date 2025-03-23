<template>
  <div class="login-container">
    <div class="big-screen">
      <div class="login-form">
        <h1 class="text-black text-3xl">Sign in to Your Account</h1>
        <div class="mb-5">
          <SelectButton @selection-changed="handleSelectionChange"/>
        </div>
        <p class="flex flex-col gap-2">
          <label for="email" class="text-black font-bold text-left pl-1">Email</label>
          <InputText id="email" v-model="email"/>
        </p>
        <p class="flex flex-col gap-2">
          <label for="password" class="text-black font-bold text-left pl-1">Password</label>
          <Password id="password" v-model="password" toggleMask :feedback="false"/>
        </p>
        <p>
          <Button label="Login" class="p-button-rounded w-48 md:w-2/3" @click="signIn" severity="success"/>
        </p>
        <p v-if="errorMessage" class="text-red-600 font-bold">
          {{ errorMessage }}
        </p>
        <p class="text-black">
          Don't have an account? 
          <router-link to="/register" class="register-link">Register Here</router-link>
        </p>
      </div>
      <div class="logo">
        <img src="../assets/logo.jpg" class="logo-img"/>
        <p class="logo-text text-white text-5xl font-bold">Begin today, <br>For tomorrow</p>
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
const role = ref('donor');
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
    errorMessage.value = `You are registered as a ${userRole}, not a ${role.value}`;
    await signOut(); // Logout user
    return;
  }

  if (userRole === 'donor') {
    router.push('/home/donor');
  } else {
    router.push('/home');
  }
};

const signOut = async () => {
  store.dispatch('logout'); // Clear and logout user data
  router.push('/'); // Redirect to login page
};

</script>

  <style scoped>

  @keyframes gradient-animation {
    0% {
      background-position: 0% 50%;
    }
    50% {
      background-position: 100% 50%;
    }
    100% {
      background-position: 0% 50%;
	}
}

  @media (max-width: 1023px) {
  .logo {
    position: absolute;
    display: none;
    top: 20px;
    left: 20px;
    font-size: 20px;
    font-family: Roboto Flex;
    color: white;
  }


  .login-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100%;
    width: 100%;
    padding: 2rem;
    box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    
    background: linear-gradient(90deg, #ff7e5f, #feb47b, #ffd56b);

    background-size: 600% 600%;
    animation: gradient-animation 25s ease infinite;
  }

  .login-form {
    width: 100%;
    max-width: 400px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    padding: 70px 30px 40px 30px;
    border-radius: 25px;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
  }
  .big-screen{
    display: flex;
    justify-content: center;
    align-items: center;
  }
}

@media (min-width: 1024px) {
  .login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    width: 100%;
    padding: 2rem;
    box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    
    background: linear-gradient(90deg, #ff7e5f, #feb47b, #ffd56b);



    background-size: 600% 600%;
    animation: gradient-animation 25s ease infinite;
  }

  .login-form {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 2rem;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
  }

  .login-form > * {
    width: 100%;
    max-width: 400px;
  }

  .logo {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 97%;
    width: 50%;
    max-width: 700px;
  }

  .logo-img {
    width: 100%;
    height: 100%;
    object-fit: cover; 
    border-radius: 30px;
  }

  .logo-text {
    position: absolute;
    left: 55%;
    text-align: left;
    line-height: 1.5;
    text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.4);
  }

  .big-screen{
    display: flex;
    flex-direction: row;
    background: #fff;
    gap: 2em;
    width: 90%;
    max-width: 1400px;
    height: 100%;
    align-items: center;
    border-radius: 40px;
    padding-left: 2rem;
    padding-right: 2rem;
  }
}
  
  h1 {
    text-align: left;
    margin-bottom: 1rem;
  }
  
  .login-form p {
    margin-bottom: 1rem;
  }
  
  .error-message {
    color: red;
    text-align: center;
  }

  :deep .p-inputtext,
  :deep .p-password {
    width: 100%;
    max-width: 400px;
    border: 0 none;
    border-radius: 0;
    transition: all 0.2s;
    background: transparent;
    color: black;
    border-bottom: 1px solid black;
  }

  :deep .p-inputtext:focus,
  :deep .p-password:focus {
    outline: 0 none;
  }

  </style>