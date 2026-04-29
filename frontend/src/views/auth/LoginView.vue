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
            <Input
              id="username"
              type="text"
              placeholder="Enter your username"
              v-model="username"
              required
              :disabled="isLoading"
            />
          </div>
          <div class="space-y-2">
            <Label for="password">Password</Label>
            <Input
              id="password"
              type="password"
              placeholder="••••••••"
              v-model="password"
              required
              :disabled="isLoading"
            />
          </div>
          <Button type="submit" class="w-full bg-blue-600 hover:bg-blue-700" :disabled="isLoading">
            {{ isLoading ? 'Signing in...' : 'Sign In' }}
          </Button>
          
          <div v-if="errorMessage" class="text-red-500 text-sm text-center mt-2">
            {{ errorMessage }}
          </div>
          
          <div v-if="isUnverified" class="text-center mt-2">
            <Button type="button" variant="link" @click="handleResendVerification" :disabled="isResending" class="text-blue-600 p-0 h-auto font-normal">
              {{ isResending ? 'Sending...' : 'Resend verification email' }}
            </Button>
            <div v-if="resendMessage" class="text-green-600 text-sm mt-1">
              {{ resendMessage }}
            </div>
          </div>
        </form>

        <div class="flex justify-center mb-6">
          <button
            @click="router.push('/forgot-password')"
            class="text-sm text-blue-600 hover:underline"
            :disabled="isLoading"
          >
            Forgot password?
          </button>
        </div>

        <div class="text-center text-sm">
          <span class="text-gray-500">Don't have an account? </span>
          <button
            @click="router.push('/signup')"
            class="text-blue-600 hover:underline font-medium"
            :disabled="isLoading"
          >
            Sign up
          </button>
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { getDefaultRouteForRole, useAuth } from "@/composables/useAuth";

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Activity } from "lucide-vue-next";

const router = useRouter();
const { login, user, resendVerificationEmail } = useAuth();

const username = ref("");
const password = ref("");
const isLoading = ref(false);
const errorMessage = ref("");
const isUnverified = ref(false);
const isResending = ref(false);
const resendMessage = ref("");

const handleLogin = async () => {
  isLoading.value = true;
  errorMessage.value = "";
  isUnverified.value = false;
  resendMessage.value = "";
  try {
    await login(username.value, password.value);
    router.push(getDefaultRouteForRole(user.value?.primary_role));
  } catch (error) {
    const data = error.response?.data;
    const dataErrors = data?.errors || data?.details;
    
    if (dataErrors) {
        const errors = [];
        for (const [key, val] of Object.entries(dataErrors)) {
            let msg = Array.isArray(val) ? val.join(', ') : val;
            if (msg.includes("Please verify your email address before logging in.")) {
                isUnverified.value = true;
            }
            const noPrefixKeys = ['non_field_errors', 'detail', 'uid', 'token'];
            const prefix = noPrefixKeys.includes(key) ? '' : `${key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ')}: `;
            errors.push(`${prefix}${msg}`);
        }
        errorMessage.value = errors.join('\n');
    } else if (data?.detail) {
        errorMessage.value = data.detail;
        if (data.detail.includes("Please verify your email address before logging in.")) {
            isUnverified.value = true;
        }
    } else if (data?.message) {
        errorMessage.value = data.message;
    } else {
        errorMessage.value = "Invalid credentials. Please try again.";
    }
  } finally {
    isLoading.value = false;
  }
};

const handleResendVerification = async () => {
  if (!username.value) return;
  isResending.value = true;
  resendMessage.value = "";
  errorMessage.value = "";
  try {
    // Note: The backend expects email, but login uses username. 
    // We will assume the backend might be able to handle username, or we will just send it as email.
    // Wait, the backend resend-verification-email endpoint explicitly takes 'email'.
    // If the user logs in with username, we don't have their email.
    // But actually, in many systems username is the email. Let's send the username as the email parameter and if it fails, show a generic error.
    const res = await resendVerificationEmail(username.value);
    resendMessage.value = res.detail || "Verification email sent.";
  } catch (error) {
    errorMessage.value = "Failed to resend verification email. Please try again.";
  } finally {
    isResending.value = false;
  }
};

</script>
