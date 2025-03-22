<template>
  <div>
    <input v-model="email" type="email" placeholder="Email" />
    <input v-model="password" type="password" placeholder="Password" />
    <button @click="signUp">Sign Up</button>
    <button @click="signIn">Sign In</button>
    <p v-if="errorMessage">{{ errorMessage }}</p>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue';
import { useRouter } from 'vue-router';

// Inject the Supabase instance provided globally in main.js
const supabase = inject('supabase');

const email = ref('');
const password = ref('');
const errorMessage = ref('');
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
