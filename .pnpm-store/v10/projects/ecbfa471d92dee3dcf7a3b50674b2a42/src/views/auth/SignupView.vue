<template>
  <div class="min-h-screen flex items-center justify-center bg-linear-to-br from-blue-50 via-white to-teal-50 p-4 py-8">
    <Card class="w-full max-w-md my-8">
      <CardHeader class="space-y-1 text-center">
        <div class="flex justify-center mb-4">
          <div class="p-3 bg-teal-600 rounded-xl">
            <Activity class="w-8 h-8 text-white" />
          </div>
        </div>
        <CardTitle class="text-2xl">Create your account</CardTitle>
        <CardDescription>Enter your details to get started</CardDescription>
      </CardHeader>
      <CardContent v-if="!isSuccess" class="space-y-4">
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div class="grid grid-cols-2 gap-3">
            <div class="space-y-2">
              <Label for="firstName">First Name</Label>
              <Input id="firstName" placeholder="John" v-model="formData.firstName" required :disabled="isLoading" />
            </div>
            <div class="space-y-2">
              <Label for="lastName">Last Name</Label>
              <Input id="lastName" placeholder="Doe" v-model="formData.lastName" required :disabled="isLoading" />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div class="space-y-2">
              <Label for="username">Username</Label>
              <Input id="username" type="text" placeholder="johndoe123" v-model="formData.username" required :disabled="isLoading" />
            </div>
            <div class="space-y-2">
              <Label for="phone_number">Phone</Label>
              <Input id="phone_number" type="tel" placeholder="+1234567890" v-model="formData.phone_number" required :disabled="isLoading" />
            </div>
          </div>

          <div class="space-y-2">
            <Label for="email">Email</Label>
            <Input id="email" type="email" placeholder="your.email@example.com" v-model="formData.email" required :disabled="isLoading" />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div class="space-y-2">
              <Label for="date_of_birth">Date of Birth</Label>
              <Input id="date_of_birth" type="date" v-model="formData.date_of_birth" required :disabled="isLoading" />
            </div>
            <div class="space-y-2">
              <Label for="blood_type">Blood Type</Label>
              <select id="blood_type" v-model="formData.blood_type" required :disabled="isLoading" class="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50">
                <option value="" disabled>Select</option>
                <option value="A+">A+</option>
                <option value="A-">A-</option>
                <option value="B+">B+</option>
                <option value="B-">B-</option>
                <option value="AB+">AB+</option>
                <option value="AB-">AB-</option>
                <option value="O+">O+</option>
                <option value="O-">O-</option>
              </select>
            </div>
          </div>

          <div class="space-y-2">
            <Label for="gender">Gender</Label>
            <select id="gender" v-model="formData.gender" required :disabled="isLoading" class="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50">
              <option value="" disabled>Select</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
          </div>

          <div class="space-y-2">
            <Label for="password">Password</Label>
            <Input id="password" type="password" placeholder="••••••••" v-model="formData.password" required :disabled="isLoading" />
          </div>

          <div class="space-y-2">
            <Label for="confirmPassword">Confirm Password</Label>
            <Input id="confirmPassword" type="password" placeholder="••••••••" v-model="formData.confirmPassword" required :disabled="isLoading" />
          </div>

          <Button type="submit" class="w-full bg-teal-600 hover:bg-teal-700" :disabled="isLoading">
            {{ isLoading ? 'Creating account...' : 'Create Account' }}
          </Button>
          
          <div v-if="errorMessage" class="text-red-500 text-sm text-center mt-2 whitespace-pre-wrap">
            {{ errorMessage }}
          </div>
        </form>

        <div class="text-center text-sm mt-6">
          <span class="text-gray-500">Already have an account? </span>
          <button @click="router.push('/login')" class="text-blue-600 hover:underline font-medium" :disabled="isLoading">
            Sign in
          </button>
        </div>
      </CardContent>
      
      <CardContent v-else class="space-y-6 py-8">
        <div class="text-center space-y-4">
          <p class="text-gray-600">{{ successMessage }}</p>
          <Button @click="router.push('/login')" class="w-full bg-teal-600 hover:bg-teal-700">
            Go to Login
          </Button>
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { getDefaultRouteForRole, useAuth } from "@/composables/useAuth";

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Activity } from "lucide-vue-next";

const router = useRouter();
const { register, user } = useAuth();

const formData = reactive({
  username: "",
  email: "",
  password: "",
  confirmPassword: "",
  firstName: "",
  lastName: "",
  phone_number: "",
  date_of_birth: "",
  blood_type: "",
  gender: "",
});

const isLoading = ref(false);
const errorMessage = ref("");
const isSuccess = ref(false);
const successMessage = ref("");

const handleSubmit = async () => {
  if (formData.password !== formData.confirmPassword) {
    errorMessage.value = 'Passwords do not match';
    return;
  }

  if (formData.password.length < 6) {
    errorMessage.value = 'Password must be at least 6 characters';
    return;
  }

  isLoading.value = true;
  errorMessage.value = "";
  try {
    const signupData = {
      username: formData.username,
      email: formData.email,
      password: formData.password,
      password_confirm: formData.confirmPassword,
      first_name: formData.firstName,
      last_name: formData.lastName,
      phone_number: formData.phone_number,
      date_of_birth: formData.date_of_birth,
      blood_type: formData.blood_type,
      gender: formData.gender,
    };
    const response = await register(signupData);
    isSuccess.value = true;
    successMessage.value = response?.detail || "Registration successful. Please verify your email, then log in.";
  } catch (error) {
    const data = error.response?.data;
    const dataErrors = data?.errors || data?.details || data;
    
    if (dataErrors) {
        const errors = [];
        for (const [key, val] of Object.entries(dataErrors)) {
            let msg = Array.isArray(val) ? val.join(', ') : val;
            const noPrefixKeys = ['non_field_errors', 'detail', 'uid', 'token'];
            const prefix = noPrefixKeys.includes(key) ? '' : `${key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ')}: `;
            errors.push(`${prefix}${msg}`);
        }
        errorMessage.value = errors.join('\n');
    } else if (data?.detail) {
        errorMessage.value = data.detail;
    } else if (data?.message) {
        errorMessage.value = data.message;
    } else {
        errorMessage.value = "Signup failed. Please try again.";
    }
  } finally {
    isLoading.value = false;
  }
};

</script>
