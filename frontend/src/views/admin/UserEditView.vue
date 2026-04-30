<template>
  <div class="flex-1 space-y-4 p-4 md:p-8 pt-6">
    <div class="flex items-center justify-between space-y-2 mb-6">
      <div class="flex items-center space-x-2">
        <Button variant="outline" size="icon" @click="router.push('/admin/users')">
          <ArrowLeft class="h-4 w-4" />
        </Button>
        <h2 class="text-3xl font-bold tracking-tight">Edit User</h2>
      </div>
    </div>

    <Card class="max-w-2xl">
      <CardHeader>
        <CardTitle>User Details</CardTitle>
        <CardDescription>
          Update role and status for {{ user?.username || 'this user' }}.
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        <div v-if="isLoading" class="text-gray-500 py-4">
          Loading user details...
        </div>
        <div v-else-if="fetchError" class="text-red-500 py-4">
          {{ fetchError }}
        </div>
        <form v-else @submit.prevent="handleUpdate" class="space-y-6">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <Label class="text-xs text-gray-500 uppercase">Username</Label>
              <div class="font-medium mt-1">{{ user.username }}</div>
            </div>
            <div>
              <Label class="text-xs text-gray-500 uppercase">Email</Label>
              <div class="font-medium mt-1">{{ user.email }}</div>
            </div>
            <div>
              <Label class="text-xs text-gray-500 uppercase">Name</Label>
              <div class="font-medium mt-1">{{ user.first_name }} {{ user.last_name }}</div>
            </div>
          </div>

          <div class="border-t pt-4"></div>

          <div class="space-y-4">
            <div class="flex items-center space-x-2">
              <input
                type="checkbox"
                id="isActive"
                v-model="formData.is_active"
                :disabled="isSaving"
                class="h-4 w-4 rounded border-gray-300 text-teal-600 focus:ring-teal-500"
              />
              <Label for="isActive" class="font-medium">Account is Active</Label>
            </div>
            <p class="text-sm text-gray-500 pl-6">Uncheck this to disable the user's account and prevent them from logging in.</p>
          </div>

          <div class="space-y-2">
            <Label for="groups">User Groups (Roles)</Label>
            <div class="flex flex-wrap gap-2 mt-2">
              <label v-for="role in availableRoles" :key="role" class="flex items-center space-x-2 border rounded-md p-3 cursor-pointer hover:bg-gray-50" :class="{'bg-teal-50 border-teal-200': formData.groups.includes(role)}">
                <input
                  type="checkbox"
                  :value="role"
                  v-model="formData.groups"
                  :disabled="isSaving"
                  class="h-4 w-4 rounded border-gray-300 text-teal-600 focus:ring-teal-500"
                />
                <span class="text-sm font-medium">{{ role }}</span>
              </label>
            </div>
            <p class="text-sm text-gray-500 mt-1">Select all roles that apply to this user.</p>
          </div>

          <Button type="submit" class="bg-teal-600 hover:bg-teal-700" :disabled="isSaving">
            {{ isSaving ? 'Saving...' : 'Save Changes' }}
          </Button>

          <p v-if="successMessage" class="text-green-600 text-sm mt-2">{{ successMessage }}</p>
          <div v-if="saveError" class="text-red-500 text-sm mt-2 whitespace-pre-wrap">{{ saveError }}</div>
        </form>
      </CardContent>
    </Card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { userService } from "@/services/userService";

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-vue-next";

const route = useRoute();
const router = useRouter();

const userId = route.params.id;

const user = ref(null);
const isLoading = ref(true);
const fetchError = ref("");

const isSaving = ref(false);
const successMessage = ref("");
const saveError = ref("");

const availableRoles = ["Patient", "Doctor", "Receptionist", "Admin"];

const formData = reactive({
  is_active: false,
  groups: [],
});

const loadUser = async () => {
  isLoading.value = true;
  fetchError.value = "";
  try {
    const data = await userService.getUser(userId);
    user.value = data;
    formData.is_active = data.is_active !== false; // Default to true if undefined
    formData.groups = Array.isArray(data.groups) ? [...data.groups] : [];
  } catch (error) {
    fetchError.value = "Failed to load user details.";
    console.error(error);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  loadUser();
});

const handleUpdate = async () => {
  isSaving.value = true;
  successMessage.value = "";
  saveError.value = "";

  try {
    await userService.updateUser(userId, {
      is_active: formData.is_active,
      groups: formData.groups,
    });
    successMessage.value = "User updated successfully.";
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
        saveError.value = errors.join('\n');
    } else {
        saveError.value = "Failed to update user.";
    }
  } finally {
    isSaving.value = false;
  }
};
</script>
