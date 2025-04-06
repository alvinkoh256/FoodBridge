<template>
  <div class="register-container">
    <div class="auth-card">
      <div class="form-section">
        <h1 class="title md:mt-45">Create an Account</h1>
        
        <div class="mb-6">
          <SelectButton @selection-changed="handleSelectionChange"/>
        </div>
        
        <div class="form-group">
          <label for="username" class="form-label">Username</label>
          <InputText id="username" v-model="username" class="form-input"/>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label for="email" class="form-label">Email</label>
            <InputText id="email" v-model="email" class="form-input"/>
          </div>
          
          <div class="form-group">
            <label for="phoneNumber" class="form-label">Phone No</label>
            <InputMask id="phoneNumber" v-model="phoneNumber" mask="+6599999999" placeholder="+6599999999" class="form-input"/>
          </div>
        </div>
        
        <div class="form-group">
          <label for="password" class="form-label">Password</label>
          <Password id="password" v-model="password" toggleMask :feedback="false" class="form-input"/>
        </div>
        
        <div class="form-group">
          <label for="confirmPassword" class="form-label">Confirm Password</label>
          <Password id="confirmPassword" v-model="confirmPassword" toggleMask :feedback="false" class="form-input"/>
        </div>
        
        <div class="form-group">
          <label for="address" class="form-label">Address</label>
          <AutoComplete id="address" ref="locationAutocomplete" @location-selected="updateLocation" class="form-input"/>
        </div>
        
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
        
        <Button label="Register" icon="pi pi-check" class="submit-button" @click="validateAndSignUp" severity="success"/>
        
        <div class="auth-link">
          Been Here Before?
          <router-link to="/">Click Here</router-link>
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
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Button from 'primevue/button';
import SelectButton from '../components/SelectButton.vue';
import AutoComplete from '../components/AutoComplete.vue';
import InputMask from 'primevue/inputmask';

// Inject the Supabase instance provided globally in main.js
const supabase = inject('supabase');

const username = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const errorMessage = ref('');
const role = ref('D');
const router = useRouter();
const location = ref('Current Location');
const phoneNumber = ref(''); 

const handleSelectionChange = (selection) => {
  role.value = selection;
};

const updateLocation = (selectedLocation) => {
  location.value = selectedLocation;
};

// Validate passwords match
const validatePasswords = () => {
  errorMessage.value = "";
  if (password.value !== confirmPassword.value) {
    errorMessage.value = 'Passwords do not match';
    return false;
  }
  return true;
};

// Validate and then sign up
const validateAndSignUp = async () => {
  if (validatePasswords()) {
    await signUp();
  }
};

// Sign up method
const signUp = async () => {
  const { data, error } = await supabase.auth.signUp({
    email: email.value,
    password: password.value,
    options: {
      data: { username: username.value, role: role.value, address: location.value, phoneNumber: phoneNumber.value }
    }
  });

  if (error) {
    errorMessage.value = error.message;
  } else {
    // Create the user data object for the OutSystems API
    const userData = {
      userId: data.user.id,
      userName: username.value,
      userEmail: email.value,
      userPhoneNumber: phoneNumber.value,  
      userAddress: location.value,
      userRole: role.value
    };

    console.log(userData);

    try {
      // Send the user data to the OutSystems API
      const response = await fetch('https://personal-tdqpornm.outsystemscloud.com/FoodBridge/rest/AccountInfoAPI/user', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      });

      if(role.value === 'F'){
        const responseAPI = await fetch('http://localhost:5010/public/hub/createFoodbank', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(userData)
        });
      }

      if (!response.ok) {
        throw new Error('API request failed');
      }
      
      if(response.ok && role.value === 'F') {
        const responseAPIData = await responseAPI.json();
        console.log('API response:', responseAPIData);
      }
      
      const responseData = await response.json();
      console.log('API response:', responseData);
    } catch (error) {
      console.error('Failed to send user data to API:', error);
    }

    // Save to Supabase profiles table
    await supabase.from('profiles').insert([
      { id: data.user.id, email: email.value, role: role.value, address: location.value, phone_number: phoneNumber.value }
    ]);

    router.push('/');
  }
};
</script>

<style scoped>
.register-container {
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
  padding: 2rem;
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
  margin-bottom: 1.25rem;
}

.form-row {
  width: 100%;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  margin-bottom: 1.25rem;
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
  max-width: 400px;
  text-align: center;
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
:deep .p-password,
:deep .p-inputmask {
  width: 100%;
  border: none;
  border-bottom: 2px solid #e5e7eb;
  background: transparent;
  transition: all 0.3s;
  padding: 0.75rem 0.5rem;
  color: #333;
}

:deep .p-button{
  overflow: visible;
}

:deep .p-inputtext:focus,
:deep .p-password:focus,
:deep .p-inputmask:focus {
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
    padding: 2.5rem;
  }
  
  .title {
    font-size: 2rem;
  }
  
  .form-row {
    flex-direction: row;
    gap: 1.5rem;
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
    padding: 3rem;
    overflow-y: auto;
    justify-content: center;
  }
  
  .brand-section {
    display: block;
    width: 50%;
  }
}
</style>