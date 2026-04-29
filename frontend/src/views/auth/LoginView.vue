<template>
  <div class="min-h-screen flex items-center justify-center bg-linear-to-br from-blue-50 via-white to-teal-50 p-4">
    <Card class="w-full max-w-md">
      <CardHeader class="space-y-1 text-center">
        <div class="flex justify-center mb-4">
          <div class="p-3 bg-blue-600 rounded-xl">
            <Activity class="w-8 h-8 text-white" />
          </div>
        </div>
        <CardTitle class="text-2xl">Welcome to HealthCare Clinic</CardTitle>
        <CardDescription>Sign in to manage your appointments</CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div class="space-y-2">
            <Label for="username">Username</Label>
            <Input id="username" type="text" placeholder="Enter your username" v-model="username" required
              :disabled="isLoading" />
          </div>
          <div class="space-y-2">
            <Label for="password">Password</Label>
            <Input id="password" type="password" placeholder="••••••••" v-model="password" required
              :disabled="isLoading" />
          </div>
          <Button type="submit" class="w-full bg-blue-600 hover:bg-blue-700" :disabled="isLoading">
            {{ isLoading ? 'Signing in...' : 'Sign In' }}
          </Button>

          <div v-if="errorMessage" class="text-red-500 text-sm text-center mt-2">
            {{ errorMessage }}
          </div>
        </form>

        <div class="relative">
          <div class="absolute inset-0 flex items-center">
            <span class="w-full border-t" />
          </div>
          <div class="relative flex justify-center text-xs uppercase">
            <span class="bg-white px-2 text-gray-500">Or continue with</span>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <Button variant="outline" @click="handleSocialLogin('google')" :disabled="isLoading">
            <Chrome class="mr-2 h-4 w-4" />
            Google
          </Button>
          <Button variant="outline" @click="handleSocialLogin('facebook')" :disabled="isLoading">
            <Facebook class="mr-2 h-4 w-4" />
            Facebook
          </Button>
        </div>

        <div class="text-center text-sm">
          <span class="text-gray-500">Don't have an account? </span>
          <button @click="router.push('/signup')" class="text-blue-600 hover:underline font-medium"
            :disabled="isLoading">
            Sign up
          </button>
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup>
import { getDefaultRouteForRole, useAuth } from "@/composables/useAuth";
import { ref } from "vue";
import { useRouter } from "vue-router";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Activity, Chrome, Facebook } from "lucide-vue-next";

const router = useRouter();
const { login, loginWithSocial, user, getCurrentUserProfile } = useAuth();

const username = ref("");
const password = ref("");
const isLoading = ref(false);
const errorMessage = ref("");

const handleLogin = async () => {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    await login(username.value, password.value);
    await getCurrentUserProfile();
    router.push(getDefaultRouteForRole(user.value?.primary_role));
  } catch (error) {
    const data = error.response?.data;
    const dataErrors = data?.errors || data?.details;

    if (dataErrors) {
      const errors = [];
      for (const [key, val] of Object.entries(dataErrors)) {
        if (Array.isArray(val)) {
          errors.push(`${key === 'non_field_errors' ? '' : key + ': '}${val.join(', ')}`);
        } else {
          errors.push(`${key === 'non_field_errors' ? '' : key + ': '}${val}`);
        }
      }
      errorMessage.value = errors.join('\n');
    } else if (data?.detail) {
      errorMessage.value = data.detail;
    } else if (data?.message) {
      errorMessage.value = data.message;
    } else {
      errorMessage.value = "Invalid credentials. Please try again.";
    }
  } finally {
    isLoading.value = false;
  }
};

const handleSocialLogin = async (provider) => {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    await loginWithSocial(provider);
    router.push(getDefaultRouteForRole(user.value?.primary_role));
  } catch {
    errorMessage.value = "Social login failed";
  } finally {
    isLoading.value = false;
  }
};
</script>
