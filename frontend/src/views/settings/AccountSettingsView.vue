<template>
  <div class="space-y-6">
    <div>
      <h3 class="text-lg font-medium">Account</h3>
      <p class="text-sm text-gray-500">
        Update your account settings. Set your preferred contact information.
      </p>
    </div>
    
    <div class="border-t pt-6"></div>

    <form @submit.prevent="handleUpdateAccount" class="space-y-4">
      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-2">
          <Label for="firstName">First Name</Label>
          <Input id="firstName" v-model="accountForm.first_name" required :disabled="isLoading" />
        </div>
        <div class="space-y-2">
          <Label for="lastName">Last Name</Label>
          <Input id="lastName" v-model="accountForm.last_name" required :disabled="isLoading" />
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-2">
          <Label for="email">Email</Label>
          <Input id="email" type="email" v-model="accountForm.email" required :disabled="isLoading" />
        </div>
        <div class="space-y-2">
          <Label for="phone">Phone Number</Label>
          <Input id="phone" type="tel" v-model="accountForm.phone_number" :disabled="isLoading" />
        </div>
      </div>
      
      <div class="flex items-center space-x-2 py-2">
        <span class="text-sm font-medium">Email Verified:</span>
        <span :class="user?.email_verified ? 'text-green-600' : 'text-yellow-600'" class="text-sm font-semibold">
          {{ user?.email_verified ? 'Yes' : 'No' }}
        </span>
      </div>

      <Button type="submit" class="bg-teal-600 hover:bg-teal-700" :disabled="isLoading">
        {{ isLoading ? 'Saving...' : 'Update Account' }}
      </Button>
      
      <p v-if="accountSuccess" class="text-green-600 text-sm mt-2">Account updated successfully.</p>
      <div v-if="accountError" class="text-red-500 text-sm mt-2 whitespace-pre-wrap">{{ accountError }}</div>
    </form>

    <div class="border-t pt-6 mt-8"></div>

    <div>
      <h3 class="text-lg font-medium">Change Password</h3>
      <p class="text-sm text-gray-500">
        Update your password. You will be asked to log in again.
      </p>
    </div>

    <form @submit.prevent="handleChangePassword" class="space-y-4 max-w-md">
      <div class="space-y-2">
        <Label for="currentPassword">Current Password</Label>
        <Input id="currentPassword" type="password" v-model="passwordForm.current_password" required :disabled="isPasswordLoading" />
      </div>

      <div class="space-y-2">
        <Label for="newPassword">New Password</Label>
        <Input id="newPassword" type="password" v-model="passwordForm.new_password" required :disabled="isPasswordLoading" />
      </div>

      <div class="space-y-2">
        <Label for="confirmPassword">Confirm New Password</Label>
        <Input id="confirmPassword" type="password" v-model="passwordForm.new_password_confirm" required :disabled="isPasswordLoading" />
      </div>

      <Button type="submit" class="bg-teal-600 hover:bg-teal-700" :disabled="isPasswordLoading">
        {{ isPasswordLoading ? 'Changing...' : 'Change Password' }}
      </Button>

      <p v-if="passwordSuccess" class="text-green-600 text-sm mt-2">{{ passwordSuccess }}</p>
      <div v-if="passwordError" class="text-red-500 text-sm mt-2 whitespace-pre-wrap">{{ passwordError }}</div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { useAuth } from "@/composables/useAuth";

import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

const { user, updateAccount, changePassword } = useAuth();
const router = useRouter();

const isLoading = ref(false);
const accountSuccess = ref(false);
const accountError = ref("");

const isPasswordLoading = ref(false);
const passwordSuccess = ref("");
const passwordError = ref("");

const accountForm = reactive({
  first_name: "",
  last_name: "",
  email: "",
  phone_number: "",
});

const passwordForm = reactive({
  current_password: "",
  new_password: "",
  new_password_confirm: "",
});

const loadUserData = () => {
  if (user.value) {
    accountForm.first_name = user.value.first_name || "";
    accountForm.last_name = user.value.last_name || "";
    accountForm.email = user.value.email || "";
    accountForm.phone_number = user.value.phone_number || "";
  }
};

onMounted(() => {
  loadUserData();
});

watch(user, () => {
  loadUserData();
}, { deep: true });

const handleUpdateAccount = async () => {
  isLoading.value = true;
  accountError.value = "";
  accountSuccess.value = false;
  
  try {
    await updateAccount(accountForm);
    accountSuccess.value = true;
  } catch (error) {
    const data = error.response?.data;
    const dataErrors = data?.errors || data?.details || data;

    if (dataErrors && typeof dataErrors === 'object') {
        const errors = [];
        for (const [key, val] of Object.entries(dataErrors)) {
            let msg = Array.isArray(val) ? val.join(', ') : val;
            const noPrefixKeys = ['non_field_errors', 'detail'];
            const prefix = noPrefixKeys.includes(key) ? '' : `${key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ')}: `;
            errors.push(`${prefix}${msg}`);
        }
        accountError.value = errors.join('\n');
    } else {
        accountError.value = "Failed to update account.";
    }
  } finally {
    isLoading.value = false;
  }
};

const handleChangePassword = async () => {
  if (passwordForm.new_password !== passwordForm.new_password_confirm) {
    passwordError.value = "New passwords do not match.";
    return;
  }

  isPasswordLoading.value = true;
  passwordError.value = "";
  passwordSuccess.value = "";

  try {
    const res = await changePassword(
      passwordForm.current_password,
      passwordForm.new_password,
      passwordForm.new_password_confirm
    );
    passwordSuccess.value = res.detail || "Password changed. Redirecting to login...";
    setTimeout(() => {
      router.push('/login?message=password_changed');
    }, 2000);
  } catch (error) {
    const data = error.response?.data;
    const dataErrors = data?.errors || data?.details || data;

    if (dataErrors && typeof dataErrors === 'object') {
        const errors = [];
        for (const [key, val] of Object.entries(dataErrors)) {
            let msg = Array.isArray(val) ? val.join(', ') : val;
            const noPrefixKeys = ['non_field_errors', 'detail'];
            const prefix = noPrefixKeys.includes(key) ? '' : `${key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ')}: `;
            errors.push(`${prefix}${msg}`);
        }
        passwordError.value = errors.join('\n');
    } else {
        passwordError.value = "Failed to change password.";
    }
  } finally {
    isPasswordLoading.value = false;
  }
};
</script>
