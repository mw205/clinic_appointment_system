<template>
  <div class="min-h-screen flex items-center justify-center bg-linear-to-br from-blue-50 via-white to-teal-50 p-4">
    <Card class="w-full max-w-md">
      <CardHeader class="space-y-1 text-center">
        <div class="flex justify-center mb-4">
          <div class="p-3 bg-teal-600 rounded-xl">
            <Activity class="w-8 h-8 text-white" />
          </div>
        </div>
        <CardTitle class="text-2xl">Forgot Password</CardTitle>
        <CardDescription>Enter your email to reset your password</CardDescription>
      </CardHeader>
      
      <CardContent class="space-y-4">
        <form v-if="!isSuccess" @submit.prevent="handleSubmit" class="space-y-4">
          <div class="space-y-2">
            <Label for="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="your.email@example.com"
              v-model="email"
              required
              :disabled="isLoading"
            />
          </div>

          <Button type="submit" class="w-full bg-teal-600 hover:bg-teal-700" :disabled="isLoading">
            {{ isLoading ? 'Sending...' : 'Send Reset Link' }}
          </Button>
          
          <div v-if="errorMessage" class="text-red-500 text-sm text-center mt-2 whitespace-pre-wrap">
            {{ errorMessage }}
          </div>
        </form>

        <div v-else class="text-center space-y-4 py-4">
          <p class="text-gray-600">{{ successMessage }}</p>
        </div>

        <div class="text-center text-sm pt-4 border-t mt-6">
          <span class="text-gray-500">Remember your password? </span>
          <button
            @click="router.push('/login')"
            class="text-blue-600 hover:underline font-medium"
            :disabled="isLoading"
          >
            Sign in
          </button>
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuth } from "@/composables/useAuth";

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Activity } from "lucide-vue-next";

const router = useRouter();
const { forgotPassword } = useAuth();

const email = ref("");
const isLoading = ref(false);
const isSuccess = ref(false);
const errorMessage = ref("");
const successMessage = ref("");

const handleSubmit = async () => {
  if (!email.value) return;

  isLoading.value = true;
  errorMessage.value = "";
  
  try {
    const res = await forgotPassword(email.value);
    isSuccess.value = true;
    successMessage.value = res.detail || "If an account with that email exists, a password reset link has been sent.";
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
        errorMessage.value = "Failed to request password reset. Please try again.";
    }
  } finally {
    isLoading.value = false;
  }
};
</script>
