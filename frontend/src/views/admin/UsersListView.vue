<template>
  <div class="flex-1 space-y-4 p-4 md:p-8 pt-6">
    <div class="flex items-center justify-between space-y-2">
      <h2 class="text-3xl font-bold tracking-tight">Users Management</h2>
    </div>

    <Card>
      <CardHeader>
        <CardTitle>All Users</CardTitle>
        <CardDescription>
          Manage system users and their roles.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div v-if="isLoading" class="text-gray-500 py-4">
          Loading users...
        </div>
        <div v-else-if="error" class="text-red-500 py-4">
          {{ error }}
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm text-left text-gray-500">
            <thead class="text-xs text-gray-700 uppercase bg-gray-50">
              <tr>
                <th scope="col" class="px-6 py-3">ID</th>
                <th scope="col" class="px-6 py-3">Username</th>
                <th scope="col" class="px-6 py-3">Name</th>
                <th scope="col" class="px-6 py-3">Email</th>
                <th scope="col" class="px-6 py-3">Primary Role</th>
                <th scope="col" class="px-6 py-3">Status</th>
                <th scope="col" class="px-6 py-3">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id" class="bg-white border-b hover:bg-gray-50">
                <td class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap">
                  {{ user.id }}
                </td>
                <td class="px-6 py-4">
                  {{ user.username }}
                </td>
                <td class="px-6 py-4">
                  {{ user.first_name }} {{ user.last_name }}
                </td>
                <td class="px-6 py-4">
                  {{ user.email }}
                </td>
                <td class="px-6 py-4">
                  {{ user.primary_role }}
                </td>
                <td class="px-6 py-4">
                  <span
                    class="px-2 py-1 text-xs rounded-full font-medium"
                    :class="user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                  >
                    {{ user.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <Button variant="outline" size="sm" @click="router.push(`/admin/users/${user.id}`)">
                    Edit
                  </Button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { userService } from "@/services/userService";

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const router = useRouter();

const users = ref([]);
const isLoading = ref(true);
const error = ref("");

const fetchUsers = async () => {
  isLoading.value = true;
  error.value = "";
  try {
    const data = await userService.getUsers();
    // Assuming data is an array or { results: [...] } based on DRF pagination
    users.value = data.results || data;
  } catch (err) {
    error.value = "Failed to load users.";
    console.error(err);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchUsers();
});
</script>
