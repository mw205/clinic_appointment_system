<template>
  <div class="min-h-screen flex items-center justify-center bg-linear-to-br from-blue-50 via-white to-teal-50 p-4">
    <Card class="w-full max-w-md">
      <CardHeader class="space-y-1 text-center">
        <div class="flex justify-center mb-4">
          <div class="p-3 bg-teal-600 rounded-xl">
            <Activity class="w-8 h-8 text-white" />
          </div>
        </div>
        <CardTitle class="text-2xl">Reset Password</CardTitle>
        <CardDescription>Create a new password for your account</CardDescription>
      </CardHeader>
      
      <CardContent class="space-y-4">
        <div v-if="!isValidLink" class="text-center space-y-4 py-4">
          <p class="text-red-500 font-medium">{{ errorMessage || 'Invalid or missing reset link parameters.' }}</p>
          <Button @click="router.push('/login')" class="w-full bg-teal-600 hover:bg-teal-700">
            Go to Login
          </Button>
        </div>

        <form v-else-if="!isSuccess" @submit.prevent="handleSubmit" class="space-y-4">
          <div class="space-y-2">
            <Label for="password">New Password</Label>
            <Input
              id="password"
              type="password"
              placeholder="••••••••"
              v-model="password"
              required
              :disabled="isLoading"
            />
          </div>

          <div class="space-y-2">
            <Label for="confirmPassword">Confirm New Password</Label>
            <Input
              id="confirmPassword"
              type="password"
              placeholder="••••••••"
              v-model="confirmPassword"
              required
              :disabled="isLoading"
            />
          </div>

          <Button type="submit" class="w-full bg-teal-600 hover:bg-teal-700" :disabled="isLoading">
            {{ isLoading ? 'Resetting...' : 'Reset Password' }}
          </Button>
          
          <div v-if="errorMessage" class="text-red-500 text-sm text-center mt-2 whitespace-pre-wrap">
            {{ errorMessage }}
          </div>
        </form>

        <div v-else class="text-center space-y-4 py-4">
          <p class="text-green-600 font-medium">{{ successMessage }}</p>
          <Button @click="router.push('/login')" class="w-full bg-teal-600 hover:bg-teal-700">
            Go to Login
          </Button>
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuth } from "@/composables/useAuth";

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Activity } from "lucide-vue-next";

const route = useRoute();
const router = useRouter();
const { resetPassword } = useAuth();

const password = ref("");
const confirmPassword = ref("");
const isLoading = ref(false);
const isSuccess = ref(false);
const isValidLink = ref(true);
const errorMessage = ref("");
const successMessage = ref("");

const uid = ref("");
const token = ref("");

onMounted(() => {
  uid.value = route.query.uid;
  token.value = route.query.token;
  
  if (!uid.value || !token.value) {
    isValidLink.value = false;
  }
});

const handleSubmit = async () => {
  if (password.value !== confirmPassword.value) {
    errorMessage.value = "Passwords do not match.";
    return;
  }

  if (password.value.length < 6) {
    errorMessage.value = "Password must be at least 6 characters.";
    return;
  }

  isLoading.value = true;
  errorMessage.value = "";
  
  try {
    const res = await resetPassword(uid.value, token.value, password.value, confirmPassword.value);
    isSuccess.value = true;
    successMessage.value = res.detail || "Password has been reset successfully.";
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
        errorMessage.value = "Failed to reset password. The link might be invalid or expired.";
    }
  } finally {
    isLoading.value = false;
  }
};
</script>
