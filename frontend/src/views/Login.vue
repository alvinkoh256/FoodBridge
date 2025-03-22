<template>
  <div class="login-container">
    <div class="big-screen">
      <div class="login-form">
        <h1 class="text-black text-3xl">Sign in to Your Account</h1>
        <p>
          <InputText v-model="email" placeholder="Email" />
        </p>
        <p>
          <Password v-model="password" toggleMask placeholder="Password" :feedback="false" />
        </p>
        <p>
          <Button label="Login" class="p-button-rounded w-48 md:w-2/3" style="background-color: #00B0C7; outline:none" @click="signIn" />
        </p>
        <p class="text-black">
          Don't have an account? 
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
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Button from 'primevue/button';

// Inject the Supabase instance provided globally in main.js
const supabase = inject('supabase');

const email = ref('');
const password = ref('');
const errorMessage = ref('');
const showPassword = ref(false);
const router = useRouter();

// Sign up method
const signUp = async () => {
  const { error } = await supabase.auth.signUp({ email: email.value, password: password.value });
  if (error) errorMessage.value = error.message;
  else router.push('/dashboard'); // Redirect to dashboard on successful sign up
};

// Sign in method
const signIn = async () => {
  const { error } = await supabase.auth.signInWithPassword({ email: email.value, password: password.value });
  if (error) errorMessage.value = error.message;
  else router.push('/dashboard'); // Redirect to dashboard on successful sign in
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
    display: hidden;
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
    
    background: linear-gradient(90deg, #ff7676, #f54ea2, #ffb3b3);

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
    
    background: linear-gradient(90deg, #ff7676, #f54ea2, #ffb3b3);
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
    text-align: center;
    margin-bottom: 2rem;
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
  }

  </style>