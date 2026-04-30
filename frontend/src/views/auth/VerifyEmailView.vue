<template>
  <div class="min-h-screen flex items-center justify-center bg-linear-to-br from-blue-50 via-white to-teal-50 p-4">
    <Card class="w-full max-w-md">
      <CardHeader class="space-y-1 text-center">
        <div class="flex justify-center mb-4">
          <div class="p-3 bg-teal-600 rounded-xl">
            <Activity class="w-8 h-8 text-white" />
          </div>
        </div>
        <CardTitle class="text-2xl">Email Verification</CardTitle>
        <CardDescription>We are verifying your email address</CardDescription>
      </CardHeader>
      
      <CardContent class="space-y-6 py-8">
        <div v-if="isLoading" class="text-center space-y-4">
          <p class="text-gray-600">Please wait while we verify your email...</p>
        </div>
        <div v-else-if="errorMessage" class="text-center space-y-4">
          <div class="text-red-500 font-medium">{{ errorMessage }}</div>
          <Button @click="router.push('/login')" class="w-full bg-teal-600 hover:bg-teal-700">
            Go to Login
          </Button>
        </div>
        <div v-else class="text-center space-y-4">
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
import { Button } from "@/components/ui/button";
import { Activity } from "lucide-vue-next";

const route = useRoute();
const router = useRouter();
const { verifyEmail } = useAuth();

const isLoading = ref(true);
const errorMessage = ref("");
const successMessage = ref("");

onMounted(async () => {
  const { uid, token } = route.query;
  
  if (!uid || !token) {
    errorMessage.value = "Invalid or missing verification link parameters.";
    isLoading.value = false;
    return;
  }

  try {
    const res = await verifyEmail(uid, token);
    successMessage.value = res.detail || "Email has been verified successfully.";
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
        errorMessage.value = "Failed to verify email. The link might be invalid or expired.";
    }
  } finally {
    isLoading.value = false;
  }
});
</script>
